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
        due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
        task = cls(
            data['id'],
            data['title'],
            data['done'],
            due_date
        )
        task.time_spent = data.get('time_spent', 0.0)
        return task
    
    def start_timer(self):
        if not self.time_started:
            self.time_started = time.time()
            return True
        return False
    
    def stop_timer(self):
        if self.time_started:
            elapsed_time = time.time() - self.time_started
            self.time_spent += elapsed_time
            self.time_started = None
            return elapsed_time
        return 0.0
    
    def format_time_spent(self):
        hours, remainder = divmod(self.time_spent, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    
    def remaining_time(self):
        if not self.due_date or self.done:
            return None
        return (self.due_date - datetime.now()).total_seconds()
    
    def format_remaining_time(self):
        remaining = self.remaining_time()
        if remaining is None:
            return "无截止时间"
        
        if remaining < 0:
            overdue = abs(remaining)
            return f"已逾期 {int(overdue // 86400)}d {int(overdue // 3600)}h {int((overdue % 3600) // 60)}m {int(overdue % 60)}s"

        days = int(remaining // 86400)
        hours = int((remaining % 86400) // 3600)
        minutes = int((remaining % 3600) // 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}天")
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0 and days == 0:  
            parts.append(f"{minutes}分钟")
        
        if not parts:
            return "剩余时间不足1分钟"
        return "还剩 " + "".join(parts)
    
    def is_overdue(self):
        return self.due_date and not self.done and datetime.now() > self.due_date
    
class TodoList:
    def __init__(self):
        self.tasks = []
        self.next_id = 1

    def add_task(self, title, due_date=None):
        task = Task(self.next_id, title, due_date=due_date)
        self.tasks.append(task)
        self.next_id += 1
        return task
    
    def list_tasks(self, show_all=False):
        if not self.tasks:
            return []
        return [task for task in self.tasks if show_all or not task.done]
    
    def mark_done(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                task.done = True
                # Stop timer if running
                if task.timer_start:
                    task.stop_timer()
                return task
        return None
    
    def delete_task(self, task_id):
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                return self.tasks.pop(i)
        return None
    
    def find_task(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def start_timer(self, task_id):
        task = self.find_task(task_id)
        if task and not task.done:
            return task.start_timer()
        return False
    
    def stop_timer(self, task_id):
        task = self.find_task(task_id)
        if task:
            return task.stop_timer()
        return 0.0
    
    def get_total_time_spent(self):
        return sum(task.time_spent for task in self.tasks)
    
    def get_upcoming_tasks(self, days=3):
        now = datetime.now()
        cutoff = now + timedelta(days=days)
        return [task for task in self.tasks 
                if not task.done 
                and task.due_date 
                and task.due_date <= cutoff]