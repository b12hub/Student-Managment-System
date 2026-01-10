import os
import csv
from datetime import datetime

def validate_date(date_str: str) -> bool:
    """
    Validate if the date string is in YYYY-MM-DD format.
    Args:
        date_str (str): The date string to validate.
    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def calculate_gpa(grades_list: list) -> float:
    """
    Calculate GPA based on a list of Grade objects or dicts.
    Assuming 4.0 scale: A=4, B=3, C=2, D=1, F=0.
    Args:
        grades_list (list): List of grade dictionaries or Grade objects.
    Returns:
        float: Calculated GPA.
    """
    if not grades_list:
        return 0.0
        
    total_points = 0.0
    count = 0
    
    for grade in grades_list:
        if isinstance(grade, dict):
             score = float(grade.get('score', 0))
             max_score = float(grade.get('max_score', 100))
             if max_score == 0:
                 percentage = 0
             else:
                 percentage = (score / max_score) * 100
        else:
            percentage = grade.calculate_percentage()
            
        points = 0.0
        if percentage >= 90:
            points = 4.0
        elif percentage >= 80:
            points = 3.0
        elif percentage >= 70:
            points = 2.0
        elif percentage >= 60:
            points = 1.0
        else:
            points = 0.0
            
        total_points += points
        count += 1
        
    return round(total_points / count, 2) if count > 0 else 0.0

def normalize_input(data: str) -> str:
    """
    Normalize input string (strip whitespace).
    Args:
        data (str): Input string.
    Returns:
        str: Normalized string.
    """
    if not data:
        return ""
    return data.strip()

def generate_attendance_report(attendance_records: list, output_path: str = "reports/attendance_report.txt") -> bool:
    """
    Generate a human-readable attendance report.
    Args:
        attendance_records (list): List of attendance dictionaries.
        output_path (str): Path to save the report.
    Returns:
        bool: True if successful, False otherwise.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    student_stats = {}
    for record in attendance_records:
        sid = record.get('student_id')
        status = record.get('status')
        
        if sid not in student_stats:
            student_stats[sid] = {'total': 0, 'present': 0}
            
        student_stats[sid]['total'] += 1
        if status == 'P':
            student_stats[sid]['present'] += 1
            
    try:
        with open(output_path, 'w') as f:
            f.write("ATTENDANCE REPORT\n")
            f.write("=================\n\n")
            f.write(f"{'Student ID':<15} | {'Total Classes':<15} | {'Present':<10} | {'Percentage':<10}\n")
            f.write("-" * 60 + "\n")
            
            for sid, stats in student_stats.items():
                total = stats['total']
                present = stats['present']
                perc = (present / total * 100) if total > 0 else 0.0
                f.write(f"{sid:<15} | {total:<15} | {present:<10} | {perc:.1f}%\n")
                
        return True
    except IOError:
        return False

def generate_progress_report(grades: list, output_path: str = "reports/progress_report.csv") -> bool:
    """
    Generate a CSV progress report.
    Args:
        grades (list): List of grade dictionaries.
        output_path (str): Path to save the report.
    Returns:
        bool: True if successful, False otherwise.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    student_grades = {} # {sid: {'weighted_sum': 0, 'total_weight': 0, 'scores': []}}
    
    for g in grades:
        sid = g.get('student_id')
        score = float(g.get('score', 0))
        max_score = float(g.get('max_score', 100))
        weight = float(g.get('weight', 0)) # Use weight if available
        
        perc = (score / max_score * 100) if max_score > 0 else 0
        
        if sid not in student_grades:
            student_grades[sid] = {'weighted_sum': 0.0, 'total_weight': 0.0, 'percentages': []}
        
        student_grades[sid]['percentages'].append(perc)
        
        # Weighted logic
        if weight > 0:
            student_grades[sid]['weighted_sum'] += perc * weight
            student_grades[sid]['total_weight'] += weight
        
    try:
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Student ID', 'Average Grade', 'Risk Level'])
            
            for sid, data in student_grades.items():
                avg = 0.0
                if data['total_weight'] > 0:
                    avg = data['weighted_sum'] / data['total_weight']
                elif data['percentages']:
                    avg = sum(data['percentages']) / len(data['percentages'])
                
                risk = "OK"
                if avg < 60:
                    risk = "Critical"
                elif avg < 75:
                    risk = "Moderate"
                    
                writer.writerow([sid, f"{avg:.2f}", risk])
        return True
    except IOError:
        return False
