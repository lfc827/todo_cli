import argparse
from datetime import datetime, timedelta
from .todo import TodoList
from .storage import load_tasks, save_tasks

def parse_due_date(date_str):
    formats = [
        '%Y-%m-%d',          # 2023-12-31
        '%Y-%m-%d %H:%M',    # 2023-12-31 14:30
        '%m/%d/%Y',          # 12/31/2023
        '%m/%d/%Y %H:%M',    # 12/31/2023 14:30
        '%d.%m.%Y',          # 31.12.2023
        '%d.%m.%Y %H:%M',    # 31.12.2023 14:30
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unrecognized date format: {date_str}")

def main():
    parser = argparse.ArgumentParser(description='Command-line Todo Manager')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Add task
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('title', help='Task description')
    add_parser.add_argument('-d', '--due', help='Due date (format: YYYY-MM-DD or MM/DD/YYYY)')

    # List tasks
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('-a', '--all', action='store_true', help='Show all tasks including completed')
    list_parser.add_argument('-u', '--upcoming', action='store_true', help='Show upcoming tasks')
    list_parser.add_argument('-o', '--overdue', action='store_true', help='Show overdue tasks')

    # Mark task as done
    done_parser = subparsers.add_parser('done', help='Mark task as completed')
    done_parser.add_argument('task_id', type=int, help='ID of task to mark as done')
    
    # Delete task
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('task_id', type=int, help='ID of task to delete')
    
    # Timer commands
    start_parser = subparsers.add_parser('start', help='Start timer for a task')
    start_parser.add_argument('task_id', type=int, help='ID of task to start timer')
    
    stop_parser = subparsers.add_parser('stop', help='Stop timer for a task')
    stop_parser.add_argument('task_id', type=int, help='ID of task to stop timer')


    # Show timer
    time_parser = subparsers.add_parser('time', help='Show time tracking report')
    time_parser.add_argument('-s', '--summary', action='store_true', help='Show time summary only')
    
    remaining_parser = subparsers.add_parser('remaining', help='Check remaining time for a task')
    remaining_parser.add_argument('task_id', type=int, help='ID of task to check remaining time')
    
    # File options
    parser.add_argument('-f', '--file', default='tasks.json', 
                        help='Task storage file (JSON/CSV), default: tasks.json')
    
    args = parser.parse_args()
    todo_list = TodoList()

    # Load existing tasks
    try:
        todo_list.tasks = load_tasks(args.file)
        if todo_list.tasks:
            todo_list.next_id = max(task.id for task in todo_list.tasks) + 1
    except FileNotFoundError:
        pass

    # Command handling
    if args.command == 'add':
        due_date = None
        if args.due:
            try:
                due_date = parse_due_date(args.due)
            except ValueError as e:
                print(f"Error: {e}")
                print("Valid date formats: YYYY-MM-DD, MM/DD/YYYY, DD.MM.YYYY")
                return
        
        task = todo_list.add_task(args.title, due_date)
        print(f'Added task #{task.id}: {task.title}')
        if due_date:
            print(f"  Due: {due_date.strftime('%Y-%m-%d %H:%M')}")
            print(f"  {task.format_remaining_time()}")
    
    elif args.command == 'list':
        if args.upcoming:
            tasks = todo_list.get_upcoming_tasks()
            title = "Upcoming Tasks (next 3 days):"
        elif args.overdue:
            tasks = [task for task in todo_list.tasks if task.is_overdue()]
            title = "Overdue Tasks:"
        else:
            tasks = todo_list.list_tasks(args.all)
            title = "All Tasks" if args.all else "Active Tasks"
        
        if not tasks:
            suffix = ""
            if args.upcoming:
                suffix = " (use 'add' command with --due to add tasks with due dates)"
            elif args.overdue:
                suffix = " (use 'list --all' to see all tasks)"
            print(f'No tasks found{suffix}')
            return
            
        print(title)
        for task in tasks:
            status = '[x]' if task.done else '[ ]'
            timer = " (timer running)" if task.timer_start else ""
            due_info = ""
            time_info = f" [Time: {task.format_time_spent()}]" if task.time_spent > 0 else ""
            
            remaining_info = ""
            if task.due_date and not task.done:
                remaining_info = f" [{task.format_remaining_time()}]"
            
            if task.due_date:
                due_str = task.due_date.strftime('%Y-%m-%d %H:%M')
                if task.is_overdue():
                    due_info = f" [OVERDUE: {due_str}]"
                else:
                    due_info = f" [Due: {due_str}]"
            
            print(f'#{task.id} {status} {task.title}{due_info}{remaining_info}{time_info}{timer}')
    
    elif args.command == 'done':
        task = todo_list.mark_done(args.task_id)
        if task:
            print(f'Marked task #{task.id} as done: {task.title}')
        else:
            print(f'Task #{args.task_id} not found')
    
    elif args.command == 'delete':
        task = todo_list.delete_task(args.task_id)
        if task:
            print(f'Deleted task #{task.id}: {task.title}')
        else:
            print(f'Task #{args.task_id} not found')
    
    elif args.command == 'start':
        success = todo_list.start_timer(args.task_id)
        task = todo_list.find_task(args.task_id)
        if success:
            print(f'Timer started for task #{task.id}: {task.title}')
        elif task and task.done:
            print(f"Cannot start timer for completed task #{task.id}")
        else:
            print(f'Task #{args.task_id} not found or timer already running')
    
    elif args.command == 'stop':
        elapsed = todo_list.stop_timer(args.task_id)
        task = todo_list.find_task(args.task_id)
        if elapsed > 0:
            print(f'Timer stopped for task #{task.id}: {task.title}')
            print(f"  Time spent: {timedelta(seconds=int(elapsed))}")
            print(f"  Total time: {task.format_time_spent()}")
        elif task and task.timer_start:
            print(f"Timer was not running for task #{task.id}")
        else:
            print(f'Task #{args.task_id} not found')
    
    elif args.command == 'time':
        total_seconds = todo_list.get_total_time_spent()
        total_time = timedelta(seconds=int(total_seconds))
        
        if args.summary:
            print(f"Total time spent on all tasks: {total_time}")
        else:
            print("Time Tracking Report:")
            print(f"Total time spent: {total_time}\n")
            
            for task in todo_list.tasks:
                if task.time_spent > 0:
                    time_info = task.format_time_spent()
                    status = "Completed" if task.done else "Active"
                    print(f"#{task.id} {task.title} ({status}): {time_info}")
    
    elif args.command == 'remaining':
        task = todo_list.find_task(args.task_id)
        if task:
            if task.done:
                print(f"任务 #{task.id} 已完成，无剩余时间")
            elif not task.due_date:
                print(f"任务 #{task.id} 未设置截止时间")
            else:
                print(f"任务 #{task.id}: {task.title}")
                print(f"截止时间: {task.due_date.strftime('%Y-%m-%d %H:%M')}")
                print(f"状态: {task.format_remaining_time()}")
        else:
            print(f"任务 #{args.task_id} 不存在")
    
    # Save tasks
    save_tasks(todo_list.tasks, args.file)