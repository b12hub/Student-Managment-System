import os
import csv

def generate_attendance_report(attendance_records: list, output_path: str = "reports/attendance_report.txt"):
    """
    Generate a human-readable attendance report.
    Args:
        attendance_records (list): List of attendance dictionaries.
        output_path (str): Path to save the report.
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Process data: Group by student
    student_stats = {}
    for record in attendance_records:
        sid = record.get('student_id')
        status = record.get('status')
        
        if sid not in student_stats:
            student_stats[sid] = {'total': 0, 'present': 0}
            
        student_stats[sid]['total'] += 1
        if status == 'P':
            student_stats[sid]['present'] += 1
            
    # Write report
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

def generate_progress_report(grades: list, output_path: str = "reports/progress_report.csv"):
    """
    Generate a CSV progress report.
    Args:
        grades (list): List of grade dictionaries.
        output_path (str): Path to save the report.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Process data: Average grade per student
    student_grades = {} # {sid: [percentages]}
    
    for g in grades:
        sid = g.get('student_id')
        score = float(g.get('score', 0))
        max_score = float(g.get('max_score', 100))
        
        perc = (score / max_score * 100) if max_score > 0 else 0
        
        if sid not in student_grades:
            student_grades[sid] = []
        student_grades[sid].append(perc)
        
    # Write CSV
    try:
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Student ID', 'Average Grade', 'Risk Level'])
            
            for sid, percs in student_grades.items():
                avg = sum(percs) / len(percs) if percs else 0
                
                risk = "OK"
                if avg < 60:
                    risk = "Critical"
                elif avg < 75:
                    risk = "Moderate"
                    
                writer.writerow([sid, f"{avg:.2f}", risk])
        return True
    except IOError:
        return False
