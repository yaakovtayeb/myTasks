from typing import List, Dict, Optional, Tuple
from datetime import datetime
from models import Task, Subtask, Config
from storage import StorageManager


class TaskManager:
    """Business logic layer for task management."""

    def __init__(self, storage: StorageManager):
        self.storage = storage

    def get_all_tasks_ordered(self) -> Dict[str, List[Task]]:
        """Get all tasks grouped by status and ordered appropriately."""
        tasks = self.storage.load_tasks()

        grouped = {
            'historical': [],
            'current': [],
            'backlog': []
        }

        for task in tasks:
            if task.status in grouped:
                grouped[task.status].append(task)

        # Sort historical by finish_date (most recent first)
        grouped['historical'].sort(
            key=lambda t: t.finish_date if t.finish_date else "",
            reverse=True
        )

        # Sort current and backlog by order
        grouped['current'].sort(key=lambda t: t.order)
        grouped['backlog'].sort(key=lambda t: t.order)

        return grouped

    def add_task(self, title: str, task_type: str, status: str = "backlog",
                 time_estimate: str = "", notes: str = "",
                 links: List[str] = None) -> Tuple[bool, str, Optional[Task]]:
        """
        Add a new task.
        Returns (success, message, task).
        """
        if links is None:
            links = []

        # Validate if adding to current status
        if status == "current":
            can_add, message = self.can_add_current_task(task_type)
            if not can_add:
                return False, message, None

        # Get next order number for the status
        tasks = self.storage.load_tasks()
        status_tasks = [t for t in tasks if t.status == status]
        next_order = max([t.order for t in status_tasks], default=-1) + 1

        task = Task(
            title=title,
            type=task_type,
            status=status,
            time_estimate=time_estimate,
            notes=notes,
            links=links,
            order=next_order,
            start_date=datetime.now().strftime("%Y-%m-%d") if status == "current" else None
        )

        self.storage.append_task(task)
        return True, "Task added successfully", task

    def update_task(self, task_id: str, **kwargs) -> Tuple[bool, str]:
        """
        Update task fields.
        Returns (success, message).
        """
        task = self.storage.get_task_by_id(task_id)
        if not task:
            return False, "Task not found"

        # Update allowed fields
        allowed_fields = ['title', 'type', 'time_estimate', 'notes', 'links', 'order']
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(task, field, value)

        self.storage.update_task(task)
        return True, "Task updated successfully"

    def complete_task(self, task_id: str, finish_date: str) -> Tuple[bool, str]:
        """
        Mark a task as completed and move to historical.
        Returns (success, message).
        """
        task = self.storage.get_task_by_id(task_id)
        if not task:
            return False, "Task not found"

        task.status = "historical"
        task.finish_date = finish_date

        self.storage.update_task(task)
        return True, "Task completed successfully"

    def move_to_current(self, task_id: str) -> Tuple[bool, str]:
        """
        Move a backlog task to current status.
        Returns (success, message).
        """
        task = self.storage.get_task_by_id(task_id)
        if not task:
            return False, "Task not found"

        if task.status != "backlog":
            return False, "Only backlog tasks can be moved to current"

        # Validate type limits
        can_add, message = self.can_add_current_task(task.type)
        if not can_add:
            return False, message

        task.status = "current"
        task.start_date = datetime.now().strftime("%Y-%m-%d")

        # Get next order for current tasks
        tasks = self.storage.load_tasks()
        current_tasks = [t for t in tasks if t.status == "current" and t.id != task_id]
        task.order = max([t.order for t in current_tasks], default=-1) + 1

        self.storage.update_task(task)
        return True, "Task moved to current"

    def can_add_current_task(self, task_type: str) -> Tuple[bool, str]:
        """
        Check if a task of given type can be added to current status.
        Returns (can_add, message).
        """
        config = self.storage.load_config()
        tasks = self.storage.load_tasks()

        # Count current tasks of this type
        current_type_count = sum(
            1 for t in tasks
            if t.status == "current" and t.type == task_type
        )

        max_allowed = config.get_max_open_for_type(task_type)

        if current_type_count >= max_allowed:
            return False, f"Maximum {max_allowed} '{task_type}' tasks already open"

        # Check total active tasks limit
        total_current = sum(1 for t in tasks if t.status == "current")
        if total_current >= config.max_active_tasks:
            return False, f"Maximum {config.max_active_tasks} total active tasks reached"

        return True, "Can add task"

    def add_subtask(self, task_id: str, subtask_title: str) -> Tuple[bool, str]:
        """
        Add a subtask to a task.
        Returns (success, message).
        """
        task = self.storage.get_task_by_id(task_id)
        if not task:
            return False, "Task not found"

        subtask = Subtask(title=subtask_title)
        task.subtasks.append(subtask)

        self.storage.update_task(task)
        return True, "Subtask added successfully"

    def toggle_subtask(self, task_id: str, subtask_id: str) -> Tuple[bool, str]:
        """
        Toggle subtask completion status.
        Returns (success, message).
        """
        task = self.storage.get_task_by_id(task_id)
        if not task:
            return False, "Task not found"

        for subtask in task.subtasks:
            if subtask.id == subtask_id:
                subtask.completed = not subtask.completed
                self.storage.update_task(task)
                return True, "Subtask updated successfully"

        return False, "Subtask not found"

    def delete_task(self, task_id: str) -> Tuple[bool, str]:
        """
        Delete a task.
        Returns (success, message).
        """
        task = self.storage.get_task_by_id(task_id)
        if not task:
            return False, "Task not found"

        self.storage.delete_task(task_id)
        return True, "Task deleted successfully"

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a single task by ID."""
        return self.storage.get_task_by_id(task_id)
