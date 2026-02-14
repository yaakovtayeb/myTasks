import json
import os
from pathlib import Path
from typing import List, Optional
from models import Task, Config


class StorageManager:
    """Manages persistence of tasks and configuration."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.tasks_file = self.data_dir / "tasks.jsonl"
        self.config_file = self.data_dir / "config.json"
        self.ensure_data_files()

    def ensure_data_files(self):
        """Create data directory and default files if they don't exist."""
        self.data_dir.mkdir(exist_ok=True)

        # Create default config if it doesn't exist
        if not self.config_file.exists():
            default_config = Config()
            self.save_config(default_config)

        # Create empty tasks file if it doesn't exist
        if not self.tasks_file.exists():
            self.tasks_file.touch()

    def load_tasks(self) -> List[Task]:
        """Load all tasks from JSONL file."""
        tasks = []
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            task_data = json.loads(line)
                            tasks.append(Task.from_dict(task_data))
                        except json.JSONDecodeError:
                            continue
        return tasks

    def save_tasks(self, tasks: List[Task]):
        """Save all tasks to JSONL file, overwriting existing content."""
        with open(self.tasks_file, 'w') as f:
            for task in tasks:
                json.dump(task.to_dict(), f)
                f.write('\n')

    def append_task(self, task: Task):
        """Append a single task to JSONL file."""
        with open(self.tasks_file, 'a') as f:
            json.dump(task.to_dict(), f)
            f.write('\n')

    def load_config(self) -> Config:
        """Load configuration from JSON file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
                return Config.from_dict(config_data)
        return Config()

    def save_config(self, config: Config):
        """Save configuration to JSON file."""
        with open(self.config_file, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Find and return a specific task by ID."""
        tasks = self.load_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, updated_task: Task):
        """Update a specific task by replacing it in the file."""
        tasks = self.load_tasks()
        for i, task in enumerate(tasks):
            if task.id == updated_task.id:
                tasks[i] = updated_task
                break
        self.save_tasks(tasks)

    def delete_task(self, task_id: str):
        """Delete a task by ID."""
        tasks = self.load_tasks()
        tasks = [task for task in tasks if task.id != task_id]
        self.save_tasks(tasks)
