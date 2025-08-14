import argparse
import sys
from datetime import datetime, timedelta
from .todo import TodoList
from .storage import load_tasks, save_tasks, StorageError

def parse_due_date(date_str: str) -> datetime:
    """Parse due date from various formats."""
    formats = [
        '%Y-%m-%d',           # 2023-12-31
        '%Y-%m-%d %H:%M',     # 2023-12-31 14:30
        '%Y-%m-%d %H:%M:%S',  # 2023-12-31 14:30:00
        '%m/%d/%Y',           # 12/31/2023
        '%m/%d/%Y %H:%M',     # 12/31/2023 14:30
        '%d.%m.%Y',           # 31.12.2023
        '%d.%m.%Y %H:%M',     # 31.12.2023 14:30
    ]
    
    # Handle relative dates
    date_str = date_str.lower().strip()
    if date_str in ['today', 'now']:
        return datetime.now().replace(hour=23, minute=59, second=59)
    elif date_str == 'tomorrow':
        return (datetime.now() + timedelta(days=1)).replace(hour=23, minute=59, second=59)
    
    # Try parsing each format
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unrecognized date format: {date_str}")

def print_task(task, show_timer=True, show_time=True):
    """Print a formatted task line."""
    status = '[x]' if task.done else '[ ]'
    timer_indicator = " ⏰" if task.is_timer_running() else ""
    
    # Due date information
    due_info = ""
    if task.due_date:
        if task.is_overdue() and not task.done:
            due_info = f" [🔴 OVERDUE: {task.due_date.strftime('%Y-%m-%d %H:%M')}]"
        elif not task.done:
            due_info = f" [📅 Due: {task.due_date.strftime('%Y-%m-%d %H:%M')}]"
        else:
            due_info = f" [Due: {task.due_date.strftime('%Y-%m-%d %H:%M')}]"
    
    # Time information
    time_info = ""
    if show_time and task.time_spent > 0:
        time_info = f" [⏱️  {task.format_time_spent()}]"
    
    # Remaining time for incomplete tasks
    remaining_info = ""
    if not task.done and task.due_date and show_timer:
        remaining_info = f" [{task.format_remaining_time()}]"
    
    print(f"#{task.id} {status} {task.title}{due_info}{remaining_info}{time_info}{timer_indicator}")

def confirm_action(message: str) -> bool:
    """Ask for user confirmation."""
    response = input(f"{message} (y/N): ").lower().strip()
    return response in ['y', 'yes']

def main():
    parser = argparse.ArgumentParser(
        description='Todo CLI - A simple command-line task manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  todo add "Buy groceries" --due tomorrow
  todo add "Project deadline" --due "2024-03-15 09:00"
  todo list --upcoming
  todo start 1
  todo done 1
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Global options
    parser.add_argument('-f', '--file', default='tasks.json',
                       help='Task storage file (default: tasks.json)')
    parser.add_argument('--no-confirm', action='store_true',
                       help='Skip confirmation prompts')
    
    # Add task
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('title', help='Task description')
    add_parser.add_argument('-d', '--due', help='Due date (YYYY-MM-DD, MM/DD/YYYY, "tomorrow", etc.)')
    
    # List tasks
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('-a', '--all', action='store_true',
                           help='Show completed tasks')
    list_parser.add_argument('-u', '--upcoming', action='store_true',
                           help='Show upcoming tasks (next 3 days)')
    list_parser.add_argument('-o', '--overdue', action='store_true',
                           help='Show overdue tasks')
    list_parser.add_argument('--days', type=int, default=3,
                           help='Days ahead for upcoming tasks (default: 3)')
    
    # Mark done
    done_parser = subparsers.add_parser('done', help='Mark task as completed')
    done_parser.add_argument('task_id', type=int, help='Task ID')
    
    # Delete task
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('task_id', type=int, help='Task ID')
    
    # Timer commands
    start_parser = subparsers.add_parser('start', help='Start timer for a task')
    start_parser.add_argument('task_id', type=int, help='Task ID')
    
    stop_parser = subparsers.add_parser('stop', help='Stop timer for a task')
    stop_parser.add_argument('task_id', type=int, help='Task ID')
    
    # Time tracking
    time_parser = subparsers.add_parser('time', help='Show time tracking report')
    time_parser.add_argument('-s', '--summary', action='store_true',
                           help='Show summary only')
    
    # Remaining time
    remaining_parser = subparsers.add_parser('remaining', help='Check remaining time')
    remaining_parser.add_argument('task_id', type=int, help='Task ID')
    
    args = parser.parse_args()
    
    # Validate task ID if provided
    if hasattr(args, 'task_id') and args.task_id <= 0:
        print("Error: Task ID must be a positive integer", file=sys.stderr)
        return 1
    
    # Initialize todo list
    todo_list = TodoList()
    
    # Load existing tasks
    try:
        todo_list.tasks = load_tasks(args.file)
        if todo_list.tasks:
            todo_list.next_id = max(task.id for task in todo_list.tasks) + 1
    except StorageError as e:
        print(f"Error loading tasks: {e}", file=sys.stderr)
        if not args.no_confirm and not confirm_action("Continue with empty task list?"):
            return 1
    
    try:
        # Command handling
        if args.command == 'add':
            due_date = None
            if args.due:
                try:
                    due_date = parse_due_date(args.due)
                except ValueError as e:
                    print(f"Error: {e}", file=sys.stderr)
                    return 1
            
            task = todo_list.add_task(args.title, due_date)
            print(f"✅ Added task #{task.id}: {task.title}")
            if due_date:
                print(f"   📅 Due: {due_date.strftime('%Y-%m-%d %H:%M')}")
                print(f"   ⏰ {task.format_remaining_time()}")
        
        elif args.command == 'list':
            if args.upcoming:
                tasks = todo_list.get_upcoming_tasks(args.days)
                title = f"📅 Upcoming Tasks (next {args.days} days):"
            elif args.overdue:
                tasks = todo_list.get_overdue_tasks()
                title = "🔴 Overdue Tasks:"
            else:
                tasks = todo_list.list_tasks(args.all)
                title = "📝 All Tasks" if args.all else "📝 Active Tasks"
            
            if not tasks:
                print("No tasks found.")
                return 0
            
            print(title)
            for task in tasks:
                print_task(task)
        
        elif args.command == 'done':
            task = todo_list.mark_done(args.task_id)
            if task:
                print(f"✅ Completed task #{task.id}: {task.title}")
                if task.time_spent > 0:
                    print(f"   ⏱️  Total time spent: {task.format_time_spent()}")
            else:
                print(f"❌ Task #{args.task_id} not found or already completed")
                return 1
        
        elif args.command == 'delete':
            task = todo_list.find_task(args.task_id)
            if not task:
                print(f"❌ Task #{args.task_id} not found")
                return 1
            
            if not args.no_confirm and not confirm_action(f"Delete task #{task.id}: {task.title}?"):
                print("Cancelled.")
                return 0
            
            todo_list.delete_task(args.task_id)
            print(f"🗑️  Deleted task #{task.id}: {task.title}")
        
        elif args.command == 'start':
            task = todo_list.find_task(args.task_id)
            if not task:
                print(f"❌ Task #{args.task_id} not found")
                return 1
            
            if task.done:
                print(f"❌ Cannot start timer for completed task #{task.id}")
                return 1
            
            if todo_list.start_timer(args.task_id):
                print(f"⏰ Started timer for task #{task.id}: {task.title}")
            else:
                print(f"⏰ Timer already running for task #{task.id}")
        
        elif args.command == 'stop':
            task = todo_list.find_task(args.task_id)
            if not task:
                print(f"❌ Task #{args.task_id} not found")
                return 1
            
            elapsed = todo_list.stop_timer(args.task_id)
            if elapsed > 0:
                print(f"⏹️  Stopped timer for task #{task.id}: {task.title}")
                print(f"   ⏱️  Session time: {task._format_duration(elapsed)}")
                print(f"   📊 Total time: {task.format_time_spent()}")
            else:
                print(f"❌ No timer running for task #{task.id}")
        
        elif args.command == 'time':
            total_time = todo_list.get_total_time_spent()
            
            if args.summary:
                print(f"📊 Total time: {todo_list.tasks[0]._format_duration(total_time) if todo_list.tasks else '0s'}")
            else:
                print("📊 Time Tracking Report")
                print(f"Total time spent: {todo_list.tasks[0]._format_duration(total_time) if todo_list.tasks else '0s'}")
                print()
                
                for task in todo_list.tasks:
                    if task.time_spent > 0:
                        status = "✅" if task.done else "📝"
                        timer = " ⏰" if task.is_timer_running() else ""
                        print(f"{status} #{task.id} {task.title}: {task.format_time_spent()}{timer}")
        
        elif args.command == 'remaining':
            task = todo_list.find_task(args.task_id)
            if not task:
                print(f"❌ Task #{args.task_id} not found")
                return 1
            
            if task.done:
                print(f"✅ Task #{task.id} is completed")
            elif not task.due_date:
                print(f"📝 Task #{task.id} has no deadline")
            else:
                print(f"📝 Task #{task.id}: {task.title}")
                print(f"📅 Due: {task.due_date.strftime('%Y-%m-%d %H:%M')}")
                print(f"⏰ Status: {task.format_remaining_time()}")
        
        # Save tasks
        save_tasks(todo_list.tasks, args.file)
        
    except StorageError as e:
        print(f"Error saving tasks: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 0
    
    return 0

if __name__ == '__main__':
    sys.exit(main())