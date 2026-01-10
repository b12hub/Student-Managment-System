from student_management_system.utils import validate_date, normalize_input

def prompt_login() -> tuple:
    """
    Prompts the user for username and password.
    Returns:
        tuple: (username, password)
    """
    print("\n--- LOGIN ---")
    while True:
        username = input("Username: ").strip()
        if username:
            break
        print("Username cannot be empty.")
    
    while True:
        password = input("Password: ").strip()
        if password:
            break
        print("Password cannot be empty.")
        
    return username, password

def prompt_menu(options: dict) -> str:
    """
    Displays a menu based on the provided options dictionary.
    Args:
        options (dict): Key-value pairs of menu options.
    Returns:
        str: The selected key.
    """
    print("\n--- MENU ---")
    for key, value in options.items():
        print(f"{key}. {value}")
        
    while True:
        selection = input("Select an option: ").strip()
        if selection in options:
            return selection
        print("Invalid selection. Please try again.")

def prompt_confirmation(message: str) -> bool:
    """
    Prompts the user for confirmation (y/n).
    Args:
        message (str): The confirmation message.
    Returns:
        bool: True if confirmed, False otherwise.
    """
    while True:
        response = input(f"{message} (y/n): ").strip().lower()
        if response == 'y':
            return True
        elif response == 'n':
            return False
        print("Please enter 'y' or 'n'.")

def prompt_user_details() -> dict:
    """
    Prompts for new user details.
    Returns:
        dict: User data including username, password, role.
    """
    print("\n[User Creation]")
    while True:
        username = normalize_input(input("Username: "))
        if username: break
        print("Username required.")
        
    while True:
        password = normalize_input(input("Password: ")) # Hash usually done later or here? Model takes hash.
        # For simplicity, we pass plain text to controller which hashes it, OR prompt returns raw.
        # Step 4 said "Match credentials against users.json", previous code checks hash. 
        # Models expect password_hash. 
        # For this prompt, we return the raw password.
        if password: break
        print("Password required.")
        
    print("Roles: Admin, Teacher, Student")
    while True:
        role = normalize_input(input("Role: ")).capitalize()
        if role in ['Admin', 'Teacher', 'Student']:
            break
        print("Invalid role. Choose Admin, Teacher, or Student.")
        
    return {
        '_username': username,
        '_password': password, # Note: temporary key, controller should hash
        '_role': role,
        '_is_active': True 
    }

def prompt_attendance_details() -> dict:
    """
    Prompts for attendance marking details.
    Returns:
        dict: student_id, course_id, date, status
    """
    print("\n[Mark Attendance]")
    while True:
        student_id = normalize_input(input("Student ID: "))
        if student_id: break
        print("Student ID required.")
        
    while True:
        course_id = normalize_input(input("Course ID: "))
        if course_id: break
        print("Course ID required.")
        
    while True:
        date_str = normalize_input(input("Date (YYYY-MM-DD): "))
        if validate_date(date_str):
            break
        print("Invalid date format. Use YYYY-MM-DD.")
        
    print("Statuses: P (Present), A (Absent), L (Late), E (Excused)")
    while True:
        status = normalize_input(input("Status: ")).upper()
        if status in ['P', 'A', 'L', 'E']:
            break
        print("Invalid status.")
        
    return {
        'student_id': student_id,
        'course_id': course_id,
        'date': date_str,
        'status': status
    }

def prompt_grade_details() -> dict:
    """
    Prompts for grade assignment details.
    Returns:
        dict: student_id, course_id, score, max_score, weight
    """
    print("\n[Assign Grade]")
    while True:
        student_id = normalize_input(input("Student ID: "))
        if student_id: break
        print("Student ID required.")
        
    while True:
        course_id = normalize_input(input("Course ID: "))
        if course_id: break
        print("Course ID required.")
        
    while True:
        try:
            score = float(input("Score: "))
            if score >= 0: break
            print("Score must be non-negative.")
        except ValueError:
            print("Invalid number.")
            
    while True:
        try:
            max_score = float(input("Max Score: "))
            if max_score > 0: break
            print("Max score must be positive.")
        except ValueError:
            print("Invalid number.")
            
    while True:
        try:
            weight = float(input("Weight (0-1.0): "))
            if 0 <= weight <= 1.0: break
            print("Weight must be between 0 and 1.0.")
        except ValueError:
            print("Invalid number.")
            
    return {
        'student_id': student_id,
        'course_id': course_id,
        'score': score,
        'max_score': max_score,
        'weight': weight
    }

def display_message(message: str):
    print(f"\n[INFO] {message}")

def display_error(message: str):
    print(f"\n[ERROR] {message}")
