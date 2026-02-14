# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MyTasks is a personal task management application with a web interface that manages historical, present, and backlog tasks. The application emphasizes simplicity with a text-based UI and local JSONL storage.

## Development Setup

### First Time Setup

1. Create virtual environment:
```bash
python3 -m venv venv
```

2. Activate virtual environment:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Load environment variables (optional):
```bash
export $(cat .env | xargs)
```

### Running the Application

1. Activate virtual environment:
```bash
source venv/bin/activate
```

2. Start the Flask development server:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5001
```

The application will automatically create the `data/` directory with `tasks.jsonl` and `config.json` files on first run.

## Architecture

### Data Storage
- **Backend**: Local JSONL file (no cloud or remote support)
- **Config**: Separate config file for app settings (editable via UI or manually)
- Each task is stored as a JSON line with support for subtasks, time estimates, notes, and links

### Task Model
- **States**: Historical (completed with finish date), Current (active), Backlog (future)
- **Types**: Tasks have types (default: "customer engagement", "content enablements")
- Each type has a maximum number of open tasks (e.g., max 3 for customer engagement)
- Tasks become historical when checked and given a finish date

### UI Behavior
- Scrollable list showing all tasks (historical at top, backlog at bottom)
- Default scroll position: current task (maintained on startup/refresh)
- Text-based format for simplicity and focus

### Settings Management
- Maximum active tasks at the same time (configurable)
- Task types and their maximum open task limits
- Configurable via UI or direct config file editing

### Print Functionality
- Print current tasks only
- Print current tasks + backlog

## Key Constraints

1. **Local-first**: No cloud synchronization or remote storage
2. **Simplicity**: Text-based interface, minimal complexity
3. **Type enforcement**: Respect maximum open tasks per type
4. **State management**: Clear distinction between historical/current/backlog states
