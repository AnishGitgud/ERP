"""
Schedule management module for courses.
Handles course scheduling with start/end dates and weekly schedule views.
"""

from datetime import datetime, timedelta
import calendar
from modules import storage as stg

def add_course_schedule(stream_name, course_name, start_date, duration_months=1):
    """
    Add schedule to a course with start date and automatic end date calculation
    
    Args:
        stream_name: Name of the stream
        course_name: Name of the course
        start_date: Start date as string (YYYY-MM-DD)
        duration_months: Duration in months (default 1)
    """
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        # Calculate end date by adding months
        if start_dt.month + duration_months <= 12:
            end_dt = start_dt.replace(month=start_dt.month + duration_months)
        else:
            end_dt = start_dt.replace(
                year=start_dt.year + 1, 
                month=(start_dt.month + duration_months) - 12
            )
        
        # Load courses data
        courses_data = stg.load_courses()
        
        if (stream_name in courses_data["courses"] and 
            course_name in courses_data["courses"][stream_name]):
            
            courses_data["courses"][stream_name][course_name]["schedule"] = {
                "start_date": start_date,
                "end_date": end_dt.strftime("%Y-%m-%d"),
                "duration_months": duration_months,
                "weekly_schedule": initialize_weekly_schedule(start_dt, end_dt)
            }
            stg.save_courses(courses_data)
            return f"Schedule added for {course_name}: {start_date} to {end_dt.strftime('%Y-%m-%d')}"
        else:
            return f"Course {course_name} not found in stream {stream_name}"
            
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD"

def update_course_end_date(stream_name, course_name, new_end_date):
    """Update the end date of a course schedule"""
    try:
        datetime.strptime(new_end_date, "%Y-%m-%d")  # Validate date format
        
        courses_data = stg.load_courses()
        
        if (stream_name in courses_data["courses"] and 
            course_name in courses_data["courses"][stream_name] and
            "schedule" in courses_data["courses"][stream_name][course_name]):
            
            courses_data["courses"][stream_name][course_name]["schedule"]["end_date"] = new_end_date
            
            # Recalculate weekly schedule with new end date
            start_date = courses_data["courses"][stream_name][course_name]["schedule"]["start_date"]
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(new_end_date, "%Y-%m-%d")
            
            courses_data["courses"][stream_name][course_name]["schedule"]["weekly_schedule"] = \
                initialize_weekly_schedule(start_dt, end_dt)
            
            stg.save_courses(courses_data)
            return f"End date updated for {course_name}: {new_end_date}"
        else:
            return f"Schedule not found for {course_name} in stream {stream_name}"
            
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD"

def initialize_weekly_schedule(start_date, end_date):
    """Initialize weekly schedule structure for a course duration"""
    weekly_schedule = {}
    current_date = start_date
    
    while current_date <= end_date:
        # Get week start (Monday)
        week_start = current_date - timedelta(days=current_date.weekday())
        week_key = week_start.strftime("%Y-W%U")  # Year-Week format
        
        if week_key not in weekly_schedule:
            weekly_schedule[week_key] = {
                "week_start": week_start.strftime("%Y-%m-%d"),
                "week_end": (week_start + timedelta(days=6)).strftime("%Y-%m-%d"),
                "daily_tasks": {
                    "Monday": "",
                    "Tuesday": "",
                    "Wednesday": "",
                    "Thursday": "",
                    "Friday": "",
                    "Saturday": "",
                    "Sunday": ""
                }
            }
        
        current_date += timedelta(days=7)
    
    return weekly_schedule

def get_course_schedule(stream_name, course_name):
    """Get the complete schedule for a course"""
    courses_data = stg.load_courses()
    
    if (stream_name in courses_data["courses"] and 
        course_name in courses_data["courses"][stream_name] and
        "schedule" in courses_data["courses"][stream_name][course_name]):
        
        return courses_data["courses"][stream_name][course_name]["schedule"]
    
    return None

def update_weekly_task(stream_name, course_name, week_key, day, task):
    """Update a specific day's task in the weekly schedule"""
    courses_data = stg.load_courses()
    
    if (stream_name in courses_data["courses"] and 
        course_name in courses_data["courses"][stream_name] and
        "schedule" in courses_data["courses"][stream_name][course_name]):
        
        schedule = courses_data["courses"][stream_name][course_name]["schedule"]
        if ("weekly_schedule" in schedule and 
            week_key in schedule["weekly_schedule"] and
            day in schedule["weekly_schedule"][week_key]["daily_tasks"]):
            
            schedule["weekly_schedule"][week_key]["daily_tasks"][day] = task
            stg.save_courses(courses_data)
            return f"Updated {day} task for week {week_key}"
    
    return "Failed to update task"

def get_all_scheduled_courses():
    """Get all courses that have schedules across all streams"""
    courses_data = stg.load_courses()
    scheduled_courses = {}
    
    for stream_name, courses in courses_data["courses"].items():
        for course_name, course_data in courses.items():
            if "schedule" in course_data and course_data["schedule"]:
                if stream_name not in scheduled_courses:
                    scheduled_courses[stream_name] = []
                scheduled_courses[stream_name].append(course_name)
    
    return scheduled_courses