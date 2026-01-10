import sys
from storage.storage_manager import StorageManager
from ui import prompts, menus
from models.user import Admin, Teacher, Student

# Configuration
DATA_DIR = "data"

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
                         print("Login failed. Account is inactive.")
                         continue

                    # Instantiate user to check password logic
                    user_obj = create_user_from_dict(found_user_data)
                    
                    if not user_obj:
                        print("Login failed. System error: Invalid user role.")
                        continue

                    if user_obj.authenticate(password):
                         current_user = user_obj
                         print(f"Welcome, {current_user._username}!")
                    else:
                        print("Login failed. Invalid credentials.")
                else:
                    print("Login failed. Invalid credentials.")
            
            else:
                # 3. Role Routing
                role = current_user._role
                action = None
                
                if role == 'Admin':
                    action = menus.admin_menu()
                    # 4. Action Dispatching (Admin)
                    if action == '1':
                        print(">> User Management Module (Placeholder)")
                    elif action == '2':
                        print(">> Course Management Module (Placeholder)")
                    elif action == '3':
                        print(">> Reports Module (Placeholder)")
                    elif action == '4':
                        current_user = None
                        print("Logged out.")
                    elif action == '5':
                        if prompts.prompt_confirmation("Are you sure you want to exit?"):
                            print("Backing up data...")
                            storage.backup_data()
                            print("Goodbye!")
                            sys.exit(0)
                            
                elif role == 'Teacher':
                    action = menus.teacher_menu()
                    # 4. Action Dispatching (Teacher)
                    if action == '1':
                        print(">> Attendance Module (Placeholder)")
                    elif action == '2':
                        print(">> Progress Module (Placeholder)")
                    elif action == '3':
                        print(">> View Students Module (Placeholder)")
                    elif action == '4':
                        current_user = None
                        print("Logged out.")
                    elif action == '5':
                        if prompts.prompt_confirmation("Are you sure you want to exit?"):
                            print("Backing up data...")
                            storage.backup_data()
                            print("Goodbye!")
                            sys.exit(0)

                elif role == 'Student':
                    action = menus.student_menu()
                    # 4. Action Dispatching (Student)
                    if action == '1':
                        print(">> View Attendance Module (Placeholder)")
                    elif action == '2':
                        print(">> View Progress Module (Placeholder)")
                    elif action == '3':
                        print(">> View Courses Module (Placeholder)")
                    elif action == '4':
                        current_user = None
                        print("Logged out.")
                    elif action == '5':
                        if prompts.prompt_confirmation("Are you sure you want to exit?"):
                            print("Backing up data...")
                            storage.backup_data()
                            print("Goodbye!")
                            sys.exit(0)
                            
                else:
                    print(f"Error: Unknown role {role}. Logging out.")
                    current_user = None

    except KeyboardInterrupt:
        print("\n\nShutdown requested via Ctrl+C.")
        print("Backing up data...")
        storage.backup_data()
        print("Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
