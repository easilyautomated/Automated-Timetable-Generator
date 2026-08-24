class Room:
    def __init__(self, room_id, name, capacity, room_type, unavailable_ranges):
        self.room_id = room_id
        self.name = name
        self.capacity = capacity
        self.room_type = room_type
        self.unavailable_ranges = unavailable_ranges

    def is_suitable_for(self, subject_required_type):
        return True if self.room_type == subject_required_type else False

    def is_available_on(self, date_str):
        for start_date, end_date in self.unavailable_ranges:
            if start_date <= date_str <= end_date:
                return False
        return True
    

        