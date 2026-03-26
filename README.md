# Architron 🤖 

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Powered%20by-Ollama-white.svg)](https://ollama.com/)

**Architron** 是一款专为开发者设计的轻量化本地智能体 (Lightweight Local Agent)。

与 AutoGPT、LangChain 等重型框架不同，Architron 专注于**极简主义**。它利用本地 Ollama 模型提供动力，在保证隐私的同时，实现毫秒级的响应速度，拒绝过度工程化。

---

## 🌟 核心特性

* 🚀 **极轻量设计**：拒绝冗余依赖，核心逻辑纯净，启动即运行。
* 🏠 **100% 本地化**：基于 Ollama 驱动，数据无需上传云端，彻底告别 API 密钥和高昂费用。
* 🛠️ **开发者友好**：内置文件操作、LLM 客户端等实用工具，支持快速自定义 Sub-Agents。
* 🧠 **小模型优化**：针对 `llama3`, `qwen2.5`, `mistral` 等 7B/14B 模型深度优化。
* 💻 **低配运行**：即使在宿舍 8GB/16GB 内存的笔记本上也能流畅运行。

---

## 🏗️ 项目架构

项目采用清晰的分层设计，方便你随时扩展工具集：

```plaintext
Architron/
├── agents/          # 智能体核心逻辑 (如 sub_agent.py)
├── tools/           # 扩展工具集 (文件操作、开发辅助、subprocess调用等)
├── utils/           # 基础底层支持 (Ollama 客户端、运行器)
├── main.py          # 程序入口
└── config.py        # 配置文件
