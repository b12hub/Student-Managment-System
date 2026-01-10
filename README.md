# Student Progress and Attendance Management System

## Project Overview
This project is a console-based (CLI) application designed to manage student progress and attendance in an educational setting. Developed as a deliverable for the Programming in Practice assignment, it utilizes Python and Object-Oriented Programming (OOP) principles to create a maintainable and modular system. The application serves as a comprehensive tool for educational institutions, allowing administrators, teachers, and students to interact with academic data through a strictly defined role-based interface.

## Key Features
*   **Role-Based Access Control (RBAC)**: Distinct distinct interfaces and permissions for Administrators, Teachers, and Students.
*   **Attendance Tracking**: Comprehensive system for recording and monitoring student daily attendance.
*   **Academic Grading**: Facilities for recording, updating, and retrieving student grades across various courses.
*   **Automated Reporting**: Generation of distinct reports for attendance logs and academic progress summaries.
*   **Data Persistence**: Custom file-based storage implementation using JSON and CSV formats.
*   **Input Validation**: Robust handling of user inputs to ensure data integrity and system stability.
*   **System Logging**: Operational and security logs to track system usage and unauthorized access attempts.

## System Architecture
The software is engineered with a separation of concerns, dividing the application into logical layers.

### Directory Structure
```
.
├── assignment_report.md
├── main.py
└── student_management_system/
    ├── config.py
    ├── data/               # Persistent JSON/CSV storage
    ├── decorators/         # Auth and logging decorators
    ├── logs/               # System activity logs
    ├── models/             # Business logic classes (User, Student, Grade)
    ├── report_generator.py # Reporting logic engine
    ├── reports/            # Generated output reports
    ├── storage/            # File I/O management
    ├── ui/                 # Menus and prompts
    └── utils.py            # Helper functions
```

*   **User Interface (UI)**: The presentation layer located in `student_management_system/ui/` handles all console input and output.
*   **Business Logic**: Core domain models (`student_management_system/models/`) and logic controllers utilize OOP to represent entities.
*   **Storage Layer**: The `student_management_system/storage/` directory abstracts file I/O operations.
*   **Utilities**: Helper functions and decorators (`student_management_system/utils.py`, `decorators/`) manage cross-cutting concerns.

## User Roles & Capabilities

### Admin
*   Manage system users (create and remove Teacher and Student accounts).
*   Oversee course data and system configurations.
*   Access and audit system logs (`logs/security.log`, `logs/system.log`).

### Teacher
*   Record and update daily student attendance.
*   Input and modify student grades for assigned courses.
*   Generate aggregate reports for classes.

### Student
*   View personal attendance history and statistics.
*   Access academic progress reports and current grades.

## How to Run the Project

### Prerequisites
*   Python 3.8 or higher.

### Execution Instructions
1.  Navigate to the project root directory:
    ```bash
    # Ensure you are at the project root containing main.py
    cd /path/to/project_root
    ```
2.  Execute the main application script:
    ```bash
    python3 main.py
    ```
3.  Follow the interactive console prompts to log in. Default credentials (if configured) or new user setup can be managed via `student_management_system/config.py`.

## Data Storage Explanation
The system implements a persistent storage mechanism using standard file formats in the `student_management_system/data/` directory.

*   **JSON Storage**: Used for `students.json`, `courses.json`, and `users.json`.
*   **CSV Storage**: Utilized for `attendance.csv` and `grades.csv`.
*   **Integrity & Backups**: The storage manager handles consistency. Regular backups are recommended.

## Reports Generated
The system includes a dedicated reporting engine (`report_generator.py`) capable of producing the following outputs in `student_management_system/reports/`:

*   **Attendance Report** (`attendance_report.txt`): A text-based summary detailing presence, absence, and tardiness.
*   **Progress Report** (`progress_report.csv`): A comma-separated value file listing student grades and averages.

## Limitations & Future Improvements
While functional for its intended academic purpose, the system has identified areas for future scalability and enhancement:

*   **Concurrency**: As a synchronous CLI application, it does not support simultaneous multi-user access. Future versions could implement threading or multiprocessing.
*   **Database Integration**: Migration from flat files to a relational database management system (RDBMS) such as SQLite or PostgreSQL would enhance data relational integrity and query performance.
*   **Security Protocol**: Currently, the system uses basic credential management. Integrating robust hashing algorithms (e.g., bcrypt) and a secure session management system would significantly improve security.
*   **Web Interface**: Transitioning the UI to a web-based framework (e.g., FastAPI or Django) would improve accessibility and user experience.
