# Todo-CLI: 命令行待办事项管理器


一个功能强大的命令行待办事项管理器，支持任务管理、时间跟踪和截止日期提醒。使用 Python 开发，简单易用但功能丰富。

## ✨ 功能亮点

- ✅ **任务管理**：添加、查看、完成、删除任务
- ⏱️ **时间跟踪**：记录任务实际花费时间
- 📅 **截止日期**：设置任务截止时间并查看剩余时间
- 📊 **时间报告**：查看任务耗时统计
- 💾 **数据持久化**：自动保存到 JSON 或 CSV 文件
- 🔔 **智能提醒**：查看即将到期和已过期任务

## 🚀 快速开始

### 前置条件
- Python 3.7 或更高版本

### 安装
```bash
# 克隆仓库
git clone https://github.com/yourusername/todo-cli.git
cd todo-cli

# 安装依赖
pip install -r requirements.txt
```

### 基本使用
```bash
# 添加新任务
python -m todo_cli.cli add "写周报" --due "2023-12-15 17:00"

# 列出所有任务
python -m todo_cli.cli list

# 开始任务计时
python -m todo_cli.cli start 1

# 停止任务计时
python -m todo_cli.cli stop 1

# 标记任务完成
python -m todo_cli.cli done 1
```

## 📖 详细使用指南

### 添加任务
```bash
python -m todo_cli.cli add "任务描述" [--due 截止时间]
```
- 支持多种时间格式：`YYYY-MM-DD`、`MM/DD/YYYY`、`DD.MM.YYYY`
- 示例：`python -m todo_cli.cli add "准备会议" --due "2023-12-20 14:30"`

### 管理任务
| 命令 | 描述 | 示例 |
|------|------|------|
| `list` | 列出任务 | `python -m todo_cli.cli list` |
| `list -a` | 列出所有任务（含已完成） | `python -m todo_cli.cli list -a` |
| `list -u` | 列出即将到期任务 | `python -m todo_cli.cli list -u` |
| `list -o` | 列出已过期任务 | `python -m todo_cli.cli list -o` |
| `done <ID>` | 标记任务完成 | `python -m todo_cli.cli done 3` |
| `delete <ID>` | 删除任务 | `python -m todo_cli.cli delete 2` |

### 时间跟踪
```bash
# 开始计时
python -m todo_cli.cli start <任务ID>

# 停止计时
python -m todo_cli.cli stop <任务ID>

# 查看时间报告
python -m todo_cli.cli time
```

### 查看剩余时间
```bash
# 查看任务剩余时间
python -m todo_cli.cli remaining <任务ID>

# 示例输出：
# 任务 #1: 写周报
# 截止时间: 2023-12-15 17:00
# 状态: 还剩 2天3小时
```

### 数据存储
默认使用 JSON 格式存储任务数据：
```bash
# 使用 CSV 格式存储
python -m todo_cli.cli add "新任务" -f tasks.csv

# 指定自定义文件
python -m todo_cli.cli list -f my_tasks.json
```

## 🧪 运行测试
```bash
# 安装测试依赖
pip install pytest

# 运行所有测试
pytest tests/
```

## 🧩 项目结构
```
todo-cli/
├── todo_cli/          # 源代码
│   ├── cli.py         # 命令行接口
│   ├── storage.py     # 文件存储
│   └── todo.py        # 核心逻辑
├── tests/             # 单元测试
├── README.md          # 本文件
└── requirements.txt   # 依赖列表
```

## 🤝 贡献指南
欢迎贡献代码！请遵循以下步骤：
1. Fork 仓库
2. 创建新分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -m 'feat: 添加新功能'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建 Pull Request

提交消息请遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

