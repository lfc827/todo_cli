import json
import csv
import os
from datetime import datetime
from typing import List
from .todo import Task

class StorageError(Exception):
    """Custom exception for storage-related errors."""
    pass

def load_tasks(filename: str) -> List[Task]:
    """Load tasks from JSON or CSV file."""
    if not os.path.exists(filename):
        return []
    
    try:
        if filename.lower().endswith('.json'):
            return _load_json_tasks(filename)
        elif filename.lower().endswith('.csv'):
            return _load_csv_tasks(filename)
        else:
            raise StorageError(f"Unsupported file format: {filename}")
    except (json.JSONDecodeError, csv.Error) as e:
        raise StorageError(f"Error reading {filename}: {e}")
    except Exception as e:
        raise StorageError(f"Unexpected error loading {filename}: {e}")

def save_tasks(tasks: List[Task], filename: str) -> None:
    """Save tasks to JSON or CSV file."""
    try:
        # Create backup of existing file
        if os.path.exists(filename):
            backup_name = f"{filename}.backup"
            os.replace(filename, backup_name)
        
        if filename.lower().endswith('.json'):
            _save_json_tasks(tasks, filename)
        elif filename.lower().endswith('.csv'):
            _save_csv_tasks(tasks, filename)
        else:
            raise StorageError(f"Unsupported file format: {filename}")
            
    except Exception as e:
        raise StorageError(f"Error saving to {filename}: {e}")

def _load_json_tasks(filename: str) -> List[Task]:
    """Load tasks from JSON file."""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return [Task.from_dict(task_data) for task_data in data]

def _save_json_tasks(tasks: List[Task], filename: str) -> None:
    """Save tasks to JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump([task.to_dict() for task in tasks], f, indent=2, ensure_ascii=False)

def _load_csv_tasks(filename: str) -> List[Task]:
    """Load tasks from CSV file."""
    tasks = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            due_date = None
            if row.get('due_date'):
                due_date = datetime.fromisoformat(row['due_date'])
            
            task = Task(
                int(row['id']),
                row['title'],
                row.get('done', '').lower() == 'true',
                due_date
            )
            task.time_spent = float(row.get('time_spent', 0.0))
            tasks.append(task)
    return tasks

def _save_csv_tasks(tasks: List[Task], filename: str) -> None:
    """Save tasks to CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'title', 'done', 'due_date', 'time_spent']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for task in tasks:
            writer.writerow({
                'id': task.id,
                'title': task.title,
                'done': str(task.done).lower(),
                'due_date': task.due_date.isoformat() if task.due_date else '',
                'time_spent': task.time_spent
            })