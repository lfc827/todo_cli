import json
import csv
import os
from datetime import datetime
from .todo import Task

def load_tasks(filename):
    # Return empty list if file doesn't exist
    if not os.path.exists(filename):
        return []
    
    # Handle JSON files
    tasks = []
    if filename.endswith('.json'):
        with open(filename, 'r') as f:
            data = json.load(f)     # Load JSON data

            # Convert each JSON object to Task instance
            for task_data in data:
                # Ensure optional fields exist in JSON
                if 'due_date' not in task_data:
                    task_data['due_date'] = None  # Default to None if missing
                if 'time_spent' not in task_data:
                    task_data['time_spent'] = 0.0  # Default to 0 if missing

                # Create Task instance from dictionary
                tasks.append(Task.from_dict(task_data))
    
    # Handle CSV files
    elif filename.endswith('.csv'):
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)

            # Process each row in CSV
            for row in reader:
                # Parse due_date from ISO format if exists
                due_date = datetime.fromisoformat(row['due_date']) if row['due_date'] else None
                
                # Create Task instance from CSV row
                task = Task(
                    id=int(row['id']),
                    title=row['title'],
                    done=row['done'].lower() == 'true',
                    due_date=due_date
                )
                # Handle time_spent field (optional in CSV)
                task.time_spent = float(row.get('time_spent', 0.0))
                tasks.append(task)
    return tasks

def save_tasks(tasks, filename):

    # Handle JSON files
    if filename.endswith('.json'):
        with open(filename, 'w') as f:
            # Convert tasks to dictionaries and write as pretty-printed JSON
            json.dump([task.to_dict() for task in tasks], f, indent=2)
    
    # Handle CSV files
    elif filename.endswith('.csv'):
        with open(filename, 'w', newline='') as f:
            # Define CSV column headers
            writer = csv.DictWriter(f, fieldnames=['id', 'title', 'done', 'due_date', 'time_spent'])
            writer.writeheader()
            
            # Write each task as a CSV row
            for task in tasks:
                writer.writerow({
                    'id': task.id,
                    'title': task.title,
                    'done': str(task.done).lower(),
                    'due_date': task.due_date.isoformat() if task.due_date else '',
                    'time_spent': task.time_spent
                })