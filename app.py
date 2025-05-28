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
from datetime import datetime

from modules.stream import Stream

from modules import storage as stg
from modules import schedule as sch
from modules.evaluation import ADDITIONAL_COMPONENT_POINTS, MAIN_COMPONENT_WEIGHTS

std.set_page_config(
    layout="wide",
)




# css styling location - later on




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
    """Show weekly schedule selection and view"""
    col1, col2, col3 = std.columns(3)
    
    with col1:
        if std.button("🏠 Home", type="primary"):
            go_home()
    
    with col2:
        std.write("### Weekly Schedule")
        
        # Get all scheduled courses
        scheduled_courses = sch.get_all_scheduled_courses()
        
        if not scheduled_courses:
            std.info("No courses have schedules yet. Add schedules to your courses firstd.")
            return
        
        # Stream selection
        selected_stream = std.selectbox("Select Stream", list(scheduled_courses.keys()))
        
        if selected_stream:
            # Course selection
            selected_course = std.selectbox("Select Course", scheduled_courses[selected_stream])
            
            if selected_course:
                # Get and display course schedule
                schedule_data = sch.get_course_schedule(selected_stream, selected_course)
                
                if schedule_data:
                    std.write(f"**Course:** {selected_course}")
                    std.write(f"**Duration:** {schedule_data['start_date']} to {schedule_data['end_date']}")
                    
                    # Weekly schedule editor
                    show_weekly_schedule_editor(selected_stream, selected_course, schedule_data)

def show_weekly_schedule_editor(stream_name, course_name, schedule_data):
    """Show editable weekly schedule table"""
    weekly_schedule = schedule_data.get("weekly_schedule", {})
    
    if not weekly_schedule:
        std.warning("No weekly schedule found for this course.")
        return
    
    # Week selection
    week_keys = list(weekly_schedule.keys())
    selected_week = std.selectbox("Select Week", week_keys, 
                                 format_func=lambda x: f"Week {x} ({weekly_schedule[x]['week_start']} to {weekly_schedule[x]['week_end']})")
    
    if selected_week:
        std.write(f"### Week: {weekly_schedule[selected_week]['week_start']} to {weekly_schedule[selected_week]['week_end']}")
        
        # Create editable table
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        daily_tasks = weekly_schedule[selected_week]["daily_tasks"]
        
        # Use columns for better layout
        col1, col2 = std.columns([1, 3])
        
        with col2:
            # Create form for editing
            with std.form(f"weekly_schedule_{selected_week}"):
                updated_tasks = {}
                for day in days:
                    updated_tasks[day] = std.text_area(
                        day, 
                        value=daily_tasks.get(day, ""),
                        height=80,
                        key=f"{selected_week}_{day}"
                    )
                
                if std.form_submit_button("Save Weekly Schedule"):
                    # Update all days
                    for day, task in updated_tasks.items():
                        sch.update_weekly_task(stream_name, course_name, selected_week, day, task)
                    std.success("Weekly schedule updated!")
                    std.rerun()

def show_course_schedule_manager(stream, course_name):
    """Show schedule management for a specific course"""
    std.write(f"### Schedule for {course_name}")
    
    # Check if course has schedule
    schedule_data = stream.get_course_schedule(course_name)
    
    if schedule_data:
        # Display existing schedule
        col1, col2 = std.columns(2)
        with col1:
            std.write(f"**Start Date:** {schedule_data['start_date']}")
            std.write(f"**End Date:** {schedule_data['end_date']}")
            std.write(f"**Duration:** {schedule_data.get('duration_months', 1)} months")
        
        with col2:
            # Use a form instead of expander for editing
            std.write("**Edit End Date:**")
            new_end_date = std.date_input("New End Date", 
                                        value=datetime.strptime(schedule_data['end_date'], "%Y-%m-%d").date(),
                                        key=f"edit_date_{course_name}")
            if std.button("Update End Date", key=f"update_{course_name}"):
                result = stream.update_course_end_date(course_name, new_end_date.strftime("%Y-%m-%d"))
                std.success(result)
                std.rerun()
    else:
        # Use a form instead of expander for adding schedule
        std.write("**Add Schedule:**")
        start_date = std.date_input("Start Date", value=datetime.now().date(), key=f"start_date_{course_name}")
        duration = std.number_input("Duration (months)", min_value=1, max_value=12, value=1, key=f"duration_{course_name}")
        
        if std.button("Add Schedule", key=f"add_schedule_{course_name}"):
            result = stream.add_course_schedule(course_name, start_date.strftime("%Y-%m-%d"), duration)
            std.success(result)
            std.rerun()


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
                        
                        show_course_schedule_manager(stream, course_name)
        
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
                        # ddo something
                        

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