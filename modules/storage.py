"""
Functional module for managing storage operations.
Uses two json files for stream info and courses info.
"""

import json
import os
from datetime import datetime

DATA_DIR = "data"   # Directory to store data files
STREAMS_FILE = os.path.join(DATA_DIR, "streams.json")  # File to store stream info
COURSES_FILE = os.path.join(DATA_DIR, "courses.json")  # File to store course info


# ensure the data directory exists
def ensure_data_dir():
    """Ensure the data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)

def load_streams():
    """Load ze streams from ze json file."""
    ensure_data_dir()
    if not os.path.exists(STREAMS_FILE):
        default_data = {
            "streams": {},
            "last_updated": datetime.now().isoformat()
        }
        save_streams(default_data)
    
    with open(STREAMS_FILE, 'r') as file:
        return json.load(file)

def save_streams(data):
    """save stream metadata"""
    ensure_data_dir()
    data["last_updated"] = datetime.now().isoformat()
    with open(STREAMS_FILE, 'w') as file:
        json.dump(data, file, indent=2)

def load_courses():
    """load all courses"""
    ensure_data_dir()
    if not os.path.exists(COURSES_FILE):
        default_courses = {
            "courses": {},
            "last_updated": datetime.now().isoformat()
        }
        save_courses(default_courses)

    with open(COURSES_FILE, 'r') as file:
        return json.load(file)
    
def save_courses(data):
    """save all courses data"""
    ensure_data_dir()
    data["last_updated"] = datetime.now().isoformat()
    with open(COURSES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_stream_courses(stream_name):
    """Get courses for a specific stream"""
    courses_data = load_courses()
    return courses_data["courses"].get(stream_name, {})

def add_stream(stream_name, description=""):
    """Add a new stream"""
    streams_data = load_streams()
    streams_data["streams"][stream_name] = {
        "description": description,
        "created": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    save_streams(streams_data)
    
    # Initialize empty courses for this stream
    courses_data = load_courses()
    if stream_name not in courses_data["courses"]:
        courses_data["courses"][stream_name] = {}
        save_courses(courses_data)

def remove_stream(stream_name):
    """Remove a stream and its courses"""
    streams_data = load_streams()
    if stream_name in streams_data["streams"]:
        del streams_data["streams"][stream_name]
        save_streams(streams_data)
    
    courses_data = load_courses()
    if stream_name in courses_data["courses"]:
        del courses_data["courses"][stream_name]
        save_courses(courses_data)

# Evaluation storage functions
EVALUATIONS_FILE = os.path.join(DATA_DIR, "evaluations.json")

def load_evaluations():
    """Load all evaluations data"""
    ensure_data_dir()
    if not os.path.exists(EVALUATIONS_FILE):
        default_evaluations = {
            "evaluations": {},  # {stream_name: {course_name: {main_evals: {}, additional_evals: {}}}}
            "last_updated": datetime.now().isoformat()
        }
        save_evaluations(default_evaluations)
        return default_evaluations
    
    with open(EVALUATIONS_FILE, 'r') as f:
        return json.load(f)

def save_evaluations(data):
    """Save all evaluations data"""
    ensure_data_dir()
    data["last_updated"] = datetime.now().isoformat()
    with open(EVALUATIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_course_evaluations(stream_name, course_name):
    """Get evaluations for a specific course"""
    evals_data = load_evaluations()
    return evals_data["evaluations"].get(stream_name, {}).get(course_name, {
        "main_evals": {
            "weekend_eval": [],
            "monthly_project": [],
            "catalogue": [],
            "notes": []
        },
        "additional_evals": {
            "off_time": [],
            "commissions": [],
            "post_reviews": [],
            "portfolio": []
        }
    })

def add_evaluation(stream_name, course_name, eval_type, eval_category, eval_data):
    """Add an evaluation entry"""
    evals_data = load_evaluations()
    
    if stream_name not in evals_data["evaluations"]:
        evals_data["evaluations"][stream_name] = {}
    if course_name not in evals_data["evaluations"][stream_name]:
        evals_data["evaluations"][stream_name][course_name] = {
            "main_evals": {"weekend_eval": [], "monthly_project": [], "catalogue": [], "notes": []},
            "additional_evals": {"off_time": [], "commissions": [], "post_reviews": [], "portfolio": []}
        }
    
    eval_entry = {
        "id": len(evals_data["evaluations"][stream_name][course_name][eval_type][eval_category]) + 1,
        "submitted_date": datetime.now().isoformat(),
        "status": "pending",
        **eval_data
    }
    
    evals_data["evaluations"][stream_name][course_name][eval_type][eval_category].append(eval_entry)
    save_evaluations(evals_data)
    return eval_entry["id"]

def update_evaluation_review(stream_name, course_name, eval_type, eval_category, eval_id, review_data):
    """Update evaluation with review and grade"""
    evals_data = load_evaluations()
    for eval_entry in evals_data["evaluations"][stream_name][course_name][eval_type][eval_category]:
        if eval_entry["id"] == eval_id:
            eval_entry.update({
                "status": "reviewed",
                "reviewed_date": datetime.now().isoformat(),
                **review_data
            })
            save_evaluations(evals_data)
            return True
    return False