"""
Course schedular, evaluation, sem management, history cataloguing and post managemnt system
for my goals - you know which one. Basically erp but better. Store data in text/json/xml idk, not decided yet.

main page for the project with subpages-
1 - Course schedule - week view and day view with editable entry to track progress
                    - dynamic view for daily design
2 - Evaluation - track progress of each course, with grading system and comments
               - editable entries to submit work/projects and review for grading
3 - Semester management - manage semester details, course registration, and deadlines
4 - History cataloguing - maintain a history of courses taken, grades received, and comments
5 - Post management - manage posts on reddit/yt and track engagement and feedback
"""

# print("You ain't killing yourself yet my boy.")
# print("Nor are you giving in to others.")
# print("Starve and you will live.")

import streamlit as std
import pandas as pd
from datetime import datetime, timedelta

from modules.stream import Stream

from modules import storage as stg
from modules import schedule as sch
from modules import plans as pln
from modules.evaluation import ADDITIONAL_COMPONENT_POINTS, MAIN_COMPONENT_WEIGHTS

std.set_page_config(
    layout="wide",
)



### Initialize session state variables
def initialize_session():
    """Initialize session state variables if not already set."""
    if 'initialized' not in std.session_state:
        std.session_state.initialized = True
        std.session_state.streams = []  # List to hold Stream instances
        std.session_state.current_stream = None  # Currently selected stream
        std.session_state.page = "home"  # Current page in the app




### Functions
def go_home():
    std.session_state.page = "home"

def load_streams_from_file(filepath="data/streams.json"):
    """Load streams from the JSON file and return a list of Stream instances."""
    streams_data = stg.load_streams()
    return [Stream(name) for name in streams_data["streams"].keys()]




### Evaluation Page Functions
def show_evaluation_page():
    """Main evaluation page with stream and course selection"""
    if std.button("🏠 Home", type="primary"):
        go_home()

    std.write("### Evaluation System")
    
    # Load streams and courses
    streams_data = stg.load_streams()
    courses_data = stg.load_courses()
    
    if not streams_data["streams"]:
        std.warning("No streams found. Please create a stream firstd.")
        return
    
    # Stream selection
    stream_names = list(streams_data["streams"].keys())
    selected_stream = std.selectbox("Select Stream", stream_names)
    
    # Course selection
    stream_courses = courses_data["courses"].get(selected_stream, {})
    if not stream_courses:
        std.warning(f"No courses found in stream '{selected_stream}'. Please add courses firstd.")
        return
    
    course_names = list(stream_courses.keys())
    selected_course = std.selectbox("Select Course", course_names)
    
    if selected_stream and selected_course:
        show_evaluation_tables(selected_stream, selected_course)

def show_evaluation_tables(stream_name, course_name):
    """Show main and additional evaluation tables"""
    std.write(f"#### Evaluations for {course_name} ({stream_name})")
    
    # Get evaluations data
    evaluations = stg.get_course_evaluations(stream_name, course_name)
    
    # Get course evaluation
    evaluated_course = stg.calculate_course_score(stream_name, course_name)

    # Create two columns for the tables
    col1, col2 = std.columns(2)
    
    with col1:
        std.write("##### Main Evaluations")
        show_main_evaluations(stream_name, course_name, evaluations["main_evals"])
    
    with col2:
        std.write("##### Additional Evaluations")
        show_additional_evaluations(stream_name, course_name, evaluations["additional_evals"])

    std.markdown('---')
    std.markdown(f"## Course Statistics for {course_name}")
    
    # Course overview in columns
    col1, col2 = std.columns(2)
    with col1:
        std.metric("Course Grade", evaluated_course.get('letter_grade'))
    with col2:
        std.metric("Course Score", f"{evaluated_course.get('final_percentage')}%")
    
    # Main Components Table with individual progress bars
    std.markdown("### 📚 Main Components")
    main_evals = evaluated_course.get("main_components", {})
    
    if main_evals:
        for component_name, component_data in main_evals.items():
            max_weight = MAIN_COMPONENT_WEIGHTS.get(component_name, 20)
            current_score = component_data.get('scaled_percentage', 0)
            submissions = component_data.get('submissions_count', 0)
            
            col1, col2, col3 = std.columns([2, 3, 1])
            with col1:
                std.write(f"**{component_name.replace('_', ' ').title()}**")
            with col2:
                # Custom progress bar with individual max
                progress = min(current_score / max_weight, 1.0) if max_weight > 0 else 0
                std.progress(progress)
                std.caption(f"{current_score:.1f}% / {max_weight}% max")
            with col3:
                std.metric("Submissions", submissions)
    
    # Additional Components Table with individual progress bars
    std.markdown("### ➕ Additional Components")
    add_evals = evaluated_course.get("additional_components", {})
    
    if add_evals:
        for component_name, component_data in add_evals.items():
            max_points = ADDITIONAL_COMPONENT_POINTS.get(component_name, 1)
            current_score = component_data.get('scaled_points', 0)
            submissions = component_data.get('submissions_count', 0)
            
            col1, col2, col3 = std.columns([2, 3, 1])
            with col1:
                std.write(f"**{component_name.replace('_', ' ').title()}**")
            with col2:
                # Custom progress bar with individual max
                progress = min(current_score / max_points, 1.0) if max_points > 0 else 0
                std.progress(progress)
                std.caption(f"{current_score:.1f}% / {max_points}% max")
            with col3:
                std.metric("Submissions", submissions)

    std.markdown('---')
    std.markdown("### Component Weigths & Grading System")
    std.markdown("### ")
    std.markdown("##### Component Weigths")
    std.markdown('---')
    c1, c2, c3, c4, c5 = std.columns(5)
    with c1:
        std.caption("### Main evaluations")
        std.caption("#### (90% of course)")
    with c2:
        std.caption("#### Weekly Eval(M1)")
        std.write("##### ")
        std.caption("30% of Course")
    with c3:
        std.caption("#### Monthly Project(M2)")
        std.write("##### ")
        std.caption("20% of Course")
    with c4:
        std.caption("#### Catalogue(M3)")
        std.write("##### ")
        std.caption("20% of Course")
    with c5:
        std.caption("#### Notes(M4)")
        std.write("##### ")
        std.caption("20% of Course")

    std.markdown('---')

    c1, c2, c3, c4, c5 = std.columns(5)
    with c1:
        std.caption("### Additional evaluations")
        std.caption("#### (1 point = 1% of course)")
        std.caption("#### (10% of course)")
    with c2:
        std.caption("#### Off Time(A1)")
        std.write("##### ")
        std.caption("1 point")
    with c3:
        std.caption("#### Commissions(A2)")
        std.write("##### ")
        std.caption("4 points")
    with c4:
        std.caption("#### Post reviews(A3)")
        std.write("##### ")
        std.caption("2 points")
    with c5:
        std.caption("#### Portfolio(A4)")
        std.write("##### ")
        std.caption("3 points")

    std.markdown('---')

    std.markdown("### ")
    std.markdown("##### Grading System")
    std.markdown('---')
    std.caption("### Six grade system for each component(Mi and Ai) : A(5), B(4), C(3), D(2), E(1), F(0)")
    std.caption("### Each component can have multiple submissions - take average grade(A-F) and score(5.0 - 1.0) for a component(each Mi and Ai)")
    std.caption("### Scale score of a component to total scale 0-100% for the course. Breakdown -")
    std.caption("#### Mi : Scale component average score(0.0 - 5.0) and scale to component percent((0 - 30%) for M1 and (0 - 20%) for other Mi)")
    std.caption("#### Ai : Scale component average score to specific component points. Example A4 -")
    c1, c2, c3, c4, c5 = std.columns(5)
    with c2:
        std.caption("#### A4 score achieved = 4.5 out of 5")
        std.caption("#### A4 max points = 3, Scale 0-5 to 0-3")
        std.caption("#### Avg A4 point achieved = 4.5 * (3 - 0)/(5 - 0) = 2.7, A4 component = 2.7%")
    std.caption("#### Add up all Mi and Ai percentages to get final course percentage out of 100%. Final course grade distribution:")
    c1, c2, c3, c4, c5 = std.columns(5)
    with c2:
        std.caption("#### A - [100-90%)")
        std.caption("#### B - [90-70%)")
        std.caption("#### C - [70-50%)")
        std.caption("#### D - [50-30%)")
        std.caption("#### E - [30-20%)")
        std.caption("#### F - [20 -0%]")

def show_main_evaluations(stream_name, course_name, main_evals):
    """Show main evaluations with tabs"""
    tab1, tab2, tab3, tab4 = std.tabs(["Weekend Eval", "Monthly Project", "Catalogue", "Notes"])
    
    with tab1:
        show_evaluation_tab(stream_name, course_name, "main_evals", "weekend_eval", 
                           main_evals["weekend_eval"], "Weekend Evaluation")
    
    with tab2:
        show_evaluation_tab(stream_name, course_name, "main_evals", "monthly_project", 
                           main_evals["monthly_project"], "Monthly Project")
    
    with tab3:
        show_evaluation_tab(stream_name, course_name, "main_evals", "catalogue", 
                           main_evals["catalogue"], "Catalogue")
    
    with tab4:
        show_evaluation_tab(stream_name, course_name, "main_evals", "notes", 
                           main_evals["notes"], "Notes")

def show_additional_evaluations(stream_name, course_name, additional_evals):
    """Show additional evaluations with tabs"""
    tab1, tab2, tab3, tab4 = std.tabs(["Off Time", "Commissions", "Post Reviews", "Portfolio"])
    
    with tab1:
        show_evaluation_tab(stream_name, course_name, "additional_evals", "off_time", 
                           additional_evals["off_time"], "Off Time Work")
    
    with tab2:
        show_evaluation_tab(stream_name, course_name, "additional_evals", "commissions", 
                           additional_evals["commissions"], "Commissions/Sponsored")
    
    with tab3:
        show_evaluation_tab(stream_name, course_name, "additional_evals", "post_reviews", 
                           additional_evals["post_reviews"], "Post Reviews/Reception")
    
    with tab4:
        show_evaluation_tab(stream_name, course_name, "additional_evals", "portfolio", 
                           additional_evals["portfolio"], "Portfolio/Resume Upskill")

def show_evaluation_tab(stream_name, course_name, eval_type, eval_category, eval_data, tab_title):
    """Show individual evaluation tab with submissions and review options"""
    
    # Add new submission form
    with std.expander(f"➕ Add New {tab_title}"):
        add_evaluation_form(stream_name, course_name, eval_type, eval_category, tab_title)
    
    # Display existing evaluations
    if eval_data:
        std.write(f"**Submitted {tab_title}:**")
        
        for eval_entry in eval_data:
            with std.container():
                col1, col2, col3 = std.columns([3, 1, 1])
                
                with col1:
                    std.write(f"**{eval_entry.get('title', 'Untitled')}**")
                    std.write(f"*Submitted:* {eval_entry['submitted_date'][:10]}")
                    if eval_entry.get('description'):
                        std.write(f"*Description:* {eval_entry['description']}")
                
                with col2:
                    status_color = "🟡" if eval_entry['status'] == "pending" else "🟢"
                    std.write(f"{status_color} {eval_entry['status'].title()}")
                    if eval_entry.get('grade'):
                        std.write(f"**Grade:** {eval_entry['grade']}")
                    if eval_entry.get('review_comments'):
                        std.write(f"**Review Comments:** {eval_entry['review_comments']}")
                    if eval_entry.get('feedback'):
                        std.write(f"**Feedback:** {eval_entry['feedback']}")
                
                with col3:
                    # Create unique button key
                    button_key = f"review_btn_{stream_name}_{course_name}_{eval_category}_{eval_entry['id']}"
                    if std.button(f"Review", key=button_key):
                        # Store the evaluation to review in session state
                        std.session_state[f"reviewing_{button_key}"] = eval_entry
                        std.rerun()
                
                # Check if this evaluation is being reviewed
                review_session_key = f"reviewing_review_btn_{stream_name}_{course_name}_{eval_category}_{eval_entry['id']}"
                if review_session_key in std.session_state:
                    show_review_form(stream_name, course_name, eval_type, eval_category, eval_entry)
                    # Add a button to close the review form
                    if std.button(f"Close Review", key=f"close_{button_key}"):
                        del std.session_state[review_session_key]
                        std.rerun()
                
                std.divider()
    else:
        std.info(f"No {tab_title.lower()} submissions yet.")

def add_evaluation_form(stream_name, course_name, eval_type, eval_category, tab_title):
    """Form to add new evaluation submission"""
    with std.form(f"add_{eval_category}"):
        title = std.text_input("Title*")
        description = std.text_area("Description")
        
        # Category-specific fields
        if eval_category in ["weekend_eval", "monthly_project"]:
            project_link = std.text_input("Project Link/File Path")
            difficulty = std.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Expert"])
            time_spent = std.number_input("Time Spent (hours)", min_value=0.0, step=0.5)
        elif eval_category == "catalogue":
            content_type = std.selectbox("Content Type", ["Article", "Tutorial", "Reference", "Documentation"])
            source_link = std.text_input("Source Link")
        elif eval_category == "notes":
            topic = std.text_input("Topic")
            note_type = std.selectbox("Note Type", ["Lecture", "Reading", "Practice", "Research"])
        elif eval_category == "commissions":
            client = std.text_input("Client/Platform")
            payment = std.number_input("Payment Amount", min_value=0.0)
            deadline = std.date_input("Deadline")
        elif eval_category == "post_reviews":
            platform = std.selectbox("Platform", ["Reddit", "YouTube", "Blog", "Social Media", "Other"])
            engagement_metrics = std.text_input("Engagement Metrics (views, likes, etc.)")
        elif eval_category == "portfolio":
            skill_area = std.text_input("Skill Area")
            portfolio_link = std.text_input("Portfolio/Resume Link")
        
        submitted = std.form_submit_button("Submit")
        
        if submitted and title:
            eval_data = {
                "title": title,
                "description": description
            }
            
            # Add category-specific data
            if eval_category in ["weekend_eval", "monthly_project"]:
                eval_data.update({
                    "project_link": project_link,
                    "difficulty": difficulty,
                    "time_spent": time_spent
                })
            elif eval_category == "catalogue":
                eval_data.update({
                    "content_type": content_type,
                    "source_link": source_link
                })
            elif eval_category == "notes":
                eval_data.update({
                    "topic": topic,
                    "note_type": note_type
                })
            elif eval_category == "commissions":
                eval_data.update({
                    "client": client,
                    "payment": payment,
                    "deadline": str(deadline)
                })
            elif eval_category == "post_reviews":
                eval_data.update({
                    "platform": platform,
                    "engagement_metrics": engagement_metrics
                })
            elif eval_category == "portfolio":
                eval_data.update({
                    "skill_area": skill_area,
                    "portfolio_link": portfolio_link
                })
            
            eval_id = stg.add_evaluation(stream_name, course_name, eval_type, eval_category, eval_data)
            std.success(f"{tab_title} submitted successfully! (ID: {eval_id})")
            std.rerun()

def show_review_form(stream_name, course_name, eval_type, eval_category, eval_entry):
    """Show review and grading form"""
    std.write(f"### Reviewing: {eval_entry['title']}")
    
    # Create unique form key to avoid conflicts
    form_key = f"review_form_{stream_name}_{course_name}_{eval_type}_{eval_category}_{eval_entry['id']}"
    
    # Display evaluation details for context
    with std.expander("Evaluation Details", expanded=True):
        std.write(f"**Title:** {eval_entry['title']}")
        std.write(f"**Description:** {eval_entry.get('description', 'No description')}")
        std.write(f"**Submitted:** {eval_entry['submitted_date'][:10]}")
        std.write(f"**Status:** {eval_entry['status']}")
        
        # Show category-specific details
        if eval_category in ["weekend_eval", "monthly_project"]:
            if eval_entry.get('project_link'):
                std.write(f"**Project Link:** {eval_entry['project_link']}")
            if eval_entry.get('difficulty'):
                std.write(f"**Difficulty:** {eval_entry['difficulty']}")
            if eval_entry.get('time_spent'):
                std.write(f"**Time Spent:** {eval_entry['time_spent']} hours")
        elif eval_category == "catalogue":
            if eval_entry.get('content_type'):
                std.write(f"**Content Type:** {eval_entry['content_type']}")
            if eval_entry.get('source_link'):
                std.write(f"**Source Link:** {eval_entry['source_link']}")
        elif eval_category == "notes":
            if eval_entry.get('topic'):
                std.write(f"**Topic:** {eval_entry['topic']}")
            if eval_entry.get('note_type'):
                std.write(f"**Note Type:** {eval_entry['note_type']}")
    
    # Review form for both main and additional evaluatives(base grade that can be converted to evaluative specific score)
    with std.form(form_key):
        grade = std.selectbox("Grade", ["A", "B", "C", "D", "E","F"], key=f"grade_{form_key}")
        review_comments = std.text_area("Review Comments", key=f"comments_{form_key}")
        feedback = std.text_area("Feedback for Improvement", key=f"feedback_{form_key}")
        
        submitted = std.form_submit_button("Submit Review")
        
        if submitted:
            # Validate inputs
            if not grade:
                std.error("Please select a grade")
                return
            
            review_data = {
                "grade": grade,
                "review_comments": review_comments,
                "feedback": feedback
            }
            
            try:
                success = stg.update_evaluation_review(
                    stream_name, course_name, eval_type, eval_category, 
                    eval_entry['id'], review_data
                )
                
                if success:
                    std.success("Review submitted successfully!")
                    # Add a small delay to show the success message
                    import time
                    time.sleep(2)
                    std.rerun()
                else:
                    std.error("Failed to submit review. Please check the console for errors.")
                    
            except Exception as e:
                std.error(f"Error submitting review: {str(e)}")
                std.write(f"DEBUG: Exception details: {e}")


### Weekly Schedule Page Functions
def show_weekly_schedule_page():
    # Page header with home button
    col1, col2 = std.columns([2, 3])
    with col1:
        if std.button("🏠 Home", type="primary"):
            go_home()
    
    with col2:
        std.title("📅 Weekly Schedule")
    
    # Get all streams and courses
    courses_data = stg.load_courses()
    
    if not courses_data["courses"]:
        std.error("No streams or courses found. Please create streams and courses first.")
        return
    
    # Stream and Course selection
    col1, col2 = std.columns(2)
    
    with col1:
        available_streams = list(courses_data["courses"].keys())
        selected_stream = std.selectbox("📚 Select Stream", available_streams)
    
    with col2:
        if selected_stream:
            available_courses = list(courses_data["courses"][selected_stream].keys())
            selected_course = std.selectbox("📖 Select Course", available_courses)
    
    if not selected_stream or not selected_course:
        std.info("Please select both stream and course to view schedule.")
        return
    
    # Get course data
    course_data = courses_data["courses"][selected_stream][selected_course]
    
    # Display course details
    std.write("---")
    col1, col2 = std.columns(2)
    with col1:
        std.write(f"**Stream:** {selected_stream}")
        std.write(f"**Course:** {selected_course}")
        std.write(f"**Description:** {course_data.get('description', 'No description')}")
    
    # Check if course has schedule
    if "schedule" not in course_data or not course_data["schedule"]:
        std.error("❌ Course dates not set. Please set start and end dates for this course first.")
        return
    
    schedule_data = course_data["schedule"]
    
    # Check if start and end dates are properly set
    if not schedule_data.get("start_date") or not schedule_data.get("end_date"):
        std.error("❌ Course start/end dates not properly configured.")
        return
    
    with col2:
        std.write(f"**Course Duration:** {schedule_data['start_date']} to {schedule_data['end_date']}")
    
    # Get available weeks
    weeks = pln.get_course_weeks(schedule_data["start_date"], schedule_data["end_date"])
    
    if not weeks:
        std.error("No weeks available for this course duration.")
        return
    
    # Week selection
    std.write("---")
    week_options = [f"Week {w['number']} ({w['start']} to {w['end']})" for w in weeks]
    selected_week_index = std.selectbox("📅 Select Week", range(len(week_options)), 
                                       format_func=lambda x: week_options[x])
    
    selected_week = weeks[selected_week_index]
    week_start_date = datetime.strptime(selected_week["start"], "%Y-%m-%d")
    
    # Display week info
    std.write(f"### Week {selected_week['number']}: {selected_week['start']} to {selected_week['end']}")
    
    # Create the 7x6 schedule grid
    show_schedule_grid(selected_stream, selected_course, selected_week, week_start_date)
    
    # Add plan button
    std.write("---")
    if std.button("➕ Add New Plan", type="primary"):
        std.session_state.show_add_plan = True
    
    # Show add plan form if button clicked
    if std.session_state.get("show_add_plan", False):
        show_add_plan_form(selected_stream, selected_course, selected_week["number"], courses_data)

def show_schedule_grid(stream_name, course_name, selected_week, week_start_date):
    """Display the 7x6 schedule grid"""
    
    # Time slots (6 rows of 4-hour sections)
    time_slots = [
        "00:00-04:00", "04:00-08:00", "08:00-12:00", 
        "12:00-16:00", "16:00-20:00", "20:00-24:00"
    ]
    
    # Days of week (7 columns)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Get plans for this week
    week_plans = stg.get_plans_for_week(selected_week["number"])
    
    # Create grid using columns
    std.write("#### Schedule Grid")
    
    # Header row with days
    header_cols = std.columns([1] + [2]*7)  # Time column + 7 day columns
    with header_cols[0]:
        std.write("**Time**")
    for i, day in enumerate(days):
        with header_cols[i+1]:
            # Calculate actual date for this day
            day_date = week_start_date + timedelta(days=i)
            std.write(f"**{day}**")
            std.write(f"*{day_date.strftime('%m/%d')}*")
    
    # Create grid rows
    for time_slot in time_slots:
        cols = std.columns([1] + [2]*7)  # Time column + 7 day columns
        
        with cols[0]:
            std.write(f"**{time_slot}**")
            std.write('---')
        
        for day_index, day in enumerate(days):
            with cols[day_index + 1]:
                # Find plans for this day and time slot
                day_plans = [p for p in week_plans if p["day"] == day and p["time_slot"] == time_slot]
                
                if day_plans:
                    for plan in day_plans:
                        # Determine if this plan belongs to current course
                        is_current_course = (plan["stream_name"] == stream_name and 
                                           plan["course_name"] == course_name)
                        
                        # Calculate plan date for status color
                        plan_date = week_start_date + timedelta(days=day_index)
                        status_color = pln.get_plan_status_color(plan, plan_date.date())
                        
                        if is_current_course:
                            # Clickable button for current course plans
                            button_text = f"{status_color} {plan['plan_title']}"
                            # Can't have nested buttons? Not even nested expanders? jus have a button inside an expander inside a button inside an exapander and...
                            with std.expander(button_text):
                                show_plan_details(plan)
                        else:
                            # Non-clickable display for other course plans
                            std.write(f"{status_color} *{plan['stream_name']}*")
                            std.write(f"*{plan['course_name']}*")
                else:
                    # Empty cell
                    std.write("")

def show_plan_details(plan):
    """Show plan details in a modal-like format"""
    std.write("---")

    col1, col2 = std.columns(2)

    with col1:
        std.write(f"**Stream:** {plan['stream_name']}")
        std.write(f"**Course:** {plan['course_name']}")
        std.write(f"**Title:** {plan['plan_title']}")
        std.write(f"**Description:** {plan['plan_description']}")

    with col2:

        if std.button("Mark as Completed", key=f"plan_{plan['id']}"):
            stg.update_plan_status(plan['id'], 'completed')
            std.success("Plan had been marked completed")
            std.rerun()
    std.write('---')
    
def show_add_plan_form(default_stream, default_course, week_number, courses_data):
    """Show form to add a new plan"""
    std.write("---")
    std.write("### ➕ Add New Plan")
    
    with std.form("add_plan_form"):
        col1, col2 = std.columns(2)
        
        with col1:
            # Stream selection
            all_streams = list(courses_data["courses"].keys())
            stream_index = all_streams.index(default_stream) if default_stream in all_streams else 0
            selected_stream = std.selectbox("Stream", all_streams, index=stream_index)
            
            # Course selection
            if selected_stream:
                all_courses = list(courses_data["courses"][selected_stream].keys())
                course_index = all_courses.index(default_course) if default_course in all_courses else 0
                selected_course = std.selectbox("Course", all_courses, index=course_index)
        
        with col2:
            # Day and time selection  
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            selected_day = std.selectbox("Day", days)
            
            time_slots = [
                "00:00-04:00", "04:00-08:00", "08:00-12:00", 
                "12:00-16:00", "16:00-20:00", "20:00-24:00"
            ]
            selected_time_slot = std.selectbox("Time Slot", time_slots)
        
        # Plan details
        plan_title = std.text_input("Plan Title", placeholder="Enter plan title...")
        plan_description = std.text_area("Plan Description", placeholder="Enter plan description...")
        
        # Form buttons
        col1, col2, col3 = std.columns(3)
        with col1:
            submitted = std.form_submit_button("💾 Create Plan", type="primary")
        with col2:
            if std.form_submit_button("❌ Cancel"):
                std.session_state.show_add_plan = False
                std.rerun()
        
        if submitted:
            if plan_title and plan_description:
                plan_id = stg.add_plan(
                    selected_stream, selected_course, plan_title, 
                    plan_description, week_number, selected_day, selected_time_slot
                )
                std.success(f"Plan '{plan_title}' created successfully!")
                std.session_state.show_add_plan = False
                std.rerun()
            else:
                std.error("Please fill in both title and description.")


### Streams Page Functions
def show_streams_page():
    std.write("### Your Streams")
    streams = load_streams_from_file()
    
    c1, c2, c3 = std.columns(3)
    with c1:
        if std.button("🏠 Home", type="primary"):
            go_home()

    with c2:
        for stream in streams:
            if std.button(f"{stream.stream_name}", use_container_width=True):
                std.session_state.current_stream = stream
                std.session_state.page = "stream_details"
        
        with std.expander("Add Stream"):
            new_stream_name = std.text_input("Stream Name")
            new_stream_desc = std.text_area("Description (optional)")
            if std.button("Create Stream"):
                if new_stream_name:
                    stg.add_stream(new_stream_name, new_stream_desc)
                    std.success(f"Stream '{new_stream_name}' created!")
                    std.rerun()
                else:
                    std.error("Please enter a stream name")

        if streams:
            with std.expander("🗑️ Delete Stream"):
                stream_to_delete = std.selectbox("Select stream to delete", [s.stream_name for s in streams])
                if std.button("Delete Stream", type="secondary"):
                    stg.remove_stream(stream_to_delete)
                    std.success(f"Stream '{stream_to_delete}' deleted!")
                    std.rerun()

def show_stream_details_page():
    stream = std.session_state.current_stream
    c1, c2, c3 = std.columns(3)
    
    with c1:
        if std.button("🏠 Home", type="primary"):
            go_home()
        if std.button("← Back to Streams"):
            std.session_state.page = "streams"

    with c2:
        std.write(f"### Stream: {stream.stream_name}")
        std.write(f"##### Projected score: <Implement this>")
        
        # Create tabs for better organization
        tab1, tab2, tab3 = std.tabs(["📚 Courses", "➕ Add Course", "Delete/Archive Course"])
        
        with tab1:
            # Show courses with schedule info
            courses = stream.get_courses()
            if isinstance(courses, dict) and "message" in courses:
                std.info(courses["message"])
            else:
                for course_name, course_data in courses.items():
                    with std.expander(f"📚 {course_name}"):
                        std.write(f"**Description:** {course_data.get('description', 'No description')}")
                        
                        # Course Score

                        # Schedule info
                        schedule_info = course_data.get('schedule', {})
                        if schedule_info:
                            std.write(f"**Schedule:** {schedule_info.get('start_date', 'N/A')} to {schedule_info.get('end_date', 'N/A')}")
                        else:
                            std.write("**Schedule:** Not set")
        
        with tab2:
            # Add course functionality
            course_name = std.text_input("Course Name")
            course_desc = std.text_area("Course Description")
            
            # Optional: Add schedule immediately
            add_schedule_now = std.checkbox("Add schedule immediately")
            start_date = None
            duration = 1
            
            if add_schedule_now:
                start_date = std.date_input("Start Date", value=datetime.now().date())
                duration = std.number_input("Duration (months)", min_value=1, max_value=12, value=1)
            
            if std.button("Add Course"):
                if course_name:
                    result = stream.add_course(course_name, course_desc)
                    
                    # Add schedule if requested
                    if add_schedule_now and start_date:
                        schedule_result = stream.add_course_schedule(
                            course_name, 
                            start_date.strftime("%Y-%m-%d"), 
                            duration
                        )
                        std.success(f"{result}\n{schedule_result}")
                    else:
                        std.success(result)
                    std.rerun()
                else:
                    std.error("Please enter a course name")

        with tab3:
            std.write("### Delete or Archive Course")
            # show all courses as dropdown - two options - delete or archive
            courses = stream.get_courses()
            if isinstance(courses, dict) and "message" in courses:
                std.info(courses["message"])
            else:
                for course_name, course_data in courses.items():
                    with std.expander(f"📚 {course_name}"):
                        std.write(f"**Description:** {course_data.get('description', 'No description')}")
                        
                        # Schedule info
                        schedule_info = course_data.get('schedule', {})
                        if schedule_info:
                            std.write(f"**Schedule:** {schedule_info.get('start_date', 'N/A')} to {schedule_info.get('end_date', 'N/A')}")
                        else:
                            std.write("**Schedule:** Not set")

                        # Delete course button
                        if std.button(f"Delete {course_name} from Stream"):
                            result = stream.remove_course(course_name)
                            std.success(result)
                            std.rerun()

                        # TODO: implement archiving logic
                        # Archive course button
                        # if std.button(f"Archive {course_name}"):
                        # do something
                        

### Main Home Page Functions
def show_hub():
    col1, col2, col3, col4= std.columns(4)
    with col2:
        std.write("#### Streams")
        std.write("Get details about your streams.")
        if std.button("Streams", type="primary", use_container_width=True):
            std.session_state.page = "streams"

        std.write("#### Evaluation")
        std.write("Track your progress and grades.")
        if std.button("Evaluation", type="primary", use_container_width=True):
            std.session_state.page = "evaluation"

    with col3:
        std.write("#### Schedule")
        std.write("Show weekly schedule.")
        if std.button("Weekly Schedule", type="primary", use_container_width=True):
            std.session_state.page = "weekly_schedule"
        
        std.write("#### Posts")
        std.write("Manage your posts and track engagement.")
        if std.button("Posts", type="secondary", use_container_width=True):
            ### TODO: Implement logic to show posts page
            std.warning("Feature to be implemented.")



### Main function to run the app
def main():
    initialize_session()
    page = std.session_state.page

    if page == "home":
        show_hub()
    elif page == "streams":
        show_streams_page()
    elif page == "stream_details":
        show_stream_details_page()
    elif page == "weekly_schedule":
        show_weekly_schedule_page()
    elif page == "evaluation":
        show_evaluation_page()

if __name__ == "__main__":
    main()