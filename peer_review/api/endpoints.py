import os.path
import logging
import mimetypes
from itertools import chain

from django.db import transaction
from django.conf import settings
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from rolepermissions.roles import get_user_roles
from rolepermissions.checkers import has_role

import peer_review.etl as etl
from peer_review.api.util import merge_validations, validate_rubric, raise_if_not_current_user, \
    raise_if_peer_review_not_given_to_student
from peer_review.util import to_camel_case, keymap_all
from peer_review.exceptions import ReviewsInProgressException, APIException
from peer_review.decorators import authorized_endpoint, authorized_json_endpoint, \
    authenticated_json_endpoint, json_body
from peer_review.models import CanvasCourse, CanvasStudent, CanvasAssignment, CanvasSubmission, \
    PeerReview, Rubric, Criterion, PeerReviewEvaluation, PeerReviewDistribution
from peer_review.queries import InstructorDashboardStatus, StudentDashboardStatus, ReviewStatus, \
    RubricForm


LOGGER = logging.getLogger(__name__)


@authenticated_json_endpoint
def logged_in_user_details(request):
    roles = [role.get_name() for role in get_user_roles(request.user)]
    course_id = request.session['lti_launch_params']['custom_canvas_course_id']
    course_name = request.session['lti_launch_params']['context_title']
    user_id = request.session['lti_launch_params']['custom_canvas_user_id']
    return {
        'username': request.user.username,
        'user_id': int(user_id),
        'course_id': int(course_id),
        'course_name': course_name,
        'roles': roles
    }


# TODO refactor this based on what we're actually using on the new students list implementation
@authorized_json_endpoint(roles=['instructor'])
def all_students(request, course_id):
    etl.persist_sections(course_id)
    etl.persist_students(course_id)

    course_model = CanvasCourse.objects.get(id=course_id)
    course = {'id': course_model.id, 'name': course_model.name}

    students = []
    for student in CanvasStudent.objects.filter(course_id=course_id):
        sections = []
        for section in student.sections.filter(course_id=course_id):
            sections.append({
                'id': section.id,
                'name': section.name,
                'course': course
            })
        students.append({
            'id': student.id,
            'sortable_name': student.sortable_name,
            'full_name': student.full_name,
            'username': student.username,
            'sections': sections,
            'course': course
        })

    return students


@authorized_json_endpoint(roles=['instructor'])
def all_peer_review_assignment_details(request, course_id):
    etl.persist_course(course_id)
    assignments = etl.persist_assignments(course_id)
    fetched_assignment_ids = tuple(map(lambda a: a.id, assignments))

    details = InstructorDashboardStatus.get(course_id, fetched_assignment_ids)

    validations = {a.id: a.validation for a in assignments}
    details_with_validations = merge_validations(details, validations)

    return keymap_all(to_camel_case, details_with_validations)


@authorized_json_endpoint(roles=['student'])
def assigned_work(request, course_id, student_id):
    raise_if_not_current_user(request, student_id)
    return StudentDashboardStatus.assigned_work(course_id, student_id)


@authorized_json_endpoint(roles=['student'])
def completed_work(request, course_id, student_id):
    raise_if_not_current_user(request, student_id)
    return StudentDashboardStatus.completed_work(course_id, student_id)


def _denormalize_reviews(reviews):

    peer_review_ids = sorted(r.id for r in reviews)
    student_numbers = {pr_id: i for i, pr_id in enumerate(peer_review_ids)}

    return {
        'title': reviews[0].submission.assignment.title,
        'entries': [
            {
                'id': review.id,
                'student_id': student_numbers[review.id],
                'entries': [{'id': comment.id,
                             'heading': comment.criterion.description,
                             'content': comment.comment}
                            for comment in review.comments.all().order_by('criterion_id')]
            }
            for review in reviews
            if review.comments.exists()
        ]
    }


@authorized_json_endpoint(roles=['student'])
def reviews_given(request, course_id, student_id, rubric_id):
    raise_if_not_current_user(request, student_id)

    reviews = PeerReview.objects.filter(
        student_id=student_id,
        submission__assignment__course_id=course_id,
        submission__assignment__rubric_for_prompt=rubric_id
    )\
        .prefetch_related('comments')\
        .order_by('id')

    return _denormalize_reviews(reviews)


@authorized_json_endpoint(roles=['student'])
def reviews_received(request, course_id, student_id, rubric_id):
    raise_if_not_current_user(request, student_id)

    reviews = PeerReview.objects.filter(
        submission__assignment__course_id=course_id,
        submission__assignment__rubric_for_prompt__id=rubric_id,
        submission__author_id=student_id
    )\
        .order_by('id')

    peer_review_ids = [r.id for r in reviews]
    student_numbers = {pr_id: i for i, pr_id in enumerate(peer_review_ids)}

    comments = list(chain(*map(lambda r: r.comments.all(), reviews)))
    criterion_ids = set(c.criterion_id for c in comments)
    criterion_numbers = {cr_id: i for i, cr_id in enumerate(criterion_ids)}

    entries = []
    for comment in comments:
        try:
            comment.peer_review.evaluation
            evaluation_submitted = True
        except ObjectDoesNotExist:
            evaluation_submitted = False

        entries.append({
            'peer_review_id': comment.peer_review_id,
            'evaluation_submitted': evaluation_submitted,
            'reviewer_id': student_numbers[comment.peer_review_id],
            'criterion_id': criterion_numbers[comment.criterion_id],
            'criterion': comment.criterion.description,
            'comment_id': comment.id,
            'comment': comment.comment
        })

    prompt_title = Rubric.objects.get(id=rubric_id).reviewed_assignment.title

    return {
        'title': prompt_title,
        'entries': entries
    }


@require_POST
@json_body
@authorized_json_endpoint(roles=['student'])
def submit_peer_review_evaluation(request, body, course_id, student_id, peer_review_id):
    raise_if_not_current_user(request, student_id)
    raise_if_peer_review_not_for_student(request, student_id, peer_review_id)

    PeerReviewEvaluation.objects.create(
        peer_review_id=peer_review_id,
        usefulness=body['usefulness'],
        comment=body['comment']
    )

    return True


@authorized_json_endpoint(roles=['instructor'])
def review_status(request, course_id, rubric_id):
    return ReviewStatus.status_for_rubric(course_id, rubric_id)


@authorized_json_endpoint(roles=['instructor'])
def rubric_info_for_peer_review_assignment(request, course_id, passback_assignment_id):
    try:
        passback_assignment = CanvasAssignment.objects.get(id=passback_assignment_id)
    except CanvasAssignment.DoesNotExist:
        raise Http404

    # TODO might need to persist course here if assignment-level launches are added for instructors
    course = CanvasCourse.objects.get(id=course_id)
    fetched_assignments = etl.persist_assignments(course_id)

    return RubricForm.rubric_info(course, passback_assignment, fetched_assignments)


@require_POST
@json_body
@authorized_json_endpoint(roles=['instructor'], default_status_code=201)
def create_or_update_rubric(request, params, course_id):
    try:
        with transaction.atomic():
            # my kingdom for destructuring assignment in Python :/
            objects = validate_rubric(int(course_id), params)
            prompt_assignment = objects['prompt_assignment']
            passback_assignment = objects['peer_review_assignment']
            revision_assignment = objects['revision_assignment']
            rubric_description = objects['rubric_description']
            criteria = objects['criteria']
            peer_review_open_date = objects['peer_review_open_date']
            pr_open_date_is_prompt_due_date = objects['peer_review_open_date_is_prompt_due_date']

            rubric, created = Rubric.objects.update_or_create(
                reviewed_assignment=prompt_assignment,
                defaults={
                    'description': rubric_description,
                    'reviewed_assignment': prompt_assignment,
                    'passback_assignment': passback_assignment,
                    'revision_assignment': revision_assignment,
                    'peer_review_open_date': peer_review_open_date,
                    'peer_review_open_date_is_prompt_due_date': pr_open_date_is_prompt_due_date,
                    'distribute_peer_reviews_for_sections': False
                }
            )

            if not created:
                try:
                    distribution = PeerReviewDistribution.objects.get(rubric_id=rubric.id)
                    if distribution.is_distribution_complete:
                        raise ReviewsInProgressException
                except PeerReviewDistribution.DoesNotExist:
                    pass
                Criterion.objects.filter(rubric_id=rubric.id).delete()

            rubric.save()
            for criterion in criteria:
                criterion.rubric_id = rubric.id
                criterion.save()

        return params
    except ReviewsInProgressException:
        error = 'Rubric is read-only because reviews are in progress.'
        raise APIException(data={'error': error}, status_code=403)


@authorized_endpoint(roles=['instructor', 'student'])
def submission_for_review(request, course_id, review_id):
    try:
        peer_review = PeerReview.objects.get(id=review_id)
    except PeerReview.DoesNotExist:
        raise Http404

    logged_in_user_id = int(request.session['lti_launch_params']['custom_canvas_user_id'])
    if has_role(request.user, 'student') and logged_in_user_id != peer_review.student_id:
        msg = 'User %s tried to download submission for a peer review (ID %s) they were not assigned'
        LOGGER.warning(msg, logged_in_user_id, review_id)
        raise PermissionDenied

    submission = peer_review.submission
    submission_path = os.path.join(settings.MEDIA_ROOT, 'submissions', submission.filename)

    with open(submission_path, 'rb') as submission_file:
        submission_bytes = submission_file.read()

    content_type = mimetypes.guess_type(submission.filename)[0] or 'application/octet-stream'
    response = HttpResponse(submission_bytes, content_type)
    response['Content-Disposition'] = 'attachment; filename="%s"' % submission.filename

    return response
