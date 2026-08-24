class Lesson:
    def __init__(self, sessions_needed, subject_id, student_group_id):
        self.sessions_needed = sessions_needed
        self.subject_id = subject_id
        self.student_group_id = student_group_id
        self.domain = []
        self.assignment = None

    def assign(self, day, period, teacher_id, room_id):
        self.assignment = (day, period, teacher_id, room_id)

    def is_assigned(self):
        return False if self.assignment is None else True

    def unassign(self):
        self.assignment = None  