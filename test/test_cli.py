import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from todo_cli.cli import main
from todo_cli.storage import load_tasks
from datetime import datetime, timedelta
import time

def run_command(capsys, command, file='tasks.json'):
    # Simulate command line arguments
    test_args = command.split()
    test_args.extend(['-f', file])
    
    # Preserve original sys.argv
    import sys
    original_argv = sys.argv
    
    try:
        sys.argv = ['cli.py'] + test_args
        main()
    finally:
        sys.argv = original_argv
    
    return capsys.readouterr()

# Test: Remaining time command
def test_cli_remaining_time(capsys, tmp_path):
    """Test that the 'remaining' command shows correct time until deadline"""
    test_file = tmp_path / "test_tasks.json"
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Add task with deadline
    run_command(capsys, f"add 'Important deadline' --due {tomorrow}", str(test_file))
    
    # Check remaining time
    run_command(capsys, "remaining 1", str(test_file))
    out, _ = capsys.readouterr()
    
    assert "Task #1: Important deadline" in out
    assert "Due date: " in out
    assert "1 day remaining" in out

# Test: Remaining time display in task list
def test_cli_list_remaining_time(capsys, tmp_path):
    """Test that task list shows remaining time for pending tasks"""
    test_file = tmp_path / "test_tasks.json"
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Add task with deadline
    run_command(capsys, f"add 'Task with deadline' --due {tomorrow}", str(test_file))
    
    # List tasks
    run_command(capsys, "list", str(test_file))
    out, _ = capsys.readouterr()
    
    assert "#1 [ ] Task with deadline" in out
    assert "1 day remaining" in out
    assert "Due: " in out

# Test: Overdue task handling
def test_cli_overdue_remaining_time(capsys, tmp_path):
    """Test proper detection and display of overdue tasks"""
    test_file = tmp_path / "test_tasks.json"
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Add overdue task
    run_command(capsys, f"add 'Overdue task' --due {yesterday}", str(test_file))
    
    # List tasks
    run_command(capsys, "list", str(test_file))
    out, _ = capsys.readouterr()
    
    assert "#1 [ ] Overdue task" in out
    assert "OVERDUE" in out
    assert "1 day overdue" in out

# Test: Edge case - task due in exactly 24 hours
def test_cli_exactly_24_hours_remaining(capsys, tmp_path):
    """Test boundary condition for 24-hour remaining mark"""
    test_file = tmp_path / "test_tasks.json"
    due_time = (datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M')
    
    run_command(capsys, f"add '24h Task' --due '{due_time}'", str(test_file))
    
    run_command(capsys, "remaining 1", str(test_file))
    out, _ = capsys.readouterr()
    
    assert "24 hours remaining" in out

# Test: Time formatting for multi-day periods
def test_cli_multi_day_formatting(capsys, tmp_path):
    """Test proper pluralization for multi-day remaining times"""
    test_file = tmp_path / "test_tasks.json"
    future_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
    
    run_command(capsys, f"add 'Multi-day Task' --due {future_date}", str(test_file))
    
    run_command(capsys, "remaining 1", str(test_file))
    out, _ = capsys.readouterr()
    
    assert "3 days remaining" in out