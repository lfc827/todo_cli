# Todo CLI - Command Line Task Manager

Todo CLI is a powerful, feature-rich command-line task manager designed for productivity enthusiasts who prefer terminal-based tools. With support for deadlines, time tracking, and intuitive task management, it helps you stay organized without leaving your terminal.


## ✨ Key Features


- ✅**Task Management**: Create, view, complete, and delete tasks
- 📅**Smart Deadlines**: Supports absolute dates (2024-12-31) and relative dates (tomorrow)
- ⏱️**Time Tracking**: Start/stop timers to track time spent on tasks
- 🔔**Prioritization**: Visual indicators for overdue and upcoming tasks
- 💾**Custom Storage**: JSON or CSV file formats with automatic backups
- 📋**Detailed Reporting**: Time tracking summaries and remaining time calculations
- 🌍**Unicode Support**: Works with international characters and emojis

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/todo-cli.git
   cd todo-cli
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Make the script executable:
   ```bash
   chmod +x todo_cli/cli.py
   ```

4. Add alias to your shell profile (`.bashrc` or `.zshrc`):
   ```bash
   alias todo="python /path/to/todo-cli/todo_cli/cli.py"
   ```

## 🚀 Getting Started

### Basic Workflow
```bash
# Add a new task
todo add "Buy groceries" --due tomorrow

# List active tasks
todo list

# Mark task as completed
todo done 1

# Delete a task
todo delete 1 --no-confirm
```

### Advanced Features
```bash
# Start timer for a task
todo start 2

# Stop timer and record time
todo stop 2

# View time tracking report
todo time

# Check remaining time for a task
todo remaining 3

# List upcoming tasks (next 3 days)
todo list --upcoming

# List overdue tasks
todo list --overdue
```

### 📋 Managing Tasks

| Command | Description | Example |
|---------|-------------|---------|
| `add "Title"` | Add a new task | `python -m todo_cli.cli add "Buy milk"` |
| `add "Title" --due <DATE>` | Add task with deadline | `python -m todo_cli.cli add "Submit report" --due 2024-06-30` |
| `list` | List active tasks | `python -m todo_cli.cli list` |
| `list -a` | List all tasks (including completed) | `python -m todo_cli.cli list -a` |
| `list -u` | List upcoming tasks | `python -m todo_cli.cli list -u` |
| `list -o` | List overdue tasks | `python -m todo_cli.cli list -o` |
| `done <ID>` | Mark task as completed | `python -m todo_cli.cli done 3` |
| `delete <ID>` | Delete a task | `python -m todo_cli.cli delete 2` |
| `start <ID>` | Start timer for task | `python -m todo_cli.cli start 5` |
| `stop <ID>` | Stop timer for task | `python -m todo_cli.cli stop 5` |
| `time` | Show time tracking report | `python -m todo_cli.cli time` |
| `time --summary` | Show time summary only | `python -m todo_cli.cli time --summary` |
| `remaining <ID>` | Check remaining time for task | `python -m todo_cli.cli remaining 4` |

### Key Options
- **Date Formats**: Use `today`, `tomorrow`, `YYYY-MM-DD`, `MM/DD/YYYY`, or `DD.MM.YYYY`  
- **Global Options**:  
  `-f FILE` - Specify storage file (default: tasks.json)  
  `--no-confirm` - Skip confirmation prompts

## 💾 Data Storage

Tasks are stored in either JSON or CSV format (determined by file extension). The default storage file is `tasks.json`.

### Storage Features:
- 🔄 Automatic backups (creates `.backup` files before saving)
- 📁 Supports both JSON and CSV formats
- 🌐 Full Unicode support
- ⚡ Efficient handling of large task lists

## 🧪 Testing & Quality

The test suite includes unit tests, integration tests, and performance tests:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_cli.py       # CLI command tests
pytest tests/test_storage.py   # Storage system tests
pytest tests/test_todo.py      # Core logic tests

# Run performance tests (marked as slow)
pytest -m slow
```

## 🧩 Project Structure
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


Commit Guidelines:

1. Use [Conventional Commits](https://www.conventionalcommits.org/)
2. Keep commits atomic and focused
3. Include tests for new features

