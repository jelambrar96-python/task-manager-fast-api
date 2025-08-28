# Flask Task Manager

This repository contains the source code for a simple task management web application built using the Flask web framework and PostgreSQL as the database.

## Features

- User authentication (registration, login, logout)
- Create, read, update, and delete tasks
- Assign tasks to different users
- Track task status (to-do, in progress, completed)
- Sort and filter tasks by various criteria (due date, assignee, status, etc.)
- Responsive design for desktop and mobile devices

## Technologies Used

- **Backend**: Flask, PostgreSQL, SQLAlchemy, Flask-Login
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Development Tools**: Git, GitHub, Virtual Environment, Pytest

## Setup

1. Clone the repository: `git clone https://github.com/your-username/flask-task-manager.git`
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`
4. Install the required dependencies: `pip install -r requirements.txt`
5. Set up the PostgreSQL database:
   - Create a new database
   - Update the database connection details in the `config.py` file
6. Run the Flask application: `flask run`
7. Open the application in your web browser at `http://localhost:5000`

## Contributing

If you find any issues or have suggestions for improvements, feel free to open a new issue or submit a pull request.
