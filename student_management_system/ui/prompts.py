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
