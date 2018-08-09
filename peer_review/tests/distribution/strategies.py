from hypothesis.strategies import composite, sets, integers

from peer_review.models import CanvasStudent, CanvasSubmission


@composite
def students(draw, min_size=1, average_size=10, max_size=25):
    ids = draw(sets(elements=integers(), min_size=min_size, average_size=average_size, max_size=max_size))
    return {CanvasStudent(id=i) for i in ids}


@composite
def students_and_submissions(draw):
    _students = draw(students(min_size=50, average_size=1000, max_size=5000))
    ids = (s.id for s in _students)
    submissions = {CanvasSubmission(id=i, author_id=i) for i in ids}
    return _students, submissions
