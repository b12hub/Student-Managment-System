# NOTE: IDs and data operations are placeholders.
# Persistence and ID generation are handled by StorageManager.

from abc import ABC, abstractmethod

class User(ABC):
    """
    Abstract Base Class representing a generic user in the system.
    """
    def __init__(self, username: str, password_hash: str, role: str, is_active: bool = True):
        """
        Initialize the User.
        
        Args:
            username (str): The username of the user.
            password_hash (str): The hashed password.
            role (str): The role of the user (e.g., 'Admin', 'Teacher', 'Student').
            is_active (bool): Whether the user account is active. Defaults to True.
        """
        self._user_id = "U-000"  # Placeholder ID
        self._username = username
        self._password_hash = password_hash
        self._role = role
        self._is_active = is_active

    def authenticate(self, input_password: str) -> bool:
        """
        Authenticate the user by comparing hashes.
        
        Args:
            input_password (str): The password hash to check against.
            
        Returns:
            bool: True if authentication succeeds, False otherwise.
        """
        # Actual hashing is handled elsewhere; compare hashes only
        return self._is_active and self._password_hash == input_password

    @abstractmethod
    def view_profile(self) -> dict:
        """
        Abstract method to view the user's profile information.
        
        Returns:
            dict: A dictionary containing profile details.
        """
        pass

    def change_password(self, new_password_hash: str) -> bool:
        """
        Change the user's password.
        
        Args:
            new_password_hash (str): The new hashed password.
            
        Returns:
            bool: True if successful.
        """
        self._password_hash = new_password_hash
        return True

    def __str__(self) -> str:
        """String representation of the User."""
        return f"[{self._role}] {self._username} (ID: {self._user_id})"


class Admin(User):
    """
    Admin subclass representing an administrator.
    """
    def __init__(self, username: str, password_hash: str, is_active: bool = True):
        super().__init__(username, password_hash, "Admin", is_active)
        self._admin_id = "A-000"  # Placeholder ID
        self._permissions = []    # List of permissions
        self._groups = []         # Internal list of groups
        self._users = []          # Internal list of users

    def add_user(self, user_data: dict) -> bool:
        """
        Add a new user to the system.
        
        Args:
            user_data (dict): Dictionary containing new user information.
            
        Returns:
            bool: True if successful.
        """
        # Check if user already exists based on username or user_id
        for user in self._users:
            if user.get("username") == user_data.get("username"):
                return False
        self._users.append(user_data)
        return True

    def add_group(self, group_data: dict) -> bool:
        """
        Add a new group to the system.

        Args:
            group_data (dict): Dictionary containing new group information.

        Returns:
            bool: True if successful.
        """
        # Prevent duplicate groups by group_id if present
        group_id = group_data.get("group_id")
        if group_id:
            for group in self._groups:
                if group.get("group_id") == group_id:
                    return False
        self._groups.append(group_data)
        return True

    def remove_user(self, user_id: str) -> bool:
        """
        Remove a user from the system.
        
        Args:
            user_id (str): The ID of the user to remove.
            
        Returns:
            bool: True if successful.
        """
        for i, user in enumerate(self._users):
            if user.get("user_id") == user_id:
                self._users.pop(i)
                return True
        return False

    def remove_group(self, group_id: str) -> bool:
        """
        Remove a group from the system.

        Args:
            group_id (str): The ID of the group to remove.

        Returns:
             bool: True if successful.
        """
        for i, group in enumerate(self._groups):
            if group.get("group_id") == group_id:
                self._groups.pop(i)
                return True
        return False

    def update_user(self, user_data: dict) -> bool:
        """
        Update user information.

        Args:
            user_data (dict): Dictionary containing user information.

        Returns:
            bool: True if successful.
        """
        # Update allowed fields (username, is_active) from dict input
        user_id = user_data.get("user_id")
        if not user_id:
            return False

        for user in self._users:
            if user.get("user_id") == user_id:
                if "username" in user_data:
                    user["username"] = user_data["username"]
                if "is_active" in user_data:
                    user["is_active"] = user_data["is_active"]
                return True
        return False

    def update_group(self, group_data: dict) -> bool:
        """
        Update group information.

        Args:
            group_data (dict): Dictionary containing group information.

        Returns:
            bool: True if successful.
        """
        group_id = group_data.get("group_id")
        if not group_id:
            return False

        for group in self._groups:
            if group.get("group_id") == group_id:
                group.update(group_data) # Update all provided fields
                return True
        return False

    def manage_course(self, course_data: dict) -> bool:
        """
        Create or update course information.
        
        Args:
            course_data (dict): Dictionary containing course details.
            
        Returns:
            bool: True if successful.
        """
        # Placeholder for course management logic (not fully specified in requirements, but returns Boolean)
        return True

    def generate_system_report(self) -> dict:
        """
        Generate a system-wide report.
        
        Returns:
            dict: The system report data.
        """
        return {
            "report_type": "System Report",
            "total_users": len(self._users),
            "total_groups": len(self._groups)
        }

    def view_profile(self) -> dict:
        """Override to view Admin profile."""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "role": self._role,
            "admin_id": self._admin_id,
            "permissions": self._permissions
        }


class Teacher(User):
    """
    Teacher subclass representing an instructor.
    """
    def __init__(self, username: str, password_hash: str, is_active: bool = True):
        super().__init__(username, password_hash, "Teacher", is_active)
        self._teacher_id = "T-000"  # Placeholder ID
        self._department = "General"
        self._assigned_courses = []

    def mark_attendance(self, student_list: list, date: str) -> dict:
        """
        Mark attendance for a list of students.
        
        Args:
            student_list (list): List of students present.
            date (str): The date of attendance.
            
        Returns:
            dict: A structured attendance record.
        """
        # Return a structured attendance record as requested
        return {
            "date": date,
            "present_students": student_list,
            "teacher_id": self._teacher_id,
            "status": "recorded"
        }

    def assign_grade(self, student_id: str, course_id: str, grade: float) -> dict:
        """
        Assign a grade to a student.
        
        Args:
            student_id (str): The student's ID.
            course_id (str): The course ID.
            grade (float): The grade to assign.
            
        Returns:
            dict: A structured grade record.
        """
        # Return a structured grade record as requested
        return {
            "student_id": student_id,
            "course_id": course_id,
            "grade": grade,
            "assigned_by": self._teacher_id
        }

    def view_student_progress(self, student_id: str) -> dict:
        """
        View progress of a specific student.
        
        Args:
            student_id (str): The student's ID.
            
        Returns:
            dict: Student progress data.
        """
        return {"student_id": student_id, "progress": "Placeholder Progress"}

    def generate_class_report(self, course_id: str) -> dict:
        """
        Generate a report for a specific course.
        
        Args:
            course_id (str): The course ID.
            
        Returns:
            dict: Class report data.
        """
        return {"course_id": course_id, "average_grade": 0.0}

    def view_profile(self) -> dict:
        """Override to view Teacher profile."""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "role": self._role,
            "teacher_id": self._teacher_id,
            "department": self._department,
            "assigned_courses": self._assigned_courses
        }


class Student(User):
    """
    Student subclass representing a student user.
    """
    def __init__(self, username: str, password_hash: str, is_active: bool = True):
        super().__init__(username, password_hash, "Student", is_active)
        self._student_id = "S-000"  # Placeholder ID
        self._enrolled_courses = []
        self._academic_year = 1
        self._grades = {} # Dictionary to store grades: {course_id: grade}

    def view_attendance(self, course_id: str) -> dict:
        """
        View attendance for a course.
        
        Args:
            course_id (str): The course ID.
            
        Returns:
            dict: Attendance records.
        """
        return {"course_id": course_id, "attendance": []}

    def view_grades(self) -> dict:
        """
        View all grades.
        
        Returns:
            dict: A dictionary of grades.
        """
        return {"student_id": self._student_id, "grades": self._grades}

    def calculate_gpa(self) -> float:
        """
        Calculate the student's GPA.
        
        Returns:
            float: The calculated GPA.
        """
        # Implement simple GPA formula using available grades
        if not self._grades:
            return 0.0
        
        total_points = sum(self._grades.values())
        return total_points / len(self._grades)

    def enroll_course(self, course_id: str) -> bool:
        """
        Enroll in a course.
        
        Args:
            course_id (str): The course ID.
            
        Returns:
            bool: True if successful.
        """
        # Append course only if not already enrolled
        if course_id not in self._enrolled_courses:
            self._enrolled_courses.append(course_id)
            return True
        return False

    def view_profile(self) -> dict:
        """Override to view Student profile."""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "role": self._role,
            "student_id": self._student_id,
            "academic_year": self._academic_year,
            "enrolled_courses": self._enrolled_courses
        }
