# Todo-CLI: Command Line Todo Manager

A powerful command-line task manager with support for task management, time tracking, and deadline reminders. Built with Python - simple to use yet feature-rich.

## ✨ Key Features

- ✅ **Task Management**: Add, view, complete, and delete tasks
- ⏱️ **Time Tracking**: Record actual time spent on tasks
- 📅 **Deadlines**: Set due dates and view remaining time
- 📊 **Time Reports**: View task time statistics
- 💾 **Data Persistence**: Automatic saving to JSON or CSV files
- 🔔 **Smart Reminders**: View upcoming and overdue tasks

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/todo-cli.git
cd todo-cli

# Install dependencies
pip install -r requirements.txt
```

# Add new task
python -m todo_cli.cli add "Write weekly report" --due "2023-12-15 17:00"

# List all tasks
python -m todo_cli.cli list

# Start task timer
python -m todo_cli.cli start 1

# Stop task timer
python -m todo_cli.cli stop 1

# Mark task as completed
python -m todo_cli.cli done 1

## 📖 Detailed Usage Guide

### Adding Tasks
```bash
python -m todo_cli.cli add "Task description" [--due due_date]
```
- Supports multiple time formats:：`YYYY-MM-DD`、`MM/DD/YYYY`、`DD.MM.YYYY`
- Example:：`python -m todo_cli.cli add "Prepare meeting" --due "2023-12-20 14:30"`

### Managing Tasks
| Command | Description | Example |
|------|------|------|
| `list` | List active tasks | `python -m todo_cli.cli list` |
| `list -a` | List all tasks (including completed) | `python -m todo_cli.cli list -a` |
| `list -u` | List upcoming tasks | `python -m todo_cli.cli list -u` |
| `list -o` | List overdue tasks | `python -m todo_cli.cli list -o` |
| `done <ID>` | Mark task as completed | `python -m todo_cli.cli done 3` |
| `delete <ID>` | Delete task | `python -m todo_cli.cli delete 2` |

### Time Tracking
```bash
# Start timer
python -m todo_cli.cli start <TaskID>

# Stop timer
python -m todo_cli.cli stop <TaskID>

# View time report
python -m todo_cli.cli time
```

### Checking Remaining Time
```bash
# Check time remaining for task
python -m todo_cli.cli remaining <TaskID>

# Sample output:
# Task #1: Write weekly report
# Due: 2023-12-15 17:00
# Status: 2 days 3 hours remaining
```

### Data Storage
Uses JSON format by default:
```bash
# Use CSV storage
python -m todo_cli.cli add "New task" -f tasks.csv

# Specify custom file
python -m todo_cli.cli list -f my_tasks.json
```

## 🧪 Running Tests
```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest tests/
```

## 🧩 项目结构
```
todo-cli/
├── todo_cli/          # Source code
│   ├── cli.py         # Command-line interface
│   ├── storage.py     # File storage
│   └── todo.py        # Core logic
├── tests/             # Unit tests
├── README.md          # This file
└── requirements.txt   # Dependency list
```

## 🤝 Contribution Guide
Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a new branch (git checkout -b feature/your-feature)
3. Commit your changes (git commit -m 'feat: Add new feature')
4. Push to branch (git push origin feature/your-feature)
5. Create a Pull Request

Commit messages should follow [Conventional Commits](https://www.conventionalcommits.org/) specification.

