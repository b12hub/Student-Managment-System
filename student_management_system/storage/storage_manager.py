import os
import json
import csv
import shutil
from datetime import datetime

class StorageManager:
    def __init__(self, data_dir: str):
        self.__data_dir = data_dir
        if not os.path.exists(self.__data_dir):
            os.makedirs(self.__data_dir)

    def _get_file_path(self, filename: str) -> str:
        return os.path.join(self.__data_dir, filename)

    # User data
    def load_users(self) -> list:
        file_path = self._get_file_path('users.json')
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def save_users(self, users: list) -> bool:
        file_path = self._get_file_path('users.json')
        try:
            with open(file_path, 'w') as f:
                json.dump(users, f, indent=4)
            return True
        except IOError:
            return False

    # Student data
    def load_students(self) -> list:
        users = self.load_users()
        students = []
        for user in users:
            if user.get('_role') == 'Student':
                students.append(user)
        return students

    # Attendance data (CSV-based)
    def load_attendance(self) -> list:
        file_path = self._get_file_path('attendance.csv')
        if not os.path.exists(file_path):
            return []
        attendance_records = []
        try:
            with open(file_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    attendance_records.append(row)
            return attendance_records
        except (csv.Error, IOError):
            return []

    def save_attendance(self, attendance_records: list) -> bool:
        file_path = self._get_file_path('attendance.csv')
        if not attendance_records:
            return True
            
        try:
            fieldnames = attendance_records[0].keys()
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(attendance_records)
            return True
        except (csv.Error, IOError, IndexError):
            return False

    # Grades data (CSV-based)
    def load_grades(self) -> list:
        file_path = self._get_file_path('grades.csv')
        if not os.path.exists(file_path):
            return []
        grades = []
        try:
            with open(file_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    grades.append(row)
            return grades
        except (csv.Error, IOError):
            return []

    def save_grades(self, grades: list) -> bool:
        file_path = self._get_file_path('grades.csv')
        if not grades:
            return True
        try:
            fieldnames = grades[0].keys()
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(grades)
            return True
        except (csv.Error, IOError, IndexError):
            return False

    # Utility / safety
    def backup_data(self) -> bool:
        backup_dir = os.path.join(self.__data_dir, 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        try:
            files_to_backup = ['users.json', 'attendance.csv', 'grades.csv']
            files_found = False
            for filename in files_to_backup:
                src = self._get_file_path(filename)
                if os.path.exists(src):
                    dst = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
                    shutil.copy2(src, dst)
                    files_found = True
            return files_found
        except IOError:
            return False

    def validate_data_integrity(self) -> bool:
        # users.json
        users_valid = True
        u_path = self._get_file_path('users.json')
        if os.path.exists(u_path):
            # SAFE FIX: If file is empty (0 bytes), initialize it
            if os.path.getsize(u_path) == 0:
                try:
                    with open(u_path, 'w') as f:
                         json.dump([], f)
                except IOError:
                     users_valid = False

            try:
                with open(u_path, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError:
                users_valid = False

        # attendance.csv
        att_valid = True
        a_path = self._get_file_path('attendance.csv')
        if os.path.exists(a_path):
            try:
                with open(a_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if not all(key in row for key in ['student_id', 'course_id', 'date', 'status']):
                            att_valid = False
                            break
                        if row['status'] not in ['P', 'A', 'L', 'E']:
                            att_valid = False
                            break
            except (csv.Error, ValueError):
                att_valid = False
                
        # grades.csv
        grades_valid = True
        g_path = self._get_file_path('grades.csv')
        if os.path.exists(g_path):
            try:
                with open(g_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if not all(key in row for key in ['student_id', 'course_id', 'score', 'max_score']):
                            grades_valid = False
                            break
                        try:
                            float(row['score'])
                            float(row['max_score'])
                        except ValueError:
                            grades_valid = False
                            break
            except (csv.Error, ValueError):
                grades_valid = False

        return users_valid and att_valid and grades_valid
