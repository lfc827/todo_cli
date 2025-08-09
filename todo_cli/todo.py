from datetime import datetime, timedelta    
import time

# The Class of task
class Task:
    # Initialize task properties
    def __init__(self, id, title, done=False, due_date=None):
        self.id = id                            # Unique identifier for the task
        self.title = title                      # Title of the task
        self.done = done                        # Completion status
        self.due_date = due_date                # Optional deadline datetime
        self.time_spent = 0.0                   # Total time spent on task (in seconds)
        self.time_started = None                # Timestamp when timer was started
    
    def to_dict(self):
        # Convert task to dictionary
        return {
            'id': self.id,
            'title': self.title,
            'done': self.done,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'time_spent': self.time_spent
        }
    
    @classmethod
    def from_dict(cls, data):
        # Create Task instance from dictionary data
        due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
        task = cls(
            data['id'],
            data['title'],
            data['done'],
            due_date
        )
        task.time_spent = data.get('time_spent', 0.0)  # Load saved time
        return task
    
    def start_timer(self):
        # Start tracking time for this task 
        if not self.time_started:
            self.time_started = time.time()  # Record start time
            return True
        return False  # Timer was already running
    
    def stop_timer(self):
        # Stop tracking time and update total
        if self.time_started:
            elapsed_time = time.time() - self.time_started  # Calculate elapsed time
            self.time_spent += elapsed_time  # Add to total time spent
            self.time_started = None  # Reset timer
            return elapsed_time
        return 0.0  # Timer was not running
    
    def format_time_spent(self):
        # Format time spent in human-readable form
        hours, remainder = divmod(self.time_spent, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    
    def remaining_time(self):
        # Calculate seconds until due date
        if not self.due_date or self.done:
            return None
        return (self.due_date - datetime.now()).total_seconds()
    
    def format_remaining_time(self):
        # Format remaining time for display
        remaining = self.remaining_time()
        if remaining is None:
            return "No due date."
        
        if remaining < 0:
            # Handle overdue tasks
            overdue = abs(remaining)
            return f"Overdue for {int(overdue // 86400)}d {int(overdue // 3600)}h {int((overdue % 3600) // 60)}m {int(overdue % 60)}s"

        days = int(remaining // 86400)
        hours = int((remaining % 86400) // 3600)
        minutes = int((remaining % 3600) // 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0 and days == 0:  
            parts.append(f"{minutes}m")
        
        if not parts:
            return "Less than 1 minute remaining."
        return "There are still " + "".join(parts) + " remaining."
    
    def is_overdue(self):
        # Check if task is past due and incomplete
        return self.due_date and not self.done and datetime.now() > self.due_date

 # Class for managing collection of tasks   
class TodoList:
    def __init__(self):
        self.tasks = []     # List of tasks
        self.next_id = 1    # Next task ID to assign

    def add_task(self, title, due_date=None):
        # Create and add new task
        task = Task(self.next_id, title, due_date=due_date)
        self.tasks.append(task)
        self.next_id += 1
        return task
    
    def list_tasks(self, show_all=False):
        # Get tasks (all or incomplete only)
        if not self.tasks:
            return []
        return [task for task in self.tasks if show_all or not task.done]
    
    def mark_done(self, task_id):
        # Mark task as completed
        for task in self.tasks:
            if task.id == task_id:
                task.done = True
                # Stop timer if running
                if task.timer_start:
                    task.stop_timer()
                return task
        return None  # Task not found
    
    def delete_task(self, task_id):
        # Remove task by ID
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                return self.tasks.pop(i)
        return None  # Task not found
    
    def find_task(self, task_id):
        # Find task by ID
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def start_timer(self, task_id):
        # Start timer for specified task
        task = self.find_task(task_id)
        if task and not task.done:
            return task.start_timer()
        return False  # Task not found or completed
    
    def stop_timer(self, task_id):
        # Stop timer for specified task
        task = self.find_task(task_id)
        if task:
            return task.stop_timer()
        return 0.0  # Task not found
    
    def get_total_time_spent(self):
        # Calculate total time spent on all tasks
        return sum(task.time_spent for task in self.tasks)
    
    def get_upcoming_tasks(self, days=3):
        # Get incomplete tasks due within specified days
        now = datetime.now()
        cutoff = now + timedelta(days=days)
        return [task for task in self.tasks 
                if not task.done 
                and task.due_date 
                and now <= task.due_date <= cutoff]