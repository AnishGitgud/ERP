"""
Schedule management module for courses with plan-based system.
Handles course scheduling with start/end dates and plan management.
"""

from datetime import datetime, timedelta
import json
import os
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
                "duration_months": duration_months
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
            stg.save_courses(courses_data)
            return f"End date updated for {course_name}: {new_end_date}"
        else:
            return f"Schedule not found for {course_name} in stream {stream_name}"
            
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD"

def get_course_schedule(stream_name, course_name):
    """Get the complete schedule for a course"""
    courses_data = stg.load_courses()
    
    if (stream_name in courses_data["courses"] and 
        course_name in courses_data["courses"][stream_name] and
        "schedule" in courses_data["courses"][stream_name][course_name]):
        
        return courses_data["courses"][stream_name][course_name]["schedule"]
    
    return None

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