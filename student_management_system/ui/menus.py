from . import prompts

def admin_menu() -> str:
    """
    Displays the Admin menu.
    Returns:
        str: Selected action key.
    """
    options = {
        "1": "Add User",
        "2": "Course Management", # Placeholder for now as mainly User/Attendance/Grade focus
        "3": "System Reports",
        "4": "Logout",
        "5": "Exit"
    }
    print("\n[ADMIN DASHBOARD]")
    return prompts.prompt_menu(options)

def teacher_menu() -> str:
    """
    Displays the Teacher menu.
    Returns:
        str: Selected action key.
    """
    options = {
        "1": "Mark Attendance",
        "2": "Assign Grade",
        "3": "View Students",
        "4": "Logout",
        "5": "Exit"
    }
    print("\n[TEACHER DASHBOARD]")
    return prompts.prompt_menu(options)

def student_menu() -> str:
    """
    Displays the Student menu.
    Returns:
        str: Selected action key.
    """
    options = {
        "1": "Check Attendance",
        "2": "Check Progress",
        "3": "View Courses",
        "4": "Logout",
        "5": "Exit"
    }
    print("\n[STUDENT DASHBOARD]")
    return prompts.prompt_menu(options)
