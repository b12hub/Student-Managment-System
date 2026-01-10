
import os
import sys
import json
import csv
import unittest
from unittest.mock import patch
from io import StringIO
import shutil

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from student_management_system.storage.storage_manager import StorageManager
# We will import main inside tests to ensure fresh starts or handle state if needed,
# but main.py is in root so we need to be careful with imports.
# main.py does 'from student_management_system import ...' 
# Depending on how the user runs it.
# Let's assume we run this script from the root.

class TestStudentManagementSystem(unittest.TestCase):
    
    DATA_DIR = "student_management_system/data"
    REPORTS_DIR = "student_management_system/reports"
    
    @classmethod
    def setUpClass(cls):
        # Backup existing data if any (though we did it manually)
        # cls.backup_existing_data()
        pass

    def setUp(self):
        # Reset data directory for each test
        if os.path.exists(self.DATA_DIR):
            shutil.rmtree(self.DATA_DIR)
        os.makedirs(self.DATA_DIR)
        if os.path.exists(self.REPORTS_DIR):
            shutil.rmtree(self.REPORTS_DIR)
            
        # Seed Admin User
        self.seed_admin_user()

    def seed_admin_user(self):
        users = [
            {
                "_username": "admin",
                "_password_hash": "admin123", # Plain text for this assignment
                "_role": "Admin",
                "_is_active": True,
                "_user_id": "A-001"
            }
        ]
        with open(os.path.join(self.DATA_DIR, "users.json"), "w") as f:
            json.dump(users, f)

    def run_main_with_inputs(self, inputs):
        """Helper to run main() with a sequence of inputs"""
        # We need to import main here to ensure it uses the specific environment if global vars change
        import main
        
        # Patch input and stdout
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                try:
                    main.main()
                except SystemExit:
                    pass # Expected on exit
                return mock_stdout.getvalue()

    def test_01_boot_and_integrity(self):
        """STEP 1: Test valid boot and integrity check on fresh data."""
        # Just run and exit immediately
        # Input flow: 'admin', 'admin123' (login), '5' (exit), 'y' (confirm)
        output = self.run_main_with_inputs(['admin', 'admin123', '5', 'y'])
        
        self.assertIn("System initialized successfully", output)
        self.assertIn("Welcome, admin!", output)
        self.assertIn("Goodbye!", output)

    def test_02_admin_workflow(self):
        """STEP 3: Admin creates users and reports."""
        inputs = [
            'admin', 'admin123',  # Login
            '1',                  # Add User
            'teacher1', 'pass1', 'Teacher', # Details for Teacher
            '1',                  # Add User
            'student1', 'pass1', 'Student', # Details for Student
            '1',                  # Add User (Duplicate check)
            'student1', 'pass2', 'Student', 
            '3',                  # Generate Reports (Initially empty but runs)
            '5', 'y'              # Exit
        ]
        output = self.run_main_with_inputs(inputs)
        
        # Verify Output messages
        self.assertIn("User teacher1 created successfully", output)
        self.assertIn("User student1 created successfully", output)
        self.assertIn("Username already exists", output) # Duplicate check
        self.assertIn("Reports generated", output)

        # Verify Data Persistence
        with open(os.path.join(self.DATA_DIR, "users.json"), 'r') as f:
            users = json.load(f)
            usernames = [u['_username'] for u in users]
            self.assertIn('teacher1', usernames)
            self.assertIn('student1', usernames)
            # Verify auto ID generation
            for u in users:
                if u['_username'] == 'student1':
                    self.assertTrue(u['_user_id'].startswith('S-'))

    def test_03_teacher_workflow(self):
        """STEP 4: Teacher marks attendance and grades."""
        # 1. Setup Data - Need a student to mark
        users = [
            {"_username": "admin", "_password_hash": "a", "_role": "Admin", "_is_active": True},
            {"_username": "teacher1", "_password_hash": "t", "_role": "Teacher", "_is_active": True, "_user_id": "T-001"},
            {"_username": "student1", "_password_hash": "s", "_role": "Student", "_is_active": True, "_user_id": "S-001"}
        ]
        with open(os.path.join(self.DATA_DIR, "users.json"), "w") as f:
            json.dump(users, f)

        # 2. Run Flow
        inputs = [
            'teacher1', 't',      # Login
            '1',                  # Mark Attendance
            'S-001', 'CS101', '2023-10-10', 'P', # Details
            '2',                  # Assign Grade
            'S-001', 'CS101', '85.5', '100', '1.0', # Details
            '2',                  # Assign Grade (Edge case 0)
            'S-001', 'CS101', '0', '100', '1.0',
            '5', 'y'              # Exit
        ]
        output = self.run_main_with_inputs(inputs)

        self.assertIn("Attendance marked successfully", output)
        self.assertIn("Grade assigned successfully", output)

        # 3. Verify Files
        # Attendance
        with open(os.path.join(self.DATA_DIR, "attendance.csv"), 'r') as f:
            content = f.read()
            self.assertIn("S-001,CS101,2023-10-10,P,teacher1", content)
        
        # Grades
        with open(os.path.join(self.DATA_DIR, "grades.csv"), 'r') as f:
            content = f.read()
            self.assertIn("S-001,CS101,85.5,100,1.0", content)
            self.assertIn("S-001,CS101,0", content)

    def test_04_student_workflow(self):
        """STEP 5: Student checks own data."""
        # 1. Setup Data
        users = [
             {"_username": "student1", "_password_hash": "s", "_role": "Student", "_is_active": True, "_user_id": "S-001"},
             {"_username": "student2", "_password_hash": "s", "_role": "Student", "_is_active": True, "_user_id": "S-002"}
        ]
        with open(os.path.join(self.DATA_DIR, "users.json"), "w") as f:
            json.dump(users, f)
            
        # Add some grades and attendance
        with open(os.path.join(self.DATA_DIR, "attendance.csv"), "w") as f:
            f.write("student_id,course_id,date,status,marked_by\n")
            f.write("S-001,CS101,2023-01-01,P,t1\n")
            f.write("S-002,CS101,2023-01-01,A,t1\n") # Should not see this
            
        with open(os.path.join(self.DATA_DIR, "grades.csv"), "w") as f:
            f.write("student_id,course_id,score,max_score,weight\n")
            f.write("S-001,CS101,90,100,1.0\n")
            f.write("S-002,CS101,50,100,1.0\n") # Should not see this

        # 2. Run Flow
        inputs = [
            'student1', 's',      # Login
            '1',                  # Check Attendance
            '2',                  # Check Progress
            '5', 'y'              # Exit
        ]
        output = self.run_main_with_inputs(inputs)

        # 3. Verify content
        self.assertIn("P", output)   # Own status
        self.assertNotIn("A", output) # Other's status (S-002)
        
        self.assertIn("90.0", output) # Own score
        self.assertIn("90.0%", output) 
        self.assertIn("4.0", output) # GPA for 90% is 4.0

    def test_05_auth_edge_cases(self):
        """STEP 2 & 6: Auth failures and inactive users."""
        users = [
            {"_username": "admin", "_password_hash": "p", "_role": "Admin", "_is_active": True, "_user_id": "A1"},
            {"_username": "lazy", "_password_hash": "p", "_role": "Student", "_is_active": False, "_user_id": "S1"}
        ]
        with open(os.path.join(self.DATA_DIR, "users.json"), "w") as f:
            json.dump(users, f)

        # Sequence: Fail Password -> Invalid User -> Inactive User -> Success Admin -> Exit
        inputs = [
            'admin', 'wrong',    # Bad Pass
            'ghost', 'p',        # Bad User
            'lazy', 'p',         # Inactive
            'admin', 'p',        # Success
            '5', 'y'             # Exit
        ]
        
        output = self.run_main_with_inputs(inputs)
        
        self.assertIn("Login failed. Invalid credentials", output)
        self.assertIn("Login failed. Account is inactive", output)
        self.assertIn("Welcome, admin!", output)

if __name__ == '__main__':
    unittest.main()
