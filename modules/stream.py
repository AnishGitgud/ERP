# Stream class definition - to have an instance, say animation=Stream("animation"), to manage the courses, schedule and evaluations for it.

import json
import os

from modules import storage as stg
from modules import schedule as sch

class Stream:
    def __init__(self, stream_name: str):
        self.stream_name = stream_name
        self._initialize_if_not_exists()

    def __repr__(self):
        return f"Stream(stream_name={self.stream_name})"
    
    def _initialize_if_not_exists(self):
        """Create a new stream if it doesn't exist."""
        streams_data = stg.load_streams()
        if self.stream_name not in streams_data["streams"]:
            stg.add_stream(self.stream_name)
            print(f"Stream '{self.stream_name}' created.")


    # Courses management methods
    def get_courses(self):
        """Get courses for the stream"""
        courses = stg.get_stream_courses(self.stream_name)
        if not courses:
            return {"message": f"No courses in stream {self.stream_name} yet."}
        return courses

    def add_course(self, course_name: str, description: str = ""):
        """Add a course to the stream"""
        courses_data = stg.load_courses()
        if self.stream_name not in courses_data["courses"]:
            courses_data["courses"][self.stream_name] = {}
        
        courses_data["courses"][self.stream_name][course_name] = {
            "description": description,
            "schedule": {},
            "evaluations": {},
            "created": stg.datetime.now().isoformat()
        }
        stg.save_courses(courses_data)
        return f"Course '{course_name}' added to stream '{self.stream_name}'"

    def remove_course(self, course_name: str):
        """Remove a course from the stream"""
        courses_data = stg.load_courses()
        if (self.stream_name in courses_data["courses"] and 
            course_name in courses_data["courses"][self.stream_name]):
            del courses_data["courses"][self.stream_name][course_name]
            stg.save_courses(courses_data)
            return f"Course '{course_name}' removed from stream '{self.stream_name}'"
        return f"Course '{course_name}' not found in stream '{self.stream_name}'"


    # Schedule management methods
    def add_course_schedule(self, course_name: str, start_date: str, duration_months: int = 1):
        """Add schedule to a course in this stream"""
        return sch.add_course_schedule(self.stream_name, course_name, start_date, duration_months)

    def update_course_end_date(self, course_name: str, new_end_date: str):
        """Update end date for a course in this stream"""
        return sch.update_course_end_date(self.stream_name, course_name, new_end_date)

    def get_course_schedule(self, course_name: str):
        """Get schedule for a specific course in this stream"""
        return sch.get_course_schedule(self.stream_name, course_name)

    def update_weekly_task(self, course_name: str, week_key: str, day: str, task: str):
        """Update a weekly task for a course"""
        return sch.update_weekly_task(self.stream_name, course_name, week_key, day, task)