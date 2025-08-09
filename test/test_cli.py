import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import shlex
from todo_cli.cli import main
from todo_cli.storage import load_tasks
from datetime import datetime, timedelta
import time

def run_command(capsys, *args, file='tasks.json'):
    """Execute CLI command with given arguments and capture output"""
    # Preserve original sys.argv
    original_argv = sys.argv
    
    try:
        # Build command arguments: program name + passed args + file option
        command_args = ['cli.py'] + list(args) + ['-f', file]
        sys.argv = command_args
        
        # Execute main CLI function
        main()
    finally:
        # Restore original arguments
        sys.argv = original_argv
    
    # Return captured stdout/stderr
    return capsys.readouterr()

# Test: Verify 'remaining' command shows correct time until deadline
def test_cli_remaining_time(capsys, tmp_path):
    test_file = tmp_path / "test_tasks.json"
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Add task with deadline using separate arguments
    run_command(capsys, 'add', 'Important deadline', '--due', tomorrow, file=str(test_file))
    
    # Check remaining time
    run_command(capsys, 'remaining', '1', file=str(test_file))
    out, _ = capsys.readouterr()
    
    # Verify expected output elements
    assert "Task #1: Important deadline" in out
    assert "Due date:" in out
    assert "1 day" in out  # Check for time remaining indication

# Test: Verify task list shows remaining time for pending tasks
def test_cli_list_remaining_time(capsys, tmp_path):
    test_file = tmp_path / "test_tasks.json"
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Add task with deadline
    run_command(capsys, 'add', 'Task with deadline', '--due', tomorrow, file=str(test_file))
    
    # List tasks
    run_command(capsys, 'list', file=str(test_file))
    out, _ = capsys.readouterr()
    
    # Verify task display includes remaining time
    assert "#1 [ ] Task with deadline" in out
    assert "Due:" in out
    assert "remaining" in out

# Test: Verify proper detection and display of overdue tasks
def test_cli_overdue_remaining_time(capsys, tmp_path):
    test_file = tmp_path / "test_tasks.json"
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Add overdue task
    run_command(capsys, 'add', 'Overdue task', '--due', yesterday, file=str(test_file))
    
    # List tasks
    run_command(capsys, 'list', file=str(test_file))
    out, _ = capsys.readouterr()
    
    # Verify overdue indicators
    assert "#1 [ ] Overdue task" in out
    assert "OVERDUE" in out
    assert "overdue" in out

# Test: Verify boundary condition for 24-hour remaining mark
def test_cli_exactly_24_hours_remaining(capsys, tmp_path):
    test_file = tmp_path / "test_tasks.json"
    due_time = (datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M')
    
    # Add task due in exactly 24 hours
    run_command(capsys, 'add', '24h Task', '--due', due_time, file=str(test_file))
    
    # Check remaining time
    run_command(capsys, 'remaining', '1', file=str(test_file))
    out, _ = capsys.readouterr()
    
    # Verify time display (either "1 day" or "24 hours" is acceptable)
    assert "1 day" in out or "24 hours" in out

# Test: Verify proper pluralization for multi-day remaining times
def test_cli_multi_day_formatting(capsys, tmp_path):
    test_file = tmp_path / "test_tasks.json"
    future_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
    
    # Add task due in 3 days
    run_command(capsys, 'add', 'Multi-day Task', '--due', future_date, file=str(test_file))
    
    # Check remaining time
    run_command(capsys, 'remaining', '1', file=str(test_file))
    out, _ = capsys.readouterr()
    
    # Verify plural day format
    assert "3 days" in out


