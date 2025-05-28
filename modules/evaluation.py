"""evaluation calculation methods here."""

MAIN_COMPONENT_WEIGHTS = {
    "weekend_eval": 30,    # M1: 30% of course
    "monthly_project": 20, # M2: 20% of course
    "catalogue": 20,       # M3: 20% of course
    "notes": 20           # M4: 20% of course
}

ADDITIONAL_COMPONENT_POINTS = {
    "off_time": 1,        # A1: 1 point (1% of course)
    "commissions": 4,     # A2: 4 points (4% of course)
    "post_reviews": 2,    # A3: 2 points (2% of course)
    "portfolio": 3        # A4: 3 points (3% of course)
}

GRADE_TO_SCORE_MAP = {
    "A": 5, "B": 4, "C": 3, "D": 2, "E": 1, "F": 0
}

SCORE_TO_GRADE_MAP = {
    (90, 100): "A",
    (70, 90): "B", 
    (50, 70): "C",
    (30, 50): "D",
    (20, 30): "E",
    (0, 20): "F"
}


# - Get all evaluations for the course from the evaluation json file - if nothing in a field - it is an automatic 'F'(score=0)
# -> dict of all component : 'each submission : grade'
def get_course_evaluations(stream_name, course_name):
    """
    Get all evaluations for the course from the evaluation json file
    Returns dict of all component : [submissions with grades]
    If nothing in a field - it is an automatic 'F'(score=0)
    """
    from modules.storage import load_evaluations

    evals_data = load_evaluations()
    course_evals = evals_data["evaluations"].get(stream_name, {}).get(course_name, {
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

    # Combine all components into a single dict
    all_components = {}

    # Add main evaluations
    for component, submissions in course_evals["main_evals"].items():
        all_components[component] = submissions
    
    # Add additional evaluations
    for component, submissions in course_evals["additional_evals"].items():
        all_components[component] = submissions
    
    return all_components

# -> above returned dict but score instead of grade
def grade_to_score(course_evaluations):
    """
    Convert grades to scores for all evaluations
    Returns dict of all component : [submissions with scores instead of grades]
    """
    scored_evaluations = {}

    for component, submissions in course_evaluations.items():
        scored_submissions = []
        
        for submission in submissions:
            # Only include reviewed submissions with grades
            if submission.get("status") == "reviewed" and submission.get("grade"):
                score = GRADE_TO_SCORE_MAP.get(submission["grade"], 0)
                scored_submission = submission.copy()
                scored_submission["score"] = score
                scored_submissions.append(scored_submission)
        
        scored_evaluations[component] = scored_submissions
    
    return scored_evaluations

# - Calculate average scores for each component (M1-M4, A1-A4)
# -> dict of all component averages
def calculate_averages(scored_evaluations):
    """
    Calculate average scores for each component (M1-M4, A1-A4)
    Returns dict of all component averages
    If no submissions, component gets score of 0 (equivalent to F)
    """
    component_averages = {}
    
    for component, submissions in scored_evaluations.items():
        if submissions:
            # Calculate average of all submission scores
            total_score = sum(sub["score"] for sub in submissions)
            average_score = total_score / len(submissions)
        else:
            # No submissions = F grade = 0 score
            average_score = 0
        
        component_averages[component] = average_score
    
    return component_averages

# - Apply component weights
# -> dict with scaled scores
def scale_score_to_percent(component_averages):
    """
    Apply component weights to scale scores to percentages
    Returns dict with scaled scores (percentages for main, points for additional)
    """
    scaled_scores = {}
    
    # Scale main components (0-5 score to 0-weight% of course)
    for component in MAIN_COMPONENT_WEIGHTS:
        avg_score = component_averages.get(component, 0)
        weight = MAIN_COMPONENT_WEIGHTS[component]
        
        # Scale from 0-5 to 0-weight%
        scaled_percentage = (avg_score / 5.0) * weight
        scaled_scores[component] = scaled_percentage
    
    # Scale additional components (0-5 score to 0-max_points of course)
    for component in ADDITIONAL_COMPONENT_POINTS:
        avg_score = component_averages.get(component, 0)
        max_points = ADDITIONAL_COMPONENT_POINTS[component]
        
        # Scale from 0-5 to 0-max_points
        scaled_points = (avg_score / 5.0) * max_points
        scaled_scores[component] = scaled_points
    
    return scaled_scores

# - Return final percentage and letter grade
# -> final percent value - return that
def calculate_course_score(stream_name, course_name):
    """
    Calculate final course score and letter grade
    Returns dict with final percentage, letter grade, and component breakdown
    """
    try:
        # Step 1: Get all evaluations
        course_evaluations = get_course_evaluations(stream_name, course_name)
        
        # Step 2: Convert grades to scores
        scored_evaluations = grade_to_score(course_evaluations)
        
        # Step 3: Calculate averages for each component
        component_averages = calculate_averages(scored_evaluations)
        
        # Step 4: Scale scores to percentages/points
        scaled_scores = scale_score_to_percent(component_averages)
        
        # Step 5: Calculate final percentage
        final_percentage = sum(scaled_scores.values())
        
        # Step 6: Determine letter grade
        letter_grade = get_letter_grade(final_percentage)
        
        # Step 7: Prepare detailed breakdown
        main_breakdown = {}
        additional_breakdown = {}
        
        for component in MAIN_COMPONENT_WEIGHTS:
            main_breakdown[component] = {
                "average_score": component_averages.get(component, 0),
                "scaled_percentage": scaled_scores.get(component, 0),
                "weight": MAIN_COMPONENT_WEIGHTS[component],
                "submissions_count": len(scored_evaluations.get(component, []))
            }
        
        for component in ADDITIONAL_COMPONENT_POINTS:
            additional_breakdown[component] = {
                "average_score": component_averages.get(component, 0),
                "scaled_points": scaled_scores.get(component, 0),
                "max_points": ADDITIONAL_COMPONENT_POINTS[component],
                "submissions_count": len(scored_evaluations.get(component, []))
            }
        
        return {
            "final_percentage": round(final_percentage, 2),
            "letter_grade": letter_grade,
            "main_components": main_breakdown,
            "additional_components": additional_breakdown,
            "total_main_percentage": sum(scaled_scores.get(comp, 0) for comp in MAIN_COMPONENT_WEIGHTS),
            "total_additional_points": sum(scaled_scores.get(comp, 0) for comp in ADDITIONAL_COMPONENT_POINTS)
        }
        
    except Exception as e:
        return {
            "error": f"Error calculating course score: {str(e)}",
            "final_percentage": 0,
            "letter_grade": "F"
        }



# more functions for letter grade assignment and detailed statistics
def get_letter_grade(percentage):
    """Convert percentage to letter grade A-F"""
    for (min_score, max_score), grade in SCORE_TO_GRADE_MAP.items():
        if min_score < percentage <= max_score:
            return grade
    
    # Handle edge case for exactly 100%
    if percentage == 100:
        return "A"
    elif percentage == 0:
        return "F"

def get_component_statistics(stream_name, course_name):
    """
    Get detailed statistics for each component
    Useful for debugging and detailed analysis
    """
    course_evaluations = get_course_evaluations(stream_name, course_name)
    scored_evaluations = grade_to_score(course_evaluations)
    
    stats = {}
    
    for component, submissions in scored_evaluations.items():
        if submissions:
            scores = [sub["score"] for sub in submissions]
            stats[component] = {
                "count": len(scores),
                "scores": scores,
                "average": sum(scores) / len(scores),
                "min": min(scores),
                "max": max(scores),
                "grades": [sub["grade"] for sub in submissions]
            }
        else:
            stats[component] = {
                "count": 0,
                "scores": [],
                "average": 0,
                "min": 0,
                "max": 0,
                "grades": []
            }
    
    return stats