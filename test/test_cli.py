import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
import tempfile
import os
import sys
from io import StringIO

from todo_cli.cli import main, parse_due_date


@pytest.fixture
def temp_task_file():
    """Create a temporary task file."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        yield f.name
    try:
        os.unlink(f.name)
    except FileNotFoundError:
        pass


def run_cli_command(args, task_file=None):
    """
    Helper function to run CLI commands and capture output.
    Returns (exit_code, stdout, stderr).
    """
    if task_file is None:
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            task_file = f.name
    
    # Add file argument
    full_args = ['cli.py'] + args + ['-f', task_file]
    
    # Capture stdout and stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    old_argv = sys.argv
    
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    
    try:
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        sys.argv = full_args
        
        exit_code = main()
        
    except SystemExit as e:
        exit_code = e.code
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        sys.argv = old_argv
        
        # Cleanup temp file if we created it
        if task_file != f.name:
            try:
                os.unlink(task_file)
            except FileNotFoundError:
                pass
    
    return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()


class TestDateParsing:
    """Test date parsing functionality."""
    
    def test_parse_iso_dates(self):
        """Test parsing ISO format dates."""
        # Date only
        result = parse_due_date('2024-12-31')
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 31
        
        # Date with time
        result = parse_due_date('2024-12-31 14:30')
        assert result.hour == 14
        assert result.minute == 30
        
        # Date with seconds
        result = parse_due_date('2024-12-31 14:30:45')
        assert result.second == 45
    
    def test_parse_us_dates(self):
        """Test parsing US format dates."""
        result = parse_due_date('12/31/2024')
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 31
        
        result = parse_due_date('12/31/2024 14:30')
        assert result.hour == 14
        assert result.minute == 30
    
    def test_parse_european_dates(self):
        """Test parsing European format dates."""
        result = parse_due_date('31.12.2024')
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 31
        
        result = parse_due_date('31.12.2024 14:30')
        assert result.hour == 14
        assert result.minute == 30
    
    def test_parse_relative_dates(self):
        """Test parsing relative dates."""
        now = datetime.now()
        
        # Today
        result = parse_due_date('today')
        assert result.date() == now.date()
        assert result.hour == 23
        assert result.minute == 59
        
        # Tomorrow
        result = parse_due_date('tomorrow')
        expected = now + timedelta(days=1)
        assert result.date() == expected.date()
        assert result.hour == 23
        assert result.minute == 59
        
        # Case insensitive
        result = parse_due_date('TODAY')
        assert result.date() == now.date()
    
    def test_parse_invalid_dates(self):
        """Test parsing invalid date formats."""
        with pytest.raises(ValueError, match="Unrecognized date format"):
            parse_due_date('invalid-date')
        
        with pytest.raises(ValueError, match="Unrecognized date format"):
            parse_due_date('2024-13-01')  # Invalid month
        
        with pytest.raises(ValueError, match="Unrecognized date format"):
            parse_due_date('32/01/2024')  # Invalid day


class TestCLIAdd:
    """Test CLI add command."""
    
    def test_add_simple_task(self, temp_task_file):
        """Test adding a simple task without due date."""
        exit_code, stdout, stderr = run_cli_command(
            ['add', 'Buy groceries'], temp_task_file
        )
        
        assert exit_code == 0
        assert "Added task #1" in stdout
        assert "Buy groceries" in stdout
        assert stderr == ""
    
    def test_add_task_with_due_date(self, temp_task_file):
        """Test adding task with due date."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        exit_code, stdout, stderr = run_cli_command(
            ['add', 'Important task', '--due', tomorrow], temp_task_file
        )
        
        assert exit_code == 0
        assert "Added task #1" in stdout
        assert "Important task" in stdout
        assert "Due:" in stdout
        assert "remaining" in stdout
    
    def test_add_task_with_relative_date(self, temp_task_file):
        """Test adding task with relative due date."""
        exit_code, stdout, stderr = run_cli_command(
            ['add', 'Do today', '--due', 'today'], temp_task_file
        )
        
        assert exit_code == 0
        assert "Added task #1" in stdout
        assert "Due:" in stdout
    
    def test_add_task_invalid_date(self, temp_task_file):
        """Test adding task with invalid due date."""
        exit_code, stdout, stderr = run_cli_command(
            ['add', 'Task', '--due', 'invalid-date'], temp_task_file
        )
        
        assert exit_code == 1
        assert "Error:" in stderr
        assert "Unrecognized date format" in stderr
    
    def test_add_multiple_tasks(self, temp_task_file):
        """Test adding multiple tasks."""
        # Add first task
        exit_code, stdout, stderr = run_cli_command(
            ['add', 'First task'], temp_task_file
        )
        assert exit_code == 0
        assert "task #1" in stdout
        
        # Add second task
        exit_code, stdout, stderr = run_cli_command(
            ['add', 'Second task'], temp_task_file
        )
        assert exit_code == 0
        assert "task #2" in stdout


class TestCLIList:
    """Test CLI list command."""
    
    def setup_test_tasks(self, temp_task_file):
        """Helper to set up test tasks."""
        now = datetime.now()
        
        # Add various tasks
        run_cli_command(['add', 'Active task'], temp_task_file)
        run_cli_command(['add', 'Completed task'], temp_task_file)
        run_cli_command(['done', '2'], temp_task_file)  # Mark as completed
        
        tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')
        run_cli_command(['add', 'Tomorrow task', '--due', tomorrow], temp_task_file)
        
        yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
        run_cli_command(['add', 'Overdue task', '--due', yesterday], temp_task_file)
    
    def test_list_active_tasks(self, temp_task_file):
        """Test listing active tasks (default)."""
        self.setup_test_tasks(temp_task_file)
        
        exit_code, stdout, stderr = run_cli_command(['list'], temp_task_file)
        
        assert exit_code == 0
        assert "Active Tasks" in stdout
        assert "#1 [ ] Active task" in stdout
        assert "#3 [ ] Tomorrow task" in stdout
        assert "#4 [ ] Overdue task" in stdout
        assert "Completed task" not in stdout  # Should not show completed
    
    def test_list_all_tasks(self, temp_task_file):
        """Test listing all tasks including completed."""
        self.setup_test_tasks(temp_task_file)
        
        exit_code, stdout, stderr = run_cli_command(['list', '--all'], temp_task_file)
        
        assert exit_code == 0
        assert "All Tasks" in stdout
        assert "#2 [x] Completed task" in stdout
        assert "Active task" in stdout
    
    def test_list_upcoming_tasks(self, temp_task_file):
        """Test listing upcoming tasks."""
        self.setup_test_tasks(temp_task_file)
        
        exit_code, stdout, stderr = run_cli_command(['list', '--upcoming'], temp_task_file)
        
        assert exit_code == 0
        assert "Upcoming Tasks" in stdout
        assert "Tomorrow task" in stdout
        assert "Overdue task" not in stdout  # Overdue tasks not in upcoming
    
    def test_list_overdue_tasks(self, temp_task_file):
        """Test listing overdue tasks."""
        self.setup_test_tasks(temp_task_file)
        
        exit_code, stdout, stderr = run_cli_command(['list', '--overdue'], temp_task_file)
        
        assert exit_code == 0
        assert "Overdue Tasks" in stdout
        assert "Overdue task" in stdout
        assert "OVERDUE" in stdout
        assert "Tomorrow task" not in stdout
    
    def test_list_empty(self, temp_task_file):
        """Test listing when no tasks exist."""
        exit_code, stdout, stderr = run_cli_command(['list'], temp_task_file)
        
        assert exit_code == 0
        assert "No tasks found" in stdout


class TestCLITaskOperations:
    """Test CLI task operations (done, delete, etc.)."""
    
    def test_mark_task_done(self, temp_task_file):
        """Test marking task as done."""
        # Add a task
        run_cli_command(['add', 'Complete me'], temp_task_file)
        
        # Mark as done
        exit_code, stdout, stderr = run_cli_command(['done', '1'], temp_task_file)
        
        assert exit_code == 0
        assert "Completed task #1" in stdout
        assert "Complete me" in stdout
        
        # Verify task is marked done
        exit_code, stdout, stderr = run_cli_command(['list', '--all'], temp_task_file)
        assert "[x]" in stdout
    
    def test_mark_nonexistent_task_done(self, temp_task_file):
        """Test marking non-existent task as done."""
        exit_code, stdout, stderr = run_cli_command(['done', '999'], temp_task_file)
        
        assert exit_code == 1
        assert "not found" in stdout
    
    def test_delete_task(self, temp_task_file):
        """Test deleting a task."""
        # Add a task
        run_cli_command(['add', 'Delete me'], temp_task_file)
        
        # Delete with confirmation bypass
        exit_code, stdout, stderr = run_cli_command(
            ['delete', '1', '--no-confirm'], temp_task_file
        )
        
        assert exit_code == 0
        assert "Deleted task #1" in stdout
        assert "Delete me" in stdout
        
        # Verify task is gone
        exit_code, stdout, stderr = run_cli_command(['list'], temp_task_file)
        assert "No tasks found" in stdout
    
    def test_delete_nonexistent_task(self, temp_task_file):
        """Test deleting non-existent task."""
        exit_code, stdout, stderr = run_cli_command(
            ['delete', '999', '--no-confirm'], temp_task_file
        )
        
        assert exit_code == 1
        assert "not found" in stdout


class TestCLITimerOperations:
    """Test CLI timer operations."""
    
    def test_start_stop_timer(self, temp_task_file):
        """Test starting and stopping timer."""
        # Add a task
        run_cli_command(['add', 'Timer task'], temp_task_file)
        
        # Start timer
        exit_code, stdout, stderr = run_cli_command(['start', '1'], temp_task_file)
        assert exit_code == 0
        assert "Started timer" in stdout
        assert "Timer task" in stdout
        
        # Stop timer
        exit_code, stdout, stderr = run_cli_command(['stop', '1'], temp_task_file)
        assert exit_code == 0
        assert "Stopped timer" in stdout
        assert "Session time:" in stdout
        assert "Total time:" in stdout
    
    def test_start_timer_completed_task(self, temp_task_file):
        """Test starting timer for completed task."""
        # Add and complete a task
        run_cli_command(['add', 'Completed task'], temp_task_file)
        run_cli_command(['done', '1'], temp_task_file)
        
        # Try to start timer
        exit_code, stdout, stderr = run_cli_command(['start', '1'], temp_task_file)
        
        assert exit_code == 1
        assert "Cannot start timer for completed task" in stdout
    
    def test_stop_timer_not_running(self, temp_task_file):
        """Test stopping timer that's not running."""
        run_cli_command(['add', 'No timer task'], temp_task_file)
        
        exit_code, stdout, stderr = run_cli_command(['stop', '1'], temp_task_file)
        
        assert exit_code == 1
        assert "No timer running" in stdout
    
    def test_timer_nonexistent_task(self, temp_task_file):
        """Test timer operations on non-existent task."""
        exit_code, stdout, stderr = run_cli_command(['start', '999'], temp_task_file)
        assert exit_code == 1
        assert "not found" in stdout
        
        exit_code, stdout, stderr = run_cli_command(['stop', '999'], temp_task_file)
        assert exit_code == 1
        assert "not found" in stdout


class TestCLITimeReporting:
    """Test CLI time reporting commands."""
    
    def test_time_report(self, temp_task_file):
        """Test time tracking report."""
        # Add tasks with some time
        run_cli_command(['add', 'Task 1'], temp_task_file)
        run_cli_command(['add', 'Task 2'], temp_task_file)
        
        # Simulate some time tracking (would need to mock actual timer)
        exit_code, stdout, stderr = run_cli_command(['time'], temp_task_file)
        
        assert exit_code == 0
        assert "Time Tracking Report" in stdout
        assert "Total time spent:" in stdout
    
    def test_time_summary(self, temp_task_file):
        """Test time summary report."""
        run_cli_command(['add', 'Task'], temp_task_file)
        
        exit_code, stdout, stderr = run_cli_command(['time', '--summary'], temp_task_file)
        
        assert exit_code == 0
        assert "Total time:" in stdout
        assert "Time Tracking Report" not in stdout  # Should be summary only
    
    def test_remaining_time(self, temp_task_file):
        """Test remaining time command."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        run_cli_command(['add', 'Due tomorrow', '--due', tomorrow], temp_task_file)
        
        exit_code, stdout, stderr = run_cli_command(['remaining', '1'], temp_task_file)
        
        assert exit_code == 0
        assert "Task #1: Due tomorrow" in stdout
        assert "Due:" in stdout
        assert "Status:" in stdout
    
    def test_remaining_time_no_due_date(self, temp_task_file):
        """Test remaining time for task with no due date."""
        run_cli_command(['add', 'No deadline'], temp_task_file)
        
        exit_code, stdout, stderr = run_cli_command(['remaining', '1'], temp_task_file)
        
        assert exit_code == 0
        assert "has no deadline" in stdout
    
    def test_remaining_time_completed_task(self, temp_task_file):
        """Test remaining time for completed task."""
        run_cli_command(['add', 'Done task'], temp_task_file)
        run_cli_command(['done', '1'], temp_task_file)
        
        exit_code, stdout, stderr = run_cli_command(['remaining', '1'], temp_task_file)
        
        assert exit_code == 0
        assert "is completed" in stdout


class TestCLIErrorHandling:
    """Test CLI error handling."""
    
    def test_invalid_task_id(self, temp_task_file):
        """Test invalid task ID handling."""
        exit_code, stdout, stderr = run_cli_command(['done', '0'], temp_task_file)
        assert exit_code == 1
        assert "must be a positive integer" in stderr
        
        exit_code, stdout, stderr = run_cli_command(['done', '-1'], temp_task_file)
        assert exit_code == 1
        assert "must be a positive integer" in stderr
    
    def test_missing_arguments(self, temp_task_file):
        """Test missing required arguments."""
        # This would typically cause ArgumentParser to exit
        with pytest.raises(SystemExit):
            run_cli_command(['add'], temp_task_file)  # Missing title
    
    @patch('todo_cli.storage.load_tasks', side_effect=Exception("Storage error"))
    def test_storage_error_handling(self, mock_load, temp_task_file):
        """Test handling of storage errors."""
        exit_code, stdout, stderr = run_cli_command(['list'], temp_task_file)
        
        assert exit_code == 1
        assert "Error loading tasks" in stderr
    
    def test_keyboard_interrupt(self, temp_task_file):
        """Test handling of keyboard interrupt."""
        with patch('todo_cli.cli.main', side_effect=KeyboardInterrupt()):
            exit_code, stdout, stderr = run_cli_command(['list'], temp_task_file)
            assert exit_code == 0
            assert "Goodbye!" in stdout


class TestCLIIntegration:
    """Integration tests for CLI functionality."""
    
    def test_full_workflow(self, temp_task_file):
        """Test a complete workflow with multiple operations."""
        # Add tasks
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        run_cli_command(['add', 'First task'], temp_task_file)
        run_cli_command(['add', 'Second task', '--due', tomorrow], temp_task_file)
        run_cli_command(['add', 'Third task'], temp_task_file)
        
        # Start timer on first task
        run_cli_command(['start', '1'], temp_task_file)
        
        # List tasks
        exit_code, stdout, stderr = run_cli_command(['list'], temp_task_file)
        assert exit_code == 0
        assert "⏰" in stdout  # Timer indicator
        
        # Complete first task (should stop timer)
        run_cli_command(['done', '1'], temp_task_file)
        
        # Delete third task
        run_cli_command(['delete', '3', '--no-confirm'], temp_task_file)
        
        # List remaining tasks
        exit_code, stdout, stderr = run_cli_command(['list', '--all'], temp_task_file)
        assert "First task" in stdout
        assert "[x]" in stdout  # Completed
        assert "Second task" in stdout
        assert "Third task" not in stdout  # Deleted
    
    def test_unicode_task_titles(self, temp_task_file):
        """Test CLI with Unicode task titles."""
        # Add tasks with various Unicode characters
        run_cli_command(['add', 'Tâche française'], temp_task_file)
        run_cli_command(['add', 'タスク日本語'], temp_task_file)
        run_cli_command(['add', 'Задача русский'], temp_task_file)
        
        # List and verify
        exit_code, stdout, stderr = run_cli_command(['list'], temp_task_file)
        assert exit_code == 0
        assert 'Tâche française' in stdout
        assert 'タスク日本語' in stdout
        assert 'Задача русский' in stdout


