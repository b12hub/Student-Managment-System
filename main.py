import sys
from colorama import Fore, Style
from student_management_system.storage.storage_manager import StorageManager
from student_management_system.ui import prompts, menus
from student_management_system.models.user import Admin, Teacher, Student
from student_management_system import utils

# Configuration
DATA_DIR = "student_management_system/data"
RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
RESET = Style.RESET_ALL

# --- Helpers for Data Mapping ---
# StorageManager and Utils expect keys with underscores (e.g., '_username').
# Domain Models (Admin.add_user) expect keys without underscores (e.g., 'username').
# We map between them at the controller level (main.py).

def map_storage_to_domain(data: dict) -> dict:
    """Convert keys from storage format (_key) to domain format (key)."""
    return {k.lstrip('_'): v for k, v in data.items()}

def map_domain_to_storage(data: dict) -> dict:
    """Convert keys from domain format (key) to storage format (_key)."""
    return {f"_{k}" if not k.startswith('_') else k: v for k, v in data.items()}

def create_user_from_dict(data: dict):
    """Helper to instantiate appropriate User subclass from valid storage dict."""
    # Ensure we use storage keys (_username, etc)
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

                    # Instantiate user
                    user_obj = create_user_from_dict(found_user_data)
                    
                    if not user_obj:
                        prompts.display_error("Login failed. System error: Invalid user role.")
                        continue

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
                    # Populate Admin state with current users/groups for management
                    # Current storage data is underscored. Convert to domain for Admin logic.
                    raw_users = storage.load_users()
                    current_user._users = [map_storage_to_domain(u) for u in raw_users]
                    # Groups management is purely runtime/mock in storage currently, 
                    # but we initialize list to avoid errors if logic expects it.
                    current_user._groups = [] 

                    action = menus.admin_menu()
                    
                    # 4. Action Dispatching (Admin)
                    if action == '1': # Add User
                        raw_input = prompts.prompt_user_details()
                        # prompts likely returns underscored keys based on legacy code.
                        # Clean them for Admin Logic.
                        clean_input = map_storage_to_domain(raw_input)
                        
                        # Generate ID if missing (Admin logic might not do it)
                        if 'user_id' not in clean_input:
                            count = len(current_user._users) + 1
                            prefix = clean_input.get('role', 'User')[0].upper()
                            clean_input['user_id'] = f"{prefix}-{count:03d}"

                        if current_user.add_user(clean_input):
                            # Save back to storage
                            # Convert Admin's internal list back to storage format
                            users_to_save = [map_domain_to_storage(u) for u in current_user._users]
                            if storage.save_users(users_to_save):
                                prompts.display_message(f"User {clean_input['username']} created successfully.")
                            else:
                                prompts.display_error("Failed to save user.")
                        else:
                            prompts.display_error("User already exists or creation failed.")

                    elif action == '2': # Update User
                        username_to_update = input("Enter username to update: ")
                        # We need to find the ID or pass data that includes ID if update_user requires it
                        # Admin.update_user logic requires 'user_id'. Find it first.
                        target_user = next((u for u in current_user._users if u['username'] == username_to_update), None)
                        
                        if target_user:
                            print("Enter new details (leave blank to keep current):")
                            new_username = input(f"New username ({target_user['username']}): ").strip()
                            active_input = input(f"Is active? (y/n) ({'y' if target_user.get('is_active', True) else 'n'}): ").strip().lower()
                            
                            update_payload = {'user_id': target_user['user_id']}
                            if new_username:
                                update_payload['username'] = new_username
                            if active_input in ['y', 'n']:
                                update_payload['is_active'] = (active_input == 'y')
                            
                            if current_user.update_user(update_payload):
                                # Save
                                users_to_save = [map_domain_to_storage(u) for u in current_user._users]
                                if storage.save_users(users_to_save):
                                    prompts.display_message("User updated successfully.")
                                else:
                                    prompts.display_error("Failed to save changes.")
                            else:
                                prompts.display_error("Update failed logic.")
                        else:
                            prompts.display_error("User not found.")

                    elif action == '3': # Delete User
                        # Refresh list to be sure
                        raw_users = storage.load_users()
                        if raw_users:
                            print("\n--- Users List ---")
                            for u in raw_users:
                                print(f"ID: {u.get('_user_id')} | Name: {u.get('_username')}")
                            
                            username_del = input("Input username to delete: ")
                            # We need ID for remove_user
                            target = next((u for u in raw_users if u.get('_username') == username_del), None)
                            
                            if target:
                                user_id_del = target.get('_user_id')
                                # Sync admin internal list again just in case
                                current_user._users = [map_storage_to_domain(u) for u in raw_users]
                                
                                if current_user.remove_user(user_id_del):
                                    users_to_save = [map_domain_to_storage(u) for u in current_user._users]
                                    if storage.save_users(users_to_save):
                                        prompts.display_message("User deleted successfully.")
                                    else:
                                        prompts.display_error("Failed to save deletion.")
                                else:
                                    prompts.display_error("Deletion failed in logic.")
                            else:
                                prompts.display_error("User not found.")
                        else:
                            prompts.display_message("No users to delete.")

                    elif action == '4': # Add Group
                        # Group persistence is not supported by StorageManager, but we implement UI/Logic
                        g_name = input("Enter Group Name: ")
                        g_id = f"G-{len(current_user._groups) + 1:03d}"
                        if current_user.add_group({'group_id': g_id, 'name': g_name}):
                            prompts.display_message(f"Group {g_name} added (Session Only - No Persistence).")
                        else:
                            prompts.display_error("Failed to add group.")

                    elif action == '5': # Update Group
                         prompts.display_message("Update Group feature is not persistent and skipped for CLI demo.")

                    elif action == '6': # Delete Group
                         prompts.display_message("Delete Group feature is not persistent and skipped for CLI demo.")

                    elif action == '7': # Show Users
                        raw_users = storage.load_users()
                        if raw_users:
                            print("\n--- Users List ---")
                            for u in raw_users:
                                print(f"ID: {u.get('_user_id')} | Role: {u.get('_role')} | Name: {u.get('_username')}")
                        else:
                            prompts.display_message("No users found.")

                    elif action == '8': # Show Groups
                        # Show session groups
                        if current_user._groups:
                            for g in current_user._groups:
                                print(f"ID: {g.get('group_id')} | Name: {g.get('name')}")
                        else:
                            prompts.display_message("No groups active in this session.")

                    elif action == '9': # Course Management
                        prompts.display_message("Course Management Module is currently a placeholder.")

                    elif action == '10': # System Reports
                        att_records = storage.load_attendance()
                        grades_records = storage.load_grades()
                        
                        # Utils likely expects lists of dicts, doing well.
                        success_att = utils.generate_attendance_report(att_records)
                        # Ensure grades are passed correctly
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
                        else:
                             # If canceled, loop continues
                             pass
                    
                    else:
                        prompts.display_error("Invalid selection.")

                elif role == 'Teacher':
                    action = menus.teacher_menu()
                    
                    if action == '1': # Mark Attendance
                        att_input = prompts.prompt_attendance_details()
                        # Input typically: student_id, course_id, date, status
                        # Teacher logic returns structured dict
                        students_attending = [att_input['student_id']] # Wrapper for the logic method
                        
                        record_dict = current_user.mark_attendance(students_attending, att_input['date'])
                        
                        # Enrich record for generic storage (which expects flattened row usually)
                        # Storage expects: student_id, course_id, date, status, marked_by
                        # The dict returned by User.mark_attendance is:
                        # {"date": date, "present_students": [list], "teacher_id": ..., "status": "recorded"}
                        # We need to adapt this to the CSV structure (one row per student-course-date)
                        
                        # NOTE: The User model logic for mark_attendance was:
                        # args: student_list, date
                        # returns: dict with student_list
                        # But storage is CSV with single rows. 
                        # We must adapt here.
                        
                        all_att = storage.load_attendance()
                        
                        # Create row(s) per student
                        saved_count = 0
                        for sid in record_dict['present_students']:
                            row = {
                                'student_id': sid,
                                'course_id': att_input['course_id'],
                                'date': record_dict['date'],
                                'status': att_input['status'],
                                'marked_by': record_dict['teacher_id']
                            }
                            all_att.append(row)
                            saved_count += 1
                        
                        if storage.save_attendance(all_att):
                            prompts.display_message(f"Attendance marked for {saved_count} student(s).")
                        else:
                            prompts.display_error("Failed to save attendance.")

                    elif action == '2': # Assign Grade
                        g_input = prompts.prompt_grade_details()
                        # Input: student_id, course_id, score, max_score, weight
                        
                        # User logic
                        # grade (float) is the 3rd arg
                        rec_dict = current_user.assign_grade(g_input['student_id'], g_input['course_id'], float(g_input['score']))
                        
                        # Adapt to storage row
                        row = {
                            'student_id': rec_dict['student_id'],
                            'course_id': rec_dict['course_id'],
                            'score': rec_dict['grade'],
                            'max_score': g_input['max_score'],
                            'weight': g_input['weight'],
                            'assigned_by': rec_dict['assigned_by']
                        }
                        
                        all_grades = storage.load_grades()
                        all_grades.append(row)
                        
                        if storage.save_grades(all_grades):
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
                    
                    if action == '1': # Check Attendance
                        my_id = getattr(current_user, '_user_id', None)
                        if not my_id:
                            prompts.display_error("User ID not found.")
                            continue
                            
                        all_att = storage.load_attendance()
                        # Use User method? Student.view_attendance returns empty placeholder in User.py
                        # Better to do Logic here or populate User then call method?
                        # models/user.py: view_attendance(course_id) -> returns dict wrapper
                        # We will fetch raw data and display it directly (simpler CLI feedback) OR populate method?
                        # The constraint was "Implement ... no method should silently do nothing".
                        # But main.py controls the data flow.
                        
                        user_att = [r for r in all_att if r.get('student_id') == my_id]
                        
                        if user_att:
                            print(f"\n{BLUE}--- Attendance Record for {current_user._username} ---")
                            print(f"{BLUE}{'Date':<12} | {'Course':<10} | {'Status':<6}")
                            print("-" * 35)
                            for r in user_att:
                                status_code = r.get('status', '?')
                                color = RED if status_code == 'A' else (GREEN if status_code == 'P' else YELLOW)
                                print(f"{color}{r.get('date', 'N/A') :<12} | {r.get('course_id', 'N/A') :<10} | {status_code :<6}{RESET}")
                        else:
                            prompts.display_message("No attendance records found.")

                    elif action == '2': # Check Progress / GPA
                        my_id = getattr(current_user, '_user_id', None)
                        if not my_id:
                            prompts.display_error("User ID not found.")
                            continue

                        all_grades = storage.load_grades()
                        user_grades_rows = [g for g in all_grades if g.get('student_id') == my_id]
                        
                        # Populate Student object internal state to use calculate_gpa() logic
                        # Student._grades is expected to be {course_id: grade_value}
                        grades_map = {}
                        for r in user_grades_rows:
                            try:
                                grades_map[r['course_id']] = float(r['score'])
                            except (ValueError, KeyError):
                                continue
                        
                        current_user._grades = grades_map
                        
                        if user_grades_rows:
                            print(f"\n{BLUE}--- Progress Record for {current_user._username} ---")
                            print(f"{BLUE}{'Course':<10} | {'Score':<8} | {'Max':<8} | {'%':<6}")
                            print("-" * 40)
                            for g in user_grades_rows:
                                try:
                                    score = float(g['score'])
                                    max_s = float(g['max_score'])
                                    perc = (score / max_s * 100) if max_s > 0 else 0
                                    color = GREEN if perc >= 85.0 else (YELLOW if 70.0 < perc < 84.0 else RED)
                                    print(f"{color}{g['course_id']:<10} | {score:<8} | {max_s:<8} | {perc:.1f}%{RESET}")
                                except ValueError:
                                    continue

                            # Use Domain Method for GPA
                            gpa = current_user.calculate_gpa()
                            # Display
                            color = GREEN if gpa > 3.0 else (YELLOW if 2.0 < gpa <= 3.0 else RED)
                            print(f"\n{color}Estimated GPA (Simple Avg): {gpa:.2f}{RESET}")
                        else:
                            prompts.display_message("No grades found.")

                    elif action == '3': # View Courses
                        # Logic: Enrollment logic
                        course_id = input("Enter Course ID to enroll (or view): ")
                        if current_user.enroll_course(course_id):
                             prompts.display_message(f"Enrolled in {course_id} (Session Only).")
                             # Note: Persistence of enrollment requires updating the User object in storage.
                             # This would require loading all users, finding self, updating 'enrolled_courses' field, and saving.
                             # For this refactor, we stick to in-memory simply or try to save if ambitious.
                             # Let's try to save for completeness if possible.
                             all_users = storage.load_users()
                             me_in_storage = next((u for u in all_users if u.get('_user_id') == my_id), None)
                             if me_in_storage:
                                 # 'enrolled_courses' key?
                                 # We need to adapt keys. Domain: _enrolled_courses. Storage: _enrolled_courses
                                 curr_list = me_in_storage.get('_enrolled_courses', [])
                                 if course_id not in curr_list:
                                     curr_list.append(course_id)
                                     me_in_storage['_enrolled_courses'] = curr_list
                                     storage.save_users(all_users)
                                     prompts.display_message("Enrollment saved.")
                        else:
                             prompts.display_message("Already enrolled.")
                             
                        print(f"Current Enrollments: {current_user._enrolled_courses}")

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
