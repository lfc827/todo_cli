# Todo CLI - 命令行任务管理器 

Todo CLI 是一个功能丰富的命令行任务管理器，专为开发者和效率爱好者设计。无需离开终端，即可通过智能截止日期、时间跟踪和直观的任务管理保持高效工作。


## ✨ 核心功能

- ✅ **任务管理** - 创建、查看、完成和删除任务
- 📅 **智能截止日期** - 支持绝对日期 (2024-12-31) 和相对日期 (明天)
- ⏱️ **时间跟踪** - 启动/停止计时器记录任务时间
- 🔔 **优先级管理** - 过期和即将到期任务视觉标识
- 💾 **自定义存储** - JSON 或 CSV 格式，带自动备份
- 📊 **详细报告** - 时间摘要和剩余时间计算
- 🌍 **国际化支持** - 支持多语言字符和表情符号

## ⚙️ 安装指南

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/todo-cli.git
cd todo-cli

# 2. 安装依赖
pip install -r requirements.txt

# 3. 使脚本可执行
chmod +x todo_cli/cli.py

# 4. 添加别名到 shell 配置文件 (.bashrc 或 .zshrc)
echo 'alias todo="python /path/to/todo-cli/todo_cli/cli.py"' >> ~/.zshrc
source ~/.zshrc
```

## 🚀 快速入门

### 基础工作流
```bash
# 添加新任务
todo add "购买日用品" --due tomorrow

# 列出活动任务
todo list

# 开始处理任务
todo start 1

# 标记任务为已完成
todo done 1

# 删除任务
todo delete 2 --no-confirm
```

### 高级用法
```bash
# 添加带复杂截止日期的任务
todo add "项目截止日期" --due "2024-06-30 14:30"

# 列出即将到期任务 (未来5天)
todo list --upcoming --days 5

# 生成时间报告
todo time

# 检查任务 #3 的剩余时间
todo remaining 3
```

## 📋 任务管理命令

| 命令 | 描述 | 示例 |
|---------|-------------|---------|
| `add "标题"` | 添加新任务 | `todo add "购买牛奶"` |
| `add "标题" --due <日期>` | 添加带截止日期的任务 | `todo add "提交报告" --due 2024-06-30` |
| `list` | 列出活动任务 | `todo list` |
| `list -a` | 列出所有任务 | `todo list -a` |
| `list -u` | 列出即将到期任务 | `todo list -u` |
| `list -o` | 列出过期任务 | `todo list -o` |
| `done <ID>` | 标记任务为已完成 | `todo done 3` |
| `delete <ID>` | 删除任务 | `todo delete 2` |
| `start <ID>` | 启动计时器 | `todo start 5` |
| `stop <ID>` | 停止计时器 | `todo stop 5` |
| `time` | 时间跟踪报告 | `todo time` |
| `time --summary` | 时间摘要 | `todo time --summary` |
| `remaining <ID>` | 查看剩余时间 | `todo remaining 4` |

### 关键选项
- **日期格式**: `today`, `tomorrow`, `YYYY-MM-DD`, `MM/DD/YYYY`, `DD.MM.YYYY`  
- **全局选项**:  
  `-f 文件` - 指定存储文件 (默认: tasks.json)  
  `--no-confirm` - 跳过确认提示

## 💾 数据存储

任务以人类可读格式存储，带自动备份功能：

```json
// tasks.json 示例
[
  {
    "id": 1,
    "title": "购买日用品",
    "done": false,
    "due_date": "2024-06-15T23:59:59",
    "time_spent": 1800
  }
]
```

**存储特性**:
- 🔄 保存前自动备份
- 📁 支持 JSON 和 CSV 格式
- 🌐 完整 Unicode 支持
- ⚡ 高效处理大型任务列表

## 🧪 测试与质量

```bash
# 运行所有测试
pytest

# 测试特定组件
pytest tests/test_cli.py       # CLI 命令测试
pytest tests/test_storage.py   # 存储系统测试
pytest tests/test_todo.py      # 核心逻辑测试

# 运行性能测试
pytest -m slow

# 代码格式化
black .
```

## 🧩 项目结构

```
todo-cli/
├── todo_cli/          # 源代码
│   ├── cli.py         # 命令行界面
│   ├── storage.py     # 文件存储处理
│   └── todo.py        # 核心任务逻辑
├── tests/             # 全面测试套件
│   ├── test_cli.py    # CLI 测试
│   ├── test_storage.py# 存储测试
│   └── test_todo.py   # 核心逻辑测试
├── README.md          # 文档
└── requirements.txt   # 依赖项
```

## 🤝 贡献指南

我们欢迎贡献！请遵循以下步骤：

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/你的特性`)
3. 提交更改 (`git commit -m 'feat: 添加神奇特性'`)
4. 推送到分支 (`git push origin feature/你的特性`)
5. 提交 Pull Request

**提交指南**:
- 使用 [Conventional Commits](https://www.conventionalcommits.org/)
- 保持提交原子化和专注
- 为新特性包含测试
