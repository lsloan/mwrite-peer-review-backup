import logging
from toolz.functoolz import thread_last
from toolz.itertoolz import unique
from django.conf import settings
from django.utils.dateparse import parse_datetime
from peer_review.util import utc_to_timezone
from peer_review.canvas import retrieve
from peer_review.models import CanvasAssignment

log = logging.getLogger(__name__)


class AssignmentValidation:
    def __init__(self, **kwargs):
        self.submission_upload_type = kwargs.get('submission_upload_type')
        self.allowed_submission_file_extensions = kwargs.get('allowed_extensions')
        local_due_date_dt = utc_to_timezone(kwargs.get('due_date_utc'), settings.TIME_ZONE)
        self.local_due_date = local_due_date_dt.strftime(settings.TIME_OUTPUT_FORMAT)
        self.number_of_due_dates = kwargs.get('number_of_due_dates')
        self.section_name = kwargs.get('section_name')
        self.number_of_sections = kwargs.get('number_of_sections')

    @staticmethod
    def json_default(validation):
        return validation.__dict__


def _due_dates_from_overrides(assignment, overrides):
    if 'due_at' in assignment:
        due_date_utc = parse_datetime(assignment['due_at'])
    elif overrides and len(overrides) == 1:
        due_date_utc = parse_datetime(overrides[0])
    else:
        due_date_utc = None
        number_of_overrides = len(overrides) if overrides else 0
        log.warning('Assignment %d has no due date and %d overrides!' % (assignment['id'], number_of_overrides))
    if due_date_utc:
        number_of_due_dates = 1
    elif overrides:
        number_of_due_dates = thread_last(overrides, (map, lambda o: o['due_at']), unique, list, len)
    else:
        number_of_due_dates = 0
    return due_date_utc, number_of_due_dates


def _is_peer_review_assignment(assignment):
    return 'external_tool_tag_attributes' in assignment and \
           'url' in assignment['external_tool_tag_attributes'] and \
           settings.APP_HOST in assignment['external_tool_tag_attributes']['url']


def _convert_assignment(assignment):
    course_id = assignment['course_id']
    assignment_id = assignment['id']
    overrides = retrieve('assignment-overrides', course_id, assignment_id) if assignment['has_overrides'] else None
    due_date_utc, number_of_due_dates = _due_dates_from_overrides(assignment, overrides)
    sections = list(map(lambda o: o['course_section_id'], overrides)) if overrides else None
    section_name = retrieve('section', course_id, sections[0])['name'] if sections and len(sections) == 1 else None
    validation = AssignmentValidation(submission_upload_type=assignment.get('submission_types'),
                                      allowed_extensions=assignment.get('allowed_extensions'),
                                      due_date_utc=due_date_utc,
                                      number_of_due_dates=number_of_due_dates,
                                      section_name=section_name,
                                      number_of_sections=len(sections) if sections else 0)
    return CanvasAssignment(id=assignment_id,
                            course_id=course_id,
                            title=assignment['name'],
                            due_date_utc=due_date_utc,
                            is_peer_review_assignment=_is_peer_review_assignment(assignment),
                            validation=validation)


def persist_assignments(course_id):
    canvas_assignments = retrieve('assignments', course_id)
    assignments = [_convert_assignment(canvas_assignment) for canvas_assignment in canvas_assignments]
    for assignment in assignments:
        assignment.save()
    return assignments
