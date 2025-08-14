from datetime import datetime, timedelta
import time
from typing import Optional, Dict, Any

# Constants for time calculations
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400

class Task:
    """Represents a single todo task with optional due date and time tracking."""
    
    def __init__(self, task_id: int, title: str, done: bool = False, due_date: Optional[datetime] = None):
        if not isinstance(task_id, int) or task_id <= 0:
            raise ValueError("Task ID must be a positive integer")
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
            
        self.id = task_id
        self.title = title.strip()
        self.done = done
        self.due_date = due_date
        self.time_spent = 0.0  # Total time in seconds
        self.timer_start: Optional[float] = None  # Consistent naming
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'done': self.done,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'time_spent': self.time_spent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task instance from dictionary data."""
        try:
            due_date = datetime.fromisoformat(data['due_date']) if data.get('due_date') else None
            task = cls(
                data['id'],
                data['title'],
                data.get('done', False),
                due_date
            )
            task.time_spent = max(0.0, data.get('time_spent', 0.0))  # Ensure non-negative
            return task
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Invalid task data: {e}")
    
    def start_timer(self) -> bool:
        """Start tracking time for this task."""
        if self.done:
            return False  # Don't start timer for completed tasks
        if self.timer_start is None:
            self.timer_start = time.time()
            return True
        return False  # Timer already running
    
    def stop_timer(self) -> float:
        """Stop tracking time and return elapsed seconds."""
        if self.timer_start is not None:
            elapsed = time.time() - self.timer_start
            self.time_spent += elapsed
            self.timer_start = None
            return elapsed
        return 0.0
    
    def is_timer_running(self) -> bool:
        """Check if timer is currently running."""
        return self.timer_start is not None
    
    def format_time_spent(self) -> str:
        """Format total time spent in human-readable form."""
        return self._format_duration(self.time_spent)
    
    def remaining_time_seconds(self) -> Optional[float]:
        """Calculate seconds until due date. Returns None if no due date or completed."""
        if not self.due_date or self.done:
            return None
        return (self.due_date - datetime.now()).total_seconds()
    
    def format_remaining_time(self) -> str:
        """Format remaining time for display."""
        remaining = self.remaining_time_seconds()
        if remaining is None:
            return "No deadline"
        
        if remaining < 0:
            return f"Overdue by {self._format_duration(abs(remaining))}"
        
        if remaining < SECONDS_PER_MINUTE:
            return "Due very soon"
        
        return f"{self._format_duration(remaining)} remaining"
    
    def is_overdue(self) -> bool:
        """Check if task is past due and incomplete."""
        if self.done or not self.due_date:
            return False
        return datetime.now() > self.due_date
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human-readable string."""
        if seconds < SECONDS_PER_MINUTE:
            return f"{int(seconds)}s"
        
        days, remainder = divmod(int(seconds), SECONDS_PER_DAY)
        hours, remainder = divmod(remainder, SECONDS_PER_HOUR)
        minutes, secs = divmod(remainder, SECONDS_PER_MINUTE)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0 and days == 0:  # Skip minutes if showing days
            parts.append(f"{minutes}m")
        if not parts or (len(parts) == 1 and parts[0].endswith('m')):
            parts.append(f"{secs}s")
        
        return " ".join(parts)


class TodoList:
    """Manages a collection of tasks."""
    
    def __init__(self):
        self.tasks: list[Task] = []
        self.next_id = 1
    
    def add_task(self, title: str, due_date: Optional[datetime] = None) -> Task:
        """Create and add a new task."""
        task = Task(self.next_id, title, due_date=due_date)
        self.tasks.append(task)
        self.next_id += 1
        return task
    
    def find_task(self, task_id: int) -> Optional[Task]:
        """Find task by ID."""
        return next((task for task in self.tasks if task.id == task_id), None)
    
    def list_tasks(self, show_all: bool = False) -> list[Task]:
        """Get tasks (all or incomplete only)."""
        if show_all:
            return self.tasks.copy()
        return [task for task in self.tasks if not task.done]
    
    def mark_done(self, task_id: int) -> Optional[Task]:
        """Mark task as completed and stop timer if running."""
        task = self.find_task(task_id)
        if task and not task.done:
            task.done = True
            if task.is_timer_running():
                task.stop_timer()
            return task
        return None
    
    def delete_task(self, task_id: int) -> Optional[Task]:
        """Remove task by ID."""
        task = self.find_task(task_id)
        if task:
            self.tasks.remove(task)
            return task
        return None
    
    def start_timer(self, task_id: int) -> bool:
        """Start timer for specified task."""
        task = self.find_task(task_id)
        return task.start_timer() if task else False
    
    def stop_timer(self, task_id: int) -> float:
        """Stop timer for specified task."""
        task = self.find_task(task_id)
        return task.stop_timer() if task else 0.0
    
    def get_total_time_spent(self) -> float:
        """Calculate total time spent on all tasks."""
        return sum(task.time_spent for task in self.tasks)
    
    def get_upcoming_tasks(self, days: int = 3) -> list[Task]:
        """Get incomplete tasks due within specified days."""
        if days <= 0:
            return []
        
        now = datetime.now()
        cutoff = now + timedelta(days=days)
        
        return [
            task for task in self.tasks
            if not task.done
            and task.due_date
            and now <= task.due_date <= cutoff
        ]
    
    def get_overdue_tasks(self) -> list[Task]:
        """Get all overdue tasks."""
        return [task for task in self.tasks if task.is_overdue()]