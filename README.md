# 自动 API 对话 (Auto Chat)

这是一个自动化的 GitHub Actions 工作流，用于定期向指定的 API 发送包含数学问题的对话请求。主要用于保持服务活跃或进行简单的 API 连通性测试。

## 功能特性

*   **定时执行**：每天北京时间 8:00、14:00、20:00 自动运行。
*   **随机内容**：每次运行会自动生成一个 100 以内的加减法问题（如 "23 + 45 等于多少"）。
*   **多组配置**：支持通过 JSON 配置同时向多个不同的 API 发起请求。
*   **灵活配置**：支持单组简易配置和多组高级配置。

## 使用方法

### 1. Fork 本仓库

点击右上角的 **Fork** 按钮，将本项目复制到你自己的 GitHub 账号下。

### 2. 配置 Secrets

进入你 Fork 后的仓库，点击 **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**。

你需要根据你的需求选择以下**一种**配置方式：

#### 方式 A：多组配置（推荐）

如果你需要同时向多个 API 发送请求，请创建一个名为 `API_CONFIGS` 的 Secret，值为 JSON 数组格式。

**Secret Name**: `API_CONFIGS`
**Secret Value 示例**:
```json
[
  {
    "url": "https://api.agentify.top/v1/chat/completions",
    "token": "sk-your-token-1",
    "model": "meta-llama/llama-3.3-70b-instruct:free"
  },
  {
    "url": "https://api.another-service.com/v1/chat/completions",
    "token": "sk-your-token-2",
    "model": "gpt-3.5-turbo"
  }
]
```

#### 方式 B：单组配置（简易）

如果你只需要向一个 API 发送请求，可以分别创建以下三个 Secret：

*   `API_URL`: 接口地址 (例如 `https://api.agentify.top/v1/chat/completions`)
*   `API_TOKEN`: Bearer Token (不带 `Bearer ` 前缀，脚本会自动添加)
*   `MODEL_NAME`: 模型名称 (例如 `meta-llama/llama-3.3-70b-instruct:free`)

> **注意**：如果同时配置了 `API_CONFIGS` 和单组变量，脚本将优先使用 `API_CONFIGS`。

### 3. 启用 Workflow 与权限设置

Fork 的仓库默认可能禁用了 Workflow，且默认权限可能不足以写入日志文件。

1.  点击仓库上方的 **Actions** 标签页，点击绿色按钮启用工作流。
2.  进入 **Settings** -> **Actions** -> **General**。
3.  在 **Workflow permissions** 区域，选中 **Read and write permissions**。
4.  点击 **Save** 保存设置。

> **重要**：如果不开启 Read and write permissions，工作流将无法把日志写入 `log.txt` 并推送到仓库。

你可以手动触发一次 `workflow_dispatch` 来测试配置是否正确。

## 定时任务说明

工作流配置为每天运行三次：
*   UTC 时间：0:00, 6:00, 12:00
*   **北京时间**：8:00, 14:00, 20:00

## 日志功能

程序会自动在根目录下生成 `log.txt` 文件，用于记录每次 API 请求的详细信息。

### 1. 日志格式

日志采用追加写入模式，每条记录包含以下三部分：

*   **请求时间**：精确到秒，格式为 `[YYYY-MM-DD HH:MM:SS]`
*   **请求内容**：发送给 API 的数学问题
*   **请求结果**：API 返回的回答内容

**示例**：
```text
请求时间：[2024-03-20 08:00:01]
请求内容：23 + 45 等于多少
请求结果：68

请求时间：[2024-03-20 08:00:02]
请求内容：88 - 12 等于多少
请求结果：76
```

### 2. 多请求处理

当配置了多组 API (`API_CONFIGS`) 时，程序会依次执行请求，并自动将每条请求的结果追加记录到日志文件中。

### 3. 注意事项

*   日志文件使用 **UTF-8** 编码。
*   每次运行 Workflow 时，日志文件会被更新并提交回仓库（保留历史记录）。
*   请确保 GitHub Actions 具有写入仓库的权限（Workflow 中已配置）。

## 本地运行

如果你想在本地测试脚本：

1.  安装依赖：
    ```bash
    pip install -r requirements.txt
    ```

2.  设置环境变量并运行：
    ```bash
    # 单组测试
    export API_URL="https://api.example.com/..."
    export API_TOKEN="your-token"
    export MODEL_NAME="model-name"
    python main.py
    
    # 或者多组测试
    export API_CONFIGS='[{"url":"...", "token":"...", "model":"..."}]'
    python main.py
    ```
