from dataclasses import dataclass, field, asdict
from typing import Optional, List
from datetime import datetime
import uuid


@dataclass
class Subtask:
    """Represents a subtask within a task."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    completed: bool = False

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class Task:
    """Represents a task in the system."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    type: str = "customer engagement"
    status: str = "backlog"  # historical|current|backlog
    created_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    start_date: Optional[str] = None
    finish_date: Optional[str] = None
    time_estimate: str = ""
    notes: str = ""
    links: List[str] = field(default_factory=list)
    subtasks: List[Subtask] = field(default_factory=list)
    order: int = 0

    def to_dict(self):
        """Convert task to dictionary, handling nested Subtask objects."""
        data = asdict(self)
        data['subtasks'] = [st.to_dict() if isinstance(st, Subtask) else st for st in self.subtasks]
        return data

    @classmethod
    def from_dict(cls, data):
        """Create Task from dictionary, handling nested subtasks."""
        if 'subtasks' in data:
            data['subtasks'] = [
                Subtask.from_dict(st) if isinstance(st, dict) else st
                for st in data['subtasks']
            ]
        return cls(**data)


@dataclass
class TaskType:
    """Represents configuration for a task type."""
    max_open: int = 3
    color: str = "#4A90E2"

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class Config:
    """Application configuration."""
    task_types: dict = field(default_factory=lambda: {
        "customer engagement": {"max_open": 3, "color": "#4A90E2"},
        "content enablements": {"max_open": 5, "color": "#7ED321"}
    })
    max_active_tasks: int = 10
    auto_scroll_to_current: bool = True

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def get_max_open_for_type(self, task_type: str) -> int:
        """Get the maximum number of open tasks for a given type."""
        if task_type in self.task_types:
            return self.task_types[task_type].get('max_open', 3)
        return 3  # Default if type not found
