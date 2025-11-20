# Smart Scraper RSS - 用户手册

## 📚 目录
1. [快速开始](#快速开始)
2. [功能介绍](#功能介绍)
3. [使用说明](#使用说明)
4. [常见问题](#常见问题)

---

## 快速开始

### 环境要求
- Python 3.11+
- Windows / macOS / Linux

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd Smart-Scraper-RSS
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置 API 密钥**
```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY="your-api-key-here"

# Linux/macOS
export DEEPSEEK_API_KEY="your-api-key-here"
```

4. **运行应用**
```bash
python -m app.main
```

应用将自动打开浏览器访问 http://localhost:8080

---

## 功能介绍

### 📊 主控台 (Dashboard)
- 查看统计数据：源数量、抓取项、今日抓取、定时任务
- 浏览最近抓取的内容
- 快速操作按钮

### 🔗 源管理 (Sources)
- 添加新的抓取源
- 查看所有源的状态
- 编辑和删除源
- 手动触发抓取

### ⚙️ 设置 (Settings)
- 配置 DeepSeek API 密钥
- 查看调度器状态
- 查看任务队列状态
- 系统配置信息

### 📡 RSS Feed
- 访问 http://localhost:8080/feed.xml 获取 RSS Feed
- 支持 RSS 阅读器订阅
- AI 增强的内容摘要和情感分析

---

## 使用说明

### 添加抓取源

1. 进入「源管理」页面
2. 点击「添加源」按钮
3. 填写表单：
   - **源名称**: 自定义名称，例如"我的B站收藏"
   - **URL**: 要抓取的页面地址
   - **平台**: 选择 bilibili 或 xiaohongshu
   - **抓取频率**: 自动抓取间隔（分钟）
4. 点击「添加」

源添加后会自动加入调度器，按设定频率自动抓取。

### 查看抓取内容

- **主控台**: 显示最近 10 条抓取内容
- 每条内容包含：
  - 标题
  - AI 生成的摘要
  - 情感分析
  - 创建时间

### 订阅 RSS

1. 复制 RSS Feed 地址：`http://localhost:8080/feed.xml`
2. 在 RSS 阅读器中添加订阅
3. 推荐阅读器：
   - Feedly
   - Inoreader
   - NetNewsWire

---

## 常见问题

### Q: 如何获取 DeepSeek API 密钥？
A: 访问 https://platform.deepseek.com/ 注册账号并创建 API 密钥。

### Q: 支持哪些平台？
A: 目前支持 Bilibili 和小红书。可以通过添加新的爬虫策略扩展。

### Q: 如何修改端口？
A: 编辑 `app/config.py` 中的 `UI_PORT` 配置。

### Q: 抓取失败怎么办？
A: 检查：
1. URL 是否正确
2. 网络连接是否正常
3. 查看日志获取详细错误信息

### Q: 如何停止自动抓取？
A: 在「源管理」中删除对应的源，或修改源的 `is_active` 状态为 False。

### Q: 数据库文件在哪里？
A: `data/database.db` - SQLite 数据库文件

### Q: 如何备份数据？
A: 复制 `data/` 目录即可备份所有数据和配置。

---

## 技术支持

如有问题或建议，请提交 Issue。

---

© 2025 Smart Scraper RSS
