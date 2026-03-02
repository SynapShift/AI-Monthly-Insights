# ⚡ AI-Monthly-Insights - 自动化获取AI进展

一个基于 Streamlit 开发的 AI 行业周报自动化展示工具。支持从 Google Sheets 实时同步数据，具备多维度筛选与精美的 UI 交互体验。

## 🚀 功能特点
- **实时同步**：自动读取 Google Sheets 多个工作表（按月份切换）。
- **智能筛选**：支持按地域（全部/中国/海外）进行数据过滤。
- **数据可视化**：自动统计基建、应用、金融等分类的数量分布。
- **工业级 UI**：响应式黑金侧边栏与卡片式流式布局。

## 🛠️ 部署指南

### 1. 数据源准备
将你的 Google Sheet 设置为 **“知道链接的任何人都可以查看”**。

### 2. 部署至 Streamlit Cloud
1. 将代码 Push 到 GitHub 仓库。
2. 在 [Streamlit Cloud](https://share.streamlit.io/) 关联此仓库。
3. **关键步骤（隐藏链接）**：
   在 App 的 **Settings -> Secrets** 中添加以下配置：
   ```toml
   gsheet_url = "你的Google_Sheets_链接"
