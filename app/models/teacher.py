class Teacher:
    def __init__(self, teacher_id, full_name, max_periods_per_day, qualified_subjects, unavailable_slots):
        self.teacher_id = teacher_id
        self.full_name = full_name
        self.max_periods_per_day = max_periods_per_day
        self.qualified_subjects = qualified_subjects
        self.unavailable_slots = unavailable_slots

    def is_available(self, day, period):
        return True if (day, period) not in self.unavailable_slots else False

    def can_teach(self, subject_id):
        return True if subject_id in self.qualified_subjects else False
