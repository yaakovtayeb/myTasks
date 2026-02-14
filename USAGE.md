# MyTasks

## Overview

MyTasks is a personal task management application with a web interface that manages historical, present, and backlog tasks. The app features a simple, text-based UI with automatic scrolling to current tasks for easy focus and productivity.

## Features

### Core Functionality

1. **Task Management**: Organize tasks in three categories:
   - **Historical**: Completed tasks with finish dates
   - **Current**: Active tasks you're working on now
   - **Backlog**: Future tasks waiting to be started

2. **Task Properties**:
   - Title (required)
   - Task type (e.g., "customer engagement", "content enablements")
   - Time estimates (e.g., "2h", "3 days")
   - Notes for additional context
   - Links to relevant resources
   - Subtasks with completion tracking

3. **Smart Task Type Limits**:
   - Each task type has a maximum number of open tasks
   - Prevents overcommitment by enforcing limits
   - Default types:
     - Customer engagement: max 3 open tasks
     - Content enablements: max 5 open tasks

4. **Auto-Scroll**: Page automatically scrolls to current tasks on load and refresh

5. **Print Functionality**:
   - Print current tasks only
   - Print current tasks + backlog

### Data Storage

- **Local JSONL file**: All tasks stored in `data/tasks.jsonl`
- **Config file**: Settings stored in `data/config.json`
- **No cloud sync**: Completely local, no remote storage

## Installation & Setup

### First Time Setup

1. **Extract the archive**:
   ```bash
   tar -xzf myTasks.tar.gz
   cd myTasks
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Activate virtual environment**:

   **On Mac/Linux**:
   ```bash
   source venv/bin/activate
   ```

   **On Windows**:
   ```bash
   venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **(Optional) Load environment variables**:
   ```bash
   export $(cat .env | xargs)
   ```

## Running the Application

### On Your Local Mac

1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Start the Flask development server**:
   ```bash
   python app.py
   ```

3. **Open your browser and navigate to**:
   ```
   http://localhost:5001
   ```

4. **Stop the server**: Press `CTRL+C` in the terminal

### On AWS SageMaker

1. **Start the Flask development server** in a terminal:
   ```bash
   cd /home/sagemaker-user/myTasks
   source venv/bin/activate
   python app.py
   ```

2. **Access the app** using the SageMaker proxy URL:
   ```
   https://[your-instance].studio.[region].sagemaker.aws/jupyterlab/default/proxy/5001/
   ```

**Note**: The app includes ProxyFix middleware to automatically handle reverse proxy paths in SageMaker.

## Using the Application

### Adding a Task

1. Click the **"Add Task"** button
2. Fill in the task details:
   - **Title**: Required
   - **Type**: Choose from configured types
   - **Status**: Choose "Current" or "Backlog"
   - **Time Estimate**: Optional (e.g., "2h", "1 day")
   - **Notes**: Optional additional context
   - **Links**: Optional URLs (one per line)
3. Click **"Add Task"**

### Working with Tasks

**Complete a Current Task**:
- Check the checkbox next to the task
- Enter the finish date (YYYY-MM-DD format)
- Task moves to Historical section

**Move Backlog to Current**:
- Click the **"Start"** button on a backlog task
- Task moves to Current section (if type limits allow)

**View Task Details**:
- Click the **▼** button to expand/collapse task details
- Shows subtasks, notes, links, and metadata

**Add Subtasks**:
1. Expand the task details (click ▼)
2. Click **"Add Subtask"**
3. Enter subtask title
4. Check/uncheck subtasks to mark completion

### Managing Settings

1. Click **"Settings"** in the navigation
2. Configure:
   - **Maximum Active Tasks**: Total limit for current tasks
   - **Task Types**: Add, remove, or modify task types
     - Each type has a name, max open count, and color
3. Click **"Save Settings"** to persist changes

### Printing Tasks

- **Print Current Only**: Click "Print Current" in navigation
- **Print Current + Backlog**: Click "Print All" in navigation
- Print dialog opens automatically with clean, formatted layout

## File Structure

```
myTasks/
├── app.py                  # Flask application with routes and API
├── config.py               # Flask configuration (port, debug settings)
├── models.py               # Data models (Task, Subtask, Config)
├── storage.py              # JSONL/JSON file operations
├── task_manager.py         # Business logic layer
├── requirements.txt        # Python dependencies
├── data/                   # Auto-created on first run
│   ├── tasks.jsonl        # Task storage (one JSON object per line)
│   └── config.json        # Application settings
├── templates/              # HTML templates
│   ├── base.html          # Base layout with navigation
│   ├── index.html         # Main task list view
│   ├── settings.html      # Settings page
│   └── print.html         # Print view
└── static/
    ├── css/style.css      # Styling
    └── js/app.js          # Client-side interactions
```

## Configuration

The `data/config.json` file contains:

```json
{
  "task_types": {
    "customer engagement": {
      "max_open": 3,
      "color": "#4A90E2"
    },
    "content enablements": {
      "max_open": 5,
      "color": "#7ED321"
    }
  },
  "max_active_tasks": 10,
  "auto_scroll_to_current": true
}
```

You can edit this file manually or use the Settings UI.

## API Endpoints

The application provides a REST API for programmatic access:

### Tasks
- `GET /api/tasks` - Get all tasks grouped by status
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/<id>` - Get a specific task
- `PUT /api/tasks/<id>` - Update a task
- `DELETE /api/tasks/<id>` - Delete a task
- `POST /api/tasks/<id>/complete` - Mark task as completed
- `POST /api/tasks/<id>/current` - Move task from backlog to current
- `POST /api/tasks/<id>/subtasks` - Add a subtask
- `POST /api/tasks/<id>/subtasks/<subtask_id>/toggle` - Toggle subtask completion

### Configuration
- `GET /api/config` - Get application configuration
- `PUT /api/config` - Update application configuration

## Troubleshooting

### Port Already in Use
If port 5001 is already in use, edit `config.py` and change the `PORT` value:
```python
PORT = 5002  # or another available port
```

### CSS/JS Not Loading in SageMaker
The app includes ProxyFix middleware which should handle this automatically. If issues persist:
1. Check that you're accessing the correct proxy URL with `/5001/` at the end
2. Verify the Flask app is running without errors
3. Check browser console for specific 404 errors

### Data Not Persisting
- Ensure the `data/` directory exists and is writable
- Check file permissions on `data/tasks.jsonl` and `data/config.json`
- Verify no errors in the Flask server console output

### Virtual Environment Issues
If you have problems with the virtual environment:
```bash
# Delete and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Tips for Best Use

1. **Start your day** by reviewing current tasks - the page auto-scrolls there
2. **Use task types** to balance different categories of work
3. **Add time estimates** to help with planning
4. **Break down complex tasks** using subtasks
5. **Add links** to relevant documents or resources
6. **Print regularly** to have a physical reference
7. **Review backlog** periodically to plan upcoming work
8. **Complete tasks promptly** to move them to historical for clean current view

## Technology Stack

- **Backend**: Flask 3.0 (Python web framework)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Storage**: JSONL files (local filesystem)
- **Middleware**: Werkzeug ProxyFix (for reverse proxy compatibility)

## License

Personal use application.
