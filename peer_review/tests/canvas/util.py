import json
from io import StringIO
from datetime import datetime, timedelta

from django.db import transaction

import peer_review.canvas as canvas
from peer_review.models import Rubric, CanvasSection, Criterion
from peer_review.etl import persist_course, persist_assignments, persist_sections


def make_test_user_details(index, email_base, password_base):
    email = email_base % index
    return {
        'user': {
            'name': 'MWrite Test User %d' % index,
            'short_name': 'MWrite %d' % index,
            'sortable_name': '%d, MWrite Test User' % index,
            'skip_registration': True
        },
        'pseudonym': {
            'unique_id': email,
            'password': password_base % index,
            'send_confirmation': False
        },
        'communication_channel': {
            'type': 'email',
            'address': email
        }
    }


def create_test_user(account_id, index, email_base, password_base):
    test_user_details = make_test_user_details(index, email_base, password_base)
    return canvas.create('users', account_id, data=test_user_details)


def enroll_test_user_in_section(course_id, user_id, section_id):
    enrollment_details = {
        'enrollment': {
            'user_id': user_id,
            'type': 'StudentEnrollment',
            'enrollment_state': 'active',
            'course_section_id': section_id
        }
    }
    return canvas.create('enrollments', course_id, data=enrollment_details)


def delete_all_assignments(course_id):
    assignments = canvas.retrieve('assignments', course_id)
    for assignment in assignments:
        canvas.delete('assignment', course_id, assignment['id'])


def create_test_assignments(course_id, num_pairs=1):
    now = datetime.utcnow()

    prompt_template = {
        'submission_types': ['online_upload'],
        'allowed_extensions': ['txt'],
        'published': True,
        'due_at': (now + timedelta(minutes=1)).isoformat() + 'Z'
    }
    peer_review_template = {
        'submission_types': ['external_tool'],
        'published': True,
        'due_at': (now + timedelta(minutes=30)).isoformat() + 'Z',
        'external_tool_tag_attributes': {
            'new_tab': True,
            'url': 'https://peer-review-dev.mwrite.openshift.dsc.umich.edu/launch'
        }
    }

    pairings = []
    for i in range(1, num_pairs+1):
        prompt_template['name'] = 'Test Prompt %s' % i
        created_assignment = canvas.create('assignments', course_id, data={'assignment': prompt_template})

        peer_review_template['name'] = 'Test Peer Review %s' % i
        created_peer_review = canvas.create('assignments', course_id, data={'assignment': peer_review_template})

        pairings.append((created_assignment, created_peer_review))

    return pairings


def create_test_rubrics(course_id, pairings, section_ids, num_criteria=3):
    persist_assignments(course_id)
    rubrics = []
    for i, pairing in enumerate(pairings, 1):
        prompt, peer_review = pairing
        with transaction.atomic():
            rubric, _ = Rubric.objects.get_or_create(defaults={
                'description': 'This is test rubric #%d.' % i,
                'reviewed_assignment_id': prompt['id'],
                'passback_assignment_id': peer_review['id'],
                'peer_review_open_date': prompt['due_at'],
                'distribute_peer_reviews_for_sections': True
            })
            for section_id in section_ids:
                section = CanvasSection.objects.get(id=section_id)
                rubric.sections.add(section)
            criteria = [Criterion(description='This is test criterion %d for test rubric %d.' % (j, i),
                                  rubric=rubric)
                        for j in range(1, num_criteria+1)]
            Criterion.objects.bulk_create(criteria)
            rubrics.append(rubric)
    return rubrics


def submit_for_assignments(course_id, assignments, users):
    for assignment in assignments:
        for user in users:
            base = '%s for %s' % (assignment['name'], user['name'])
            filename = base.replace(' ', '_') + '.txt'
            contents = StringIO(base)
            canvas.submit_file(user['token'], course_id, assignment['id'], filename, contents)


def canvas_integration_course(course_id, section_ids):
    delete_all_assignments(course_id)
    pairings = create_test_assignments(course_id, num_pairs=3)
    persist_course(course_id)
    persist_sections(course_id)
    persist_assignments(course_id)
    rubrics = create_test_rubrics(course_id, pairings, section_ids)
    with open('config/server/local/test_users.json') as test_users_file:
        users = json.loads(test_users_file.read())

    prompts = list(map(lambda p: canvas.retrieve('assignment', course_id, p[0]['id']), pairings))
    submit_for_assignments(course_id, prompts, users)
    return rubrics
