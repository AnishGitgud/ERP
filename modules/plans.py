from datetime import datetime, timedelta


def get_plan_status_color(plan, plan_date):
    """Get color indicator for plan based on status and time"""
    current_date = datetime.now().date()
    
    # lmao traffic light
    if plan["status"] == "completed":
        return "🟢"  # Green for completed
    elif plan_date > current_date:
        return "🟡"
    else:
        return "🔴"
    
def calculate_week_dates(course_start_date, week_number):
    """Calculate start and end dates for a given week number"""
    start_date = datetime.strptime(course_start_date, "%Y-%m-%d")
    week_start = start_date + timedelta(days=(week_number - 1) * 7)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end

def get_course_weeks(course_start_date, course_end_date):
    """Get all available weeks for a course"""
    start_date = datetime.strptime(course_start_date, "%Y-%m-%d")
    end_date = datetime.strptime(course_end_date, "%Y-%m-%d")
    
    weeks = []
    current_week_start = start_date
    week_number = 1
    
    while current_week_start <= end_date:
        week_end = current_week_start + timedelta(days=6)
        if week_end > end_date:
            week_end = end_date
            
        weeks.append({
            "number": week_number,
            "start": current_week_start.strftime("%Y-%m-%d"),
            "end": week_end.strftime("%Y-%m-%d")
        })
        
        current_week_start += timedelta(days=7)
        week_number += 1
        
    return weeks