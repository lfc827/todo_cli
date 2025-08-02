import json
import csv
import os
from datetime import datetime
from .todo import Task

def load_tasks(filename):
    if not os.path.exists(filename):
        return []
    
    tasks = []
    if filename.endswith('.json'):
        with open(filename, 'r') as f:
            data = json.load(f)
            for task_data in data:
                if 'due_date' not in task_data:
                    task_data['due_date'] = None
                if 'time_spent' not in task_data:
                    task_data['time_spent'] = 0.0
                tasks.append(Task.from_dict(task_data))
    elif filename.endswith('.csv'):
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                due_date = datetime.fromisoformat(row['due_date']) if row['due_date'] else None
                task = Task(
                    id=int(row['id']),
                    title=row['title'],
                    done=row['done'].lower() == 'true',
                    due_date=due_date
                )
                task.time_spent = float(row.get('time_spent', 0.0))
                tasks.append(task)
    return tasks

def save_tasks(tasks, filename):
    if filename.endswith('.json'):
        with open(filename, 'w') as f:
            json.dump([task.to_dict() for task in tasks], f, indent=2)
    elif filename.endswith('.csv'):
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'title', 'done', 'due_date', 'time_spent'])
            writer.writeheader()
            for task in tasks:
                writer.writerow({
                    'id': task.id,
                    'title': task.title,
                    'done': str(task.done).lower(),
                    'due_date': task.due_date.isoformat() if task.due_date else '',
                    'time_spent': task.time_spent
                })