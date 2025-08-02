import argparse
from .todo import TodoList
from .storage import load_tasks, save_tasks

def main():
    parser = argparse.ArgumentParser(description='Command-line Todo Manager')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Add task
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('title', help='Task description')
    
    # List tasks
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('-a', '--all', action='store_true', help='Show all tasks including completed')
    
    # Mark task as done
    done_parser = subparsers.add_parser('done', help='Mark task as completed')
    done_parser.add_argument('task_id', type=int, help='ID of task to mark as done')
    
    # Delete task
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('task_id', type=int, help='ID of task to delete')
    
    # File options
    parser.add_argument('-f', '--file', default='tasks.json', 
                        help='Task storage file (JSON/CSV), default: tasks.json')
    
    args = parser.parse_args()
    todo_list = TodoList()