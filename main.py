import sys

from jinja2.nodes import FromImport
from uaclient.status import status

from student_management_system.storage.storage_manager import StorageManager
from student_management_system.ui import prompts, menus
from student_management_system.models.user import Admin, Teacher, Student
from student_management_system.models.attendance import Attendance
from student_management_system.models.grade import Grade
from student_management_system import utils
from colorama import Fore, Style



# Configuration
DATA_DIR = "student_management_system/data"
RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
RESET = Style.RESET_ALL

def create_user_from_dict(data: dict):
    """Helper to instantiate appropriate User subclass from dict data."""
    role = data.get('_role')
    username = data.get('_username')
    password_hash = data.get('_password_hash')
    is_active = data.get('_is_active', True)

    user = None
    if role == 'Admin':
        user = Admin(username, password_hash, is_active)
    elif role == 'Teacher':
        user = Teacher(username, password_hash, is_active)
    elif role == 'Student':
        user = Student(username, password_hash, is_active)
    else:
        return None
    
    if '_user_id' in data:
        user._user_id = data['_user_id']
    
    return user

def main():
    print("Initializing Student Progress and Attendance Management System...")
    
    # 1. System Boot
    storage = StorageManager(DATA_DIR)
    
    if not storage.validate_data_integrity():
        print("CRITICAL ERROR: Data integrity validation failed.")
        sys.exit(1)
        
    print("System initialized successfully.")

    current_user = None

    try:
        while True:
            # 2. Authentication Loop
            if not current_user:
                username, password = prompts.prompt_login()
                
                users_data = storage.load_users()
                found_user_data = None
                
                for u_data in users_data:
                    if u_data.get('_username') == username:
                        found_user_data = u_data
                        break
                
                if found_user_data:
                    # Enforce Active Status
                    if not found_user_data.get('_is_active', True):
                         prompts.display_error("Login failed. Account is inactive.")
                         continue

                    # Instantiate user to check password logic
                    user_obj = create_user_from_dict(found_user_data)
                    
                    if not user_obj:
                        prompts.display_error("Login failed. System error: Invalid user role.")
                        continue

                    # In a real app, hash checking happens here. 
                    # user_obj.authenticate expects the stored hash to equal input password (as per Model step 1, 
                    # "Actual hashing is handled elsewhere; compare hashes only").
                    # Since we don't have a hasher, we assume plain text match for this console demo.
                    if user_obj.authenticate(password):
                         current_user = user_obj
                         prompts.display_message(f"Welcome, {current_user._username}!")
                    else:
                        prompts.display_error("Login failed. Invalid credentials.")
                else:
                    prompts.display_error("Login failed. Invalid credentials.")
            
            else:
                # 3. Role Routing
                role = current_user._role
                action = None

                if role == 'Admin':
                    action = menus.admin_menu()
                    # 4. Action Dispatching (Admin)
                    if action == '1': # Add User
                        new_user_data = prompts.prompt_user_details()
                        # Load existing to check dupe username
                        existing_users = storage.load_users()
                        if any(u['_username'] == new_user_data['_username'] for u in existing_users):
                            prompts.display_error("Username already exists.")
                        else:
                            # Generate simple ID
                            count = len(existing_users) + 1
                            prefix = new_user_data['_role'][0].upper()
                            new_user_data['_user_id'] = f"{prefix}-{count:03d}"
                            
                            existing_users.append(new_user_data)
                            if storage.save_users(existing_users):
                                prompts.display_message(f"User {new_user_data['_username']} created successfully.")
                            else:
                                prompts.display_error("Failed to save user.")

                    elif action == '2' :        #Update user's data
                        pass

                    elif action == 3:  # Delete User
                        users = storage.load_users()
                        if users:
                            print("\n--- Users List ---")

                            for u in users:
                                print(f"ID: {u.get('_user_id')} | Name: {u.get('_username')}")

                            else : prompts.display_message("No Users found.")

                            username = input("Input username to delete: ")
                            # Find the specific user dictionary to delete
                            user_to_delete = next((u for u in users if u['_username'] == username), None)

                            if user_to_delete:
                                users.remove(user_to_delete)
                                storage.save_users(users)  # Ensure you save the updated list
                                prompts.display_message(f"User {username} deleted successfully.")

                            else: prompts.display_error("Failed to delete user.")

                    # elif action == '3' :        #Delete User
                    #     users = storage.load_users()
                    #     if users:
                    #         print("\n--- Users List ---")
                    #         for u in users:
                    #             print(f"ID: {u.get('_user_id')} | Name: {u.get('_username')}")
                    #
                    #
                    #     username = input('Input username to delete : ')
                    #     if any(u['_username'] == username for u in users):
                    #         users.remove([u['_username'] for u in users])

                    elif action == '4' :        #Create Group
                        pass

                    elif action == '5' :        #Update Group
                        pass

                    elif action == '6' :        # Delete Group
                        pass


                    elif action == '7' :        # Show Users
                        pass

                    elif action == "8" :        #Show Groups
                        pass

                    elif action == '9': # Course Management
                        prompts.display_message("Course Management Module (Placeholder)")

                    elif action == '10': # System Reports
                        # Generate both reports
                        att_records = storage.load_attendance()
                        grades_records = storage.load_grades()
                        
                        success_att = utils.generate_attendance_report(att_records)
                        success_prog = utils.generate_progress_report(grades_records)
                        
                        if success_att and success_prog:
                            prompts.display_message("Reports generated in 'reports/' directory.")
                        else:
                            prompts.display_error("Failed to generate some reports.")

                    elif action == '11': # Logout
                        current_user = None
                        prompts.display_message("Logged out.")

                    elif action == '12': # Exit
                        if prompts.prompt_confirmation("Are you sure you want to exit?"):
                            print("Backing up data...")
                            storage.backup_data()
                            print("Goodbye!")
                            sys.exit(0)
                            
                elif role == 'Teacher':
                    action = menus.teacher_menu()
                    # 4. Action Dispatching (Teacher)
                    if action == '1': # Mark Attendance
                        att_data = prompts.prompt_attendance_details()
                        current_records = storage.load_attendance()
                        
                        # Create attendance object (logic check)
                        att = Attendance(
                            att_data['student_id'],
                            att_data['course_id'],
                            att_data['date'],
                            att_data['status'],
                            current_user._username
                        )
                        current_records.append(att.to_dict())
                        
                        if storage.save_attendance(current_records):
                            prompts.display_message("Attendance marked successfully.")
                        else:
                            prompts.display_error("Failed to save attendance.")

                    elif action == '2': # Assign Grade
                        grade_data = prompts.prompt_grade_details()
                        current_grades = storage.load_grades()
                        
                        grade = Grade(
                            grade_data['student_id'],
                            grade_data['course_id'],
                            grade_data['score'],
                            grade_data['max_score'],
                            grade_data['weight']
                        )
                        current_grades.append(grade.to_dict())
                        
                        if storage.save_grades(current_grades):
                            prompts.display_message("Grade assigned successfully.")
                        else:
                            prompts.display_error("Failed to save grade.")

                    elif action == '3': # View Students
                        students = storage.load_students()
                        if students:
                            print("\n--- Student List ---")
                            for u in students:
                                print(f"ID: {u.get('_user_id')} | Name: {u.get('_username')}")
                        else:
                            prompts.display_message("No students found.")

                    elif action == '4': # Logout
                        current_user = None
                        prompts.display_message("Logged out.")
                    
                    elif action == '5': # Exit
                        if prompts.prompt_confirmation("Are you sure you want to exit?"):
                            print("Backing up data...")
                            storage.backup_data()
                            print("Goodbye!")
                            sys.exit(0)

                elif role == 'Student':
                    action = menus.student_menu()
                    # 4. Action Dispatching (Student)
                    if action == '1': # Check Attendance
                        my_id = getattr(current_user, '_user_id', None)
                        if not my_id:
                            # Try finding by username references if ID not set in object (should be set by create func)
                            prompts.display_error("User ID not found.")
                            continue
                            
                        all_att = storage.load_attendance()
                        user_att = [r for r in all_att if r['student_id'] == my_id]
                        
                        if user_att:
                            print(f"\n{BLUE}--- Attendance Record for {current_user._username} ---")
                            print(f"{BLUE}{'Date':<12} | {'Course':<10} | {'Status':<6}")
                            print("-" * 35)
                            for r in user_att:
                                print(f"{RED if r['status'] == 'A' else (GREEN if r['status'] == 'P' else YELLOW)}{r['date'] :<12} | {r['course_id'] :<10} | {r['status'] :<6}{RESET}")
                        else:
                            prompts.display_message("No attendance records found.")

                    elif action == '2': # Check Progress
                        my_id = getattr(current_user, '_user_id', None)
                        if not my_id:
                            prompts.display_error("User ID not found.")
                            continue

                        all_grades = storage.load_grades()
                        user_grades = [g for g in all_grades if g['student_id'] == my_id]

                        if user_grades:
                            print(f"\n{BLUE}--- Progress Record for {current_user._username} ---")
                            print(f"{BLUE}{'Course':<10} | {'Score':<8} | {'Max':<8} | {'%':<6}")
                            print("-" * 40)
                            for g in user_grades:
                                score = float(g['score'])
                                max_s = float(g['max_score'])
                                perc = (score / max_s * 100) if max_s > 0 else 0
                                print(f"{GREEN if perc >= 85.0 else (YELLOW if 70.0 < perc < 84.0 else RED)}{g['course_id']:<10} | {score:<8} | {max_s:<8} | {perc:.1f}%"f"{RESET}")

                            # Calculate GPA
                            gpa = utils.calculate_gpa(user_grades)
                            print(f'{GREEN if gpa > 3.0 else(YELLOW if 2.0<gpa<3.0 else RED)}'f"\nEstimated GPA: {gpa}"f"{RESET}")
                        else:
                            prompts.display_message("No grades found.")

                    elif action == '3': # View Courses
                        # Placeholder as no course mapping yet
                        prompts.display_message("Enrolled courses: [Not Implemented]")

                    elif action == '4': # Logout
                        current_user = None
                        prompts.display_message("Logged out.")
                    
                    elif action == '5': # Exit
                        if prompts.prompt_confirmation("Are you sure you want to exit?"):
                            print("Backing up data...")
                            storage.backup_data()
                            print("Goodbye!")
                            sys.exit(0)
                            
                else:
                    prompts.display_error(f"Error: Unknown role {role}. Logging out.")
                    current_user = None

    except KeyboardInterrupt:
        print("\n\nShutdown requested via Ctrl+C.")
        print("Backing up data...")
        storage.backup_data()
        print("Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
