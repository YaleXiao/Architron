Architron 🤖
Architron 是一款专为开发者设计的轻量化本地智能体 (Lightweight Local Agent)。与 AutoGPT、LangChain 等重型框架不同，Architron 专注于极简主义，利用本地 Ollama 模型提供动力，在保证隐私的同时，实现毫秒级的响应速度。

🌟 核心特性
🚀 极轻量设计：拒绝冗余的依赖包，核心逻辑纯净，启动速度极快。

🏠 100% 本地化：基于 Ollama 驱动，数据无需上传云端，彻底告别 API 密钥和高昂费用。

🛠️ 开发者友好：内置文件操作、LLM 客户端等实用工具，支持快速自定义 Sub-Agents。

🧠 小模型优化：针对 llama3, qwen2, mistral 等 7B/14B 模型深度优化，在低配硬件上也能流畅运行。

🏗️ 项目架构
项目采用了清晰的分层设计，方便你随时扩展工具集：

Plaintext
Architron/
├── agents/            # 智能体核心逻辑 (如 sub_agent.py)
├── tools/             # 扩展工具集 (文件操作、开发辅助等)
├── utils/             # 基础底层支持 (Ollama 客户端、运行器)
└── config.py          # 配置文件
🚀 快速开始
1. 前置要求
确保你已经安装并启动了 Ollama。

2. 克隆项目
Bash
git clone git@github.com:YaleXiao/Architron.git
cd Architron
3. 环境配置
建议使用 venv 或 conda 创建虚拟环境：

Bash
python -m venv venv
source venv/bin/activate  # Windows 使用 .\venv\Scripts\activate
pip install -r requirements.txt
4. 运行
Bash
python main.py
💡 为什么选择 Architron？
在目前 Agent 领域“过度工程化”的趋势下，Architron 走的是另一条路：

无痛调试：不需要复杂的 Prompt 编排，直接与本地模型对话。

资源占用低：即使在只有 8GB/16GB 内存的笔记本（如宿舍电脑）上也能轻松跑起。

透明性：代码简单直观，你可以一眼看清 Agent 是如何调用每一个 Tool 的。

📜 开源协议
MIT License
