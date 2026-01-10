from . import prompts

def admin_menu() -> str:
    """
    Displays the Admin menu.
    Returns:
        str: Selected action key.
    """
    options = {
        "1": "User Management",
        "2": "Course Management",
        "3": "Reports",
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
        "1": "Attendance",
        "2": "Progress",
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
        "1": "View Attendance",
        "2": "View Progress",
        "3": "View Courses",
        "4": "Logout",
        "5": "Exit"
    }
    print("\n[STUDENT DASHBOARD]")
    return prompts.prompt_menu(options)
