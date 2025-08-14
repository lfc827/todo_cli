import pytest
import time
from datetime import datetime, timedelta
import tempfile
import os

from todo_cli.todo import TodoList, Task
from todo_cli.storage import save_tasks, load_tasks


@pytest.mark.slow
class TestPerformance:
    """Performance tests for todo CLI."""
    
    def test_large_task_list_operations(self):
        """Test operations with large number of tasks."""
        todo = TodoList()
        
        # Add 1000 tasks
        start_time = time.time()
        for i in range(1000):
            todo.add_task(f"Task {i}")
        add_time = time.time() - start_time
        
        assert add_time < 1.0, f"Adding 1000 tasks took {add_time:.2f}s, should be < 1s"
        assert len(todo.tasks) == 1000
        
        # Test finding tasks
        start_time = time.time()
        for i in range(0, 1000, 10):  # Test every 10th task
            task = todo.find_task(i + 1)
            assert task is not None
        find_time = time.time() - start_time
        
        assert find_time < 0.5, f"Finding 100 tasks took {find_time:.2f}s, should be < 0.5s"
        
        # Test listing tasks
        start_time = time.time()
        active_tasks = todo.list_tasks()
        list_time = time.time() - start_time
        
        assert list_time < 0.1, f"Listing tasks took {list_time:.2f}s, should be < 0.1s"
        assert len(active_tasks) == 1000
    
    def test_storage_performance(self):
        """Test storage performance with large datasets."""
        # Create large task list
        tasks = []
        for i in range(500):
            task = Task(i + 1, f"Performance task {i}")
            if i % 10 == 0:  # Every 10th task has due date
                task.due_date = datetime.now() + timedelta(days=i % 30)
            if i % 15 == 0:  # Every 15th task has time spent
                task.time_spent = float(i * 60)  # i minutes
            tasks.append(task)
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            json_file = f.name
        
        try:
            # Test JSON save performance
            start_time = time.time()
            save_tasks(tasks, json_file)
            save_time = time.time() - start_time
            
            assert save_time < 1.0, f"Saving 500 tasks took {save_time:.2f}s, should be < 1s"
            
            # Test JSON load performance
            start_time = time.time()
            loaded_tasks = load_tasks(json_file)
            load_time = time.time() - start_time
            
            assert load_time < 1.0, f"Loading 500 tasks took {load_time:.2f}s, should be < 1s"
            assert len(loaded_tasks) == 500
            
        finally:
            os.unlink(json_file)
    
    def test_timer_precision(self):
        """Test timer precision and performance."""
        task = Task(1, "Timer precision test")
        
        # Test multiple short timer sessions
        total_measured = 0
        total_actual = 0
        
        for _ in range(10):
            task.start_timer()
            start_time = time.time()
            
            time.sleep(0.01)  # 10ms sleep
            
            actual_elapsed = time.time() - start_time
            measured_elapsed = task.stop_timer()
            
            total_actual += actual_elapsed
            total_measured += measured_elapsed
        
        # Timer should be reasonably accurate (within 10% for short intervals)
        accuracy = abs(total_measured - total_actual) / total_actual
        assert accuracy < 0.1, f"Timer accuracy {accuracy:.1%} should be < 10%"