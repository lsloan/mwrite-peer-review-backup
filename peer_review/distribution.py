import logging
from collections import OrderedDict

from toolz.itertoolz import unique

from django.db import transaction

from peer_review.etl import persist_students, persist_sections, persist_submissions
from peer_review.models import CanvasAssignment

log = logging.getLogger(__name__)


def make_distribution(students, submissions, n=3):
    submissions_by_id = {submission.id: submission for submission in submissions}

    submissions_to_review_by_student = {student.id: set() for student in students}
    review_count_by_submission = {submission.id: 0 for submission in submissions}

    for student in students:
        while len(submissions_to_review_by_student[student.id]) < n:
            review_count_by_submission = OrderedDict(sorted(review_count_by_submission.items(), key=lambda t: t[1]))
            for submission_id, _ in review_count_by_submission.items():
                if submissions_by_id[submission_id].author_id != student.id \
                        and submission_id not in submissions_to_review_by_student[student.id]:
                    review_count_by_submission[submission_id] += 1
                    submissions_to_review_by_student[student.id].add(submission_id)
                    break

    return submissions_to_review_by_student, review_count_by_submission


def distribute_reviews(prompt_id):
    log.info('would have distributed reviews for %d' % prompt_id)


# TODO think about how multiple instances may react to each other trying to do this -- wrap in transactions, locks, etc.
def review_distribution_task(utc_timestamp):
    log.info('Starting review distribution at %s' % utc_timestamp.isoformat())

    try:
        # TODO remove assignments with no due date
        prompts_for_distribution = CanvasAssignment.objects.filter(
            rubric_for_prompt__peer_review_distribution=None,
            rubric_for_prompt__reviewed_assignment__due_date_utc__lt=utc_timestamp
        )

        if not prompts_for_distribution:
            log.info('No prompts ready for review distribution.')
        else:
            courses = unique(map(lambda a: a.course, prompts_for_distribution))
            for course in courses:
                log.info('Persisting sections for course %d' % course.id)
                persist_sections(course)

                log.info('Persisting students for course %d' % course.id)
                persist_students(course)

            for prompt in prompts_for_distribution:
                log.info('Distributing reviews for prompt %d...' % prompt.id)

                try:
                    log.debug('Fetching and persisting submissions for prompt %d...' % prompt.id)
                    persist_submissions(prompt)
                    log.debug('Finished persisting submissions for prompt %d' % prompt.id)

                    log.debug('Distributing for prompt %d for review...' % prompt.id)
                    with transaction.atomic():
                        distribute_reviews(prompt.id)
                        distribution = prompt.rubric_for_prompt.peer_review_distribution
                        distribution.is_distribution_complete = True
                        distribution.distributed_at_utc = utc_timestamp  # TODO correct?
                        distribution.save()
                    log.debug('Finished review distribution for prompt %d' % prompt.id)

                except Exception as ex:
                    # TODO expose failed prompt distribution to health check
                    log.error('Skipping review distribution for prompt %d due to error' % prompt.id, ex)

                log.info('Finished distributing reviews for prompt %d' % prompt.id)
    except Exception as ex:
        # TODO expose failed "all" distribution to health check
        log.error('Review distribution failed due to uncaught exception', ex)
        raise ex

    log.info('Finished review distribution that began at %s' % utc_timestamp.isoformat())
