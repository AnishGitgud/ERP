#This is a project to help me not procrastinate. If i'm forced to learn coding, i might as well use it for myself.

Anything i want to learn, or master? I'll plan it on paper then implement it as a course in here.

Claude's summary of this project - "A comprehensive Streamlit-based application designed to help manage personal learning goals, track progress, and maintain accountability in skill development. Built as a personal ERP system for learning and productivity."

PROJECT STRUCTURE:

course_erp/
│
├── app.py                    # Main Streamlit application
├── README.md                 # Project documentation
│
├── modules/                  # Core functionality modules
│   ├── stream.py            # Stream class and management
│   ├── storage.py           # Data persistence (JSON I/O)
│   ├── schedule.py          # Scheduling logic
│   ├── history.py           # Progress and history tracking
│   ├── posts.py             # Post engagement management
│   └── description.py       # Course descriptions
│
├── data/                     # JSON data storage
│   ├── streams.json         # Stream definitions and metadata
│   ├── courses.json         # Course data and schedules
│   └── evaluations.json     # Evaluation submissions and reviews

HOW TO RUN:

Prerequisites

Python 3.7+
pip package manager

Installation

Clone the repository:
bashgit clone <repository-url>
cd track

Create and activate virtual environment:
bashpython -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

Install dependencies:
bashpip install streamlit pandas

Run the application:
bashstreamlit run app.py

Access the application:

Open your browser to http://localhost:8501
