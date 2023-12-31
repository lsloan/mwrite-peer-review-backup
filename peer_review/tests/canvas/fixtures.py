from datetime import timedelta

from django.conf import settings


def test_course_api(course):
    return {
        'id': course.id,
        'name': course.name,
        # 'account_id': X,
        # 'uuid': UUID_GOES_HERE,
        'start_at': '2016-12-22T18:53:00Z',
        'grading_standard_id': None,
        'is_public': False,
        'course_code': 'MPR1',
        'default_view': 'feed',
        # 'root_account_id': X,
        # 'enrollment_term_id': X,
        'end_at': None,
        'public_syllabus': False,
        'public_syllabus_to_auth': False,
        'storage_quota_mb': 500,
        'is_public_to_auth_users': False,
        'hide_final_grades': False,
        'apply_assignment_group_weights': False,
        # 'calendar': {
        #     'ics': LINK_GOES_HERE
        # },
        'time_zone': 'America/New_York',
        'blueprint': False,
        'sis_course_id': None,
        'sis_import_id': None,
        'integration_id': None,
        # 'enrollments': [
        #     {'type': 'teacher', 'role': 'TeacherEnrollment', 'role_id': X, 'user_id': X, 'enrollment_state': 'active'}
        # ],
        'workflow_state': 'available',
        'restrict_enrollments_to_course_dates': False
    }


def test_assignment_api(now, course, assignment):
    timestamp = now.isoformat() + 'Z'
    result = {
        'id': assignment.id,
        'description': None,
        'due_at': assignment.due_date_utc.isoformat() + 'Z',
        'unlock_at': None,
        'lock_at': None,
        'points_possible': None,
        'grading_type': 'points',
        # 'assignment_group_id': X,
        'grading_standard_id': None,
        'created_at': timestamp,
        'updated_at': timestamp,
        'peer_reviews': False,
        'automatic_peer_reviews': False,
        # 'position': X,
        'grade_group_students_individually': False,
        'anonymous_peer_reviews': False,
        'group_category_id': None,
        'post_to_sis': False,
        'moderated_grading': False,
        'omit_from_final_grade': False,
        'intra_group_peer_reviews': False,
        'anonymous_instructor_annotations': False,
        'anonymous_grading': False,
        'graders_anonymous_to_graders': False,
        'grader_count': None,
        'grader_comments_visible_to_graders': True,
        'final_grader_id': None,
        'grader_names_visible_to_final_grader': True,
        # 'secure_params': SECURE_PARAMS_HERE,
        'course_id': course.id,
        'name': assignment.title,
        'has_submitted_submissions': True,
        'due_date_required': False,
        'max_name_length': 255,
        'in_closed_grading_period': False,
        'overrides': [],
        'is_quiz_assignment': False,
        'can_duplicate': True,
        'original_assignment_id': None,
        'original_assignment_name': None,
        'workflow_state': 'published',
        'muted': False,
        # 'html_url': URL_GOES_HERE,
        'has_overrides': False,
        # 'needs_grading_count': X,
        'integration_id': None,
        'integration_data': {},
        'published': True,
        'unpublishable': False,
        'only_visible_to_overrides': False,
        'locked_for_user': False,
        'submissions_download_url': 'https://umich-dev.instructure.com/courses/%d/assignments/%d/submissions?zip=1'
                                    % (course.id, assignment.id),
        'anonymize_students': False
    }

    if assignment.is_peer_review_assignment:
        # assignment['url']: LAUNCH_URL_GOES_HERE,
        result['submission_types'] = ['external_tool']
        result['external_tool_tag_attributes'] = {
            'url': 'https://%s/launch' % settings.APP_HOST,
            'new_tab': True,
            # 'resource_link_id': X
        }
    else:
        result['submission_types'] = ['online_upload']
        result['allowed_extensions'] = ['txt']

    return result


def test_sections_api(sections):
    return [
        {
            'id': s.id,
            'course_id': s.course_id,
            'name': s.name,
            'start_at': None,
            'end_at': None,
            'restrict_enrollments_to_section_dates': None,
            'nonxlist_course_id': None,
            'sis_section_id': None,
            'sis_course_id': None,
            'integration_id': None,
            'sis_import_id': None
        }
        for s in sections
    ]


def test_student_api(now, course, sections, index):
    timestamp = now.isoformat() + 'Z'
    return {
        'id': index,
        'name': 'Test%d Student' % index,
        'sortable_name': 'Student, Test%d' % index,
        'short_name': 'Test%d' % index,
        'sis_user_id': None,
        'integration_id': None,
        'sis_import_id': None,
        'login_id': 'student%d' % index,
        'enrollments': [
            {
                'id': section.id,  # FIXME not accurate, but good enough for now
                'user_id': index,
                'course_id': course.id,
                'type': 'StudentEnrollment',
                'created_at': timestamp,
                'updated_at': timestamp,
                'associated_user_id': None,
                'start_at': None,
                'end_at': None,
                'course_section_id': section.id,
                # 'root_account_id': X,
                'limit_privileges_to_course_section': False,
                'enrollment_state': 'active',
                'role': 'StudentEnrollment',
                # 'role_id': Y,
                'last_activity_at': timestamp,
                'last_attended_at': None,
                'total_activity_time': 4000,  # FIXME should this be tied to last_activity_at?
                'sis_import_id': None,
                'grades': {
                    'html_url': 'https://umich-dev.instructure.com/courses/%d/grades/%d' %
                                (course.id, index),
                    'current_score': None,
                    'current_grade': None,
                    'final_score': None,
                    'final_grade': None,
                    'unposted_current_score': None,
                    'unposted_current_grade': None,
                    'unposted_final_score': None,
                    'unposted_final_grade': None
                },
                'sis_account_id': None,
                'sis_course_id': None,
                'course_integration_id': None,
                'sis_section_id': None,
                'section_integration_id': None,
                'sis_user_id': None,
                'html_url': 'https://umich-dev.instructure.com/courses/%d/users/%d' %
                            (course.id, index)
            }
            for section in sections
        ],
        'analytics_url': '/courses/%d/analytics/users/%d' % (course.id, index)
    }


def test_submission_api(now, course, assignment, student, attachment, index):
    submission_time = now + timedelta(seconds=30)
    submission_timestamp = submission_time.isoformat() + 'Z'
    filename = 'Test_Prompt_for_Student%d.txt' % student['id']
    return {
        'id': index,
        'body': None,
        'url': None,
        'grade': None,
        'score': None,
        'submitted_at': submission_timestamp,
        'assignment_id': assignment.id,
        'user_id': student['id'],
        'submission_type': 'online_upload',
        'workflow_state': 'submitted',
        'grade_matches_current_submission': True,
        'graded_at': None,
        'grader_id': None,
        'attempt': 1,
        'cached_due_date': assignment.due_date_utc.isoformat() + 'Z',
        'excused': None,
        'late_policy_status': None,
        'points_deducted': None,
        'grading_period_id': None,
        'late': False,
        'missing': False,
        'seconds_late': 0,
        'entered_grade': None,
        'entered_score': None,
        'preview_url': 'https://umich-dev.instructure.com/courses/%d/assignments/%d/submissions/%d?preview=1&version=1'
                       % (course.id, assignment.id, student['id']),
        'attachments': [
            {
                'id': index,  # FIXME not accurate, but good enough for now
                # 'uuid': UUID_GOES_HERE,
                # 'folder_id': X,
                'display_name': filename,
                'filename': filename,
                'content-type': 'text/plain',
                'url': 'https://umich-dev.instructure.com/files/%d/download?download_frd=1&verifier=PLACEHOLDER' % index,
                'size': len(attachment),
                'created_at': submission_timestamp,
                'updated_at': submission_timestamp,
                'unlock_at': None,
                'locked': False,
                'hidden': False,
                'lock_at': None,
                'hidden_for_user': False,
                'thumbnail_url': None,
                'modified_at': submission_timestamp,
                'mime_class': 'text',
                'media_entry_id': None,
                'locked_for_user': False,
                # 'preview_url': PREVIEW_URL
            }
        ]
    }
