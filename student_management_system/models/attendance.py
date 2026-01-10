from datetime import datetime

class Attendance:
    """
    Represents a single attendance record.
    """
    def __init__(self, student_id: str, course_id: str, date: str, status: str, recorded_by: str):
        self.student_id = student_id
        self.course_id = course_id
        self.date = date
        self.status = status  # P/A/L/E
        self.recorded_by = recorded_by

    def mark(self, new_status: str) -> bool:
        """
        Update the attendance status.
        Args:
            new_status (str): The new status ('P', 'A', 'L', 'E').
        Returns:
            bool: True if valid status update, False otherwise.
        """
        valid_statuses = ['P', 'A', 'L', 'E']
        if new_status in valid_statuses:
            self.status = new_status
            return True
        return False

    def to_dict(self) -> dict:
        """
        Convert to dictionary for persistence.
        Returns:
            dict: The dictionary representation.
        """
        return {
            'student_id': self.student_id,
            'course_id': self.course_id,
            'date': self.date,
            'status': self.status,
            'recorded_by': self.recorded_by
        }
