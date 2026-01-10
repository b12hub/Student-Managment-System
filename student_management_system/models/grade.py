class Grade:
    """
    Represents a grade record.
    """
    def __init__(self, student_id: str, course_id: str, score: float, max_score: float, weight: float):
        self.student_id = student_id
        self.course_id = course_id
        self.score = score
        self.max_score = max_score
        self.weight = weight

    def calculate_percentage(self) -> float:
        """
        Calculate the percentage score.
        Returns:
            float: The percentage (0-100).
        """
        if self.max_score == 0:
            return 0.0
        return (self.score / self.max_score) * 100

    def get_letter_grade(self) -> str:
        """
        Get the letter grade based on percentage.
        Returns:
            str: The letter grade (A, B, C, D, F).
        """
        percentage = self.calculate_percentage()
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'

    def to_dict(self) -> dict:
        """
        Convert to dictionary for persistence.
        Returns:
            dict: The dictionary representation.
        """
        return {
            'student_id': self.student_id,
            'course_id': self.course_id,
            'score': self.score,
            'max_score': self.max_score,
            'weight': self.weight
        }
