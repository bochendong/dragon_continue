# 龙族续写项目 - Dragon Continue

AI驱动的《龙族Ⅰ火之晨曦》续写系统

---

## 🎯 项目简介

这是一个使用AI技术续写江南《龙族Ⅰ火之晨曦》的项目，包含：

- 📚 **角色数据库**：详细的角色背景、性格、关系
- 📖 **情节数据库**：分层情节大纲、章节摘要
- 🤖 **AI写作系统**：江南风格的智能续写
- 🎨 **Web前端**：在线阅读界面
- ✅ **质量控制**：自动风格检查和改进

---

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- npm 或 yarn

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd dragon_continue
```

### 2. 安装后端依赖

```bash
# 创建虚拟环境
cd agents
python3 -m venv agents_venv
source agents_venv/bin/activate  # Windows: agents_venv\Scripts\activate

# 安装依赖
pip install -r ../requirements.txt
```

### 3. 配置OpenAI API

```bash
# 设置环境变量
export OPENAI_API_KEY="your-api-key-here"

# 或创建 .env 文件
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 4. 安装前端依赖

```bash
cd ..
npm install
```

### 5. 启动服务

```bash
# 终端1：启动前端
npm start

# 终端2：生成新章节
cd agents
source agents_venv/bin/activate
python3 continue_story.py
```

### 6. 访问应用

打开浏览器访问：http://localhost:3000

---

## 📁 项目结构

```
dragon_continue/
├── README.md                          # 项目文档
├── requirements.txt                   # Python依赖
├── package.json                       # Node.js依赖
│
├── agents/                            # AI写作系统
│   ├── agents_venv/                   # Python虚拟环境
│   ├── database/                      # 数据库模块
│   │   ├── character_database.py     # 角色数据库
│   │   ├── database_api.py           # 角色API
│   │   ├── plot_database.py          # 情节数据库
│   │   ├── plot_api.py               # 情节API
│   │   ├── storyline_database.py     # 故事线数据库
│   │   ├── merge_agent.py            # AI合并Agent
│   │   ├── ai_merge_interface.py     # AI合并接口
│   │   ├── plot_merge_system.py      # 情节合并系统
│   │   ├── dragon_characters.db      # 角色SQLite数据库
│   │   ├── plot_outline.db           # 情节SQLite数据库
│   │   └── storyline_db.db           # 故事线SQLite数据库
│   │
│   ├── continuation_writers.py        # 核心写作系统
│   ├── ai_story_planner.py           # AI故事规划（双层）
│   ├── story_arc_planner.py          # 故事弧线规划
│   ├── writing_style_controller.py   # 风格质量控制
│   ├── character_info_extraction.py  # 角色信息提取
│   ├── new_character_detector.py     # 新角色检测
│   ├── integrate_quality_control.py  # 质量控制集成
│   ├── continue_story.py             # 续写入口脚本
│   └── output/                        # 生成的章节（详细版）
│
├── src/                               # React前端
│   ├── components/                    # React组件
│   ├── pages/                         # 页面组件
│   │   ├── HomePage.js               # 主页（搞怪风）
│   │   ├── ChapterListPage.js        # 章节列表
│   │   └── ChapterReaderPage.js      # 阅读器
│   ├── App.js                         # 主应用
│   └── index.js                       # 入口文件
│
├── chapters_2000_words/               # 章节文件
│   ├── 001-131_*.txt                 # 原著章节
│   └── 132+_*.txt                    # AI生成章节
│
├── public/                            # 静态资源
│   ├── index.html                    # HTML模板
│   └── chapters_2000_words/          # 章节文件软链接
│
└── 《龙族Ⅰ火之晨曦》_readable.txt      # 原著完整文本
```

---

## 🤖 核心功能

### 1. 角色管理系统

**功能**：
- 存储角色的详细信息（背景、血统、性格、说话方式、名言）
- 管理角色关系网络
- 自动从原文提取角色信息
- 自动检测新角色

**使用**：
```bash
# 从原文提取所有角色信息
cd agents
source agents_venv/bin/activate
python3 character_info_extraction.py

# 检测新章节中的新角色
python3 new_character_detector.py output/chapter_27_*.txt
```

### 2. 情节管理系统

**功能**：
- B-tree式的分层章节摘要
- AI智能生成父节点摘要
- 主storyline和sub-storyline管理
- 长期规划和短期规划

**特点**：
- 近期章节显示详细内容
- 远期章节显示合并摘要
- 避免context length问题

### 3. AI写作系统

**双层规划**：
- **长期规划**（`AILongTermPlanner`）：整体故事弧线
- **短期规划**（`AIShortTermPlanner`）：单章详细指导

**风格控制**（5个维度）：
1. ✅ **内心OS和吐槽** - "真烦真烦真烦！"
2. ✅ **废柴性格** - "路鸣泽的哥哥"
3. ✅ **具体细节** - N96手机、36000美元
4. ✅ **对比反差** - S级混血种 vs 废柴
5. ✅ **口语化** - GG了、秀逗了

**质量保证**：
- 自动风格检查（0-100分）
- 自动改进（最多3轮）
- 详细评分报告

### 4. Web前端

**功能**：
- 📖 章节列表（支持滚动加载）
- 📄 在线阅读器（上一章/下一章导航）
- 🤖 AI章节标记（绿色边框+AI图标）
- 📱 响应式设计
- 😎 搞怪主页（江南老贼吐槽风）

---

## 📝 使用指南

### 生成新章节

```bash
cd agents
source agents_venv/bin/activate

# 自动生成下一章
python3 continue_story.py

# 生成指定章节
python3 continue_story.py 28

# 生成过程会自动：
# 1. AI规划情节大纲
# 2. AI写作章节内容
# 3. 保存到数据库和文件
```

### 提取角色信息

```bash
# 从原文提取所有主要角色的详细信息
python3 character_info_extraction.py

# 支持的角色：
# - 路明非、楚子航、恺撒、诺诺、芬格尔
# - 路鸣泽、昂热、夏弥、陈雯雯等
```

### 检测新角色

```bash
# 分析新生成的章节，自动检测并添加新角色
python3 new_character_detector.py output/chapter_27_*.txt

# 会自动：
# 1. 检测新角色
# 2. 提取角色信息
# 3. 添加到数据库
```

### 质量控制

```bash
# TODO: 集成到写作流程
# 当前版本会在生成时自动进行基本检查
```

---

## 🔧 技术栈

### 后端

- **Python 3.9+**
- **OpenAI Agents API** - AI Agent框架
- **SQLite 3** - 数据库
- **Pydantic** - 数据验证
- **asyncio** - 异步编程
- **nest-asyncio** - 嵌套事件循环支持

### 前端

- **React 18** - UI框架
- **Material-UI (MUI)** - UI组件库
- **React Router** - 路由管理
- **JavaScript ES6+**

---

## 📊 数据库设计

### 角色数据库 (`dragon_characters.db`)

**表**：
- `characters` - 角色基本信息
- `character_bloodline` - 角色血统信息
- `personality_traits` - 性格特点
- `speech_patterns` - 说话方式
- `memorable_quotes` - 经典语录
- `character_relationships` - 角色关系

### 情节数据库 (`plot_outline.db`)

**表**：
- `chapters` - 章节信息
- `plot_lines` - 情节线
- `character_arcs` - 角色发展
- `merge_summaries` - AI生成的合并摘要
- `chapter_plot_lines` - 章节与情节线关联

### 故事线数据库 (`storyline_db.db`)

**表**：
- `main_storyline_phases` - 主故事线阶段
- `storylines` - 子故事线（弧线）
- `storyline_events` - 故事线事件
- `storyline_characters` - 故事线角色

---

## 🎯 质量保证

### 评分标准

| 分数 | 评级 | 说明 | 处理方式 |
|-----|------|------|---------|
| 90-100 | 优秀 | 完美符合江南风格 | 直接发布 ✅ |
| 80-89 | 良好 | 很好，小问题 | 直接发布 ✅ |
| 70-79 | 合格 | 基本符合，有明显问题 | 发布但标记 ⚠️ |
| 60-69 | 不合格 | 风格偏离，需要大改 | 自动改进 🔧 |
| <60 | 差 | 完全不符合 | 需人工重写 ❌ |

### 检查维度

1. **内心OS和吐槽** (20分)
   - 是否有大量内心独白？
   - 是否有吐槽式的幽默？
   - 是否有"想vs说"的对比？

2. **废柴性格** (20分)
   - 是否体现路明非的自卑和自嘲？
   - 是否有"路鸣泽的哥哥"类似的梗？
   - 是否有白烂和蔫儿坏的表现？

3. **具体细节** (20分)
   - 是否有具体的品牌、数字、时间？
   - 是否避免了抽象和模糊的描写？
   - 细节是否生动有趣？

4. **对比反差** (20分)
   - 是否有强烈的对比场景？
   - 是否体现双重身份的矛盾？
   - 想象与现实的落差？

5. **语言风格** (20分)
   - 是否口语化、自然？
   - 是否使用网络用语？
   - 是否避免了过于文艺的表达？

---

## 📈 当前状态

- ✅ **原著章节**：131章 (chapters_2000_words/001-131)
- ✅ **AI生成章节**：第26-27章 (chapters_2000_words/132-133)
- ✅ **角色数据**：18个主要角色 + 详细信息
- ✅ **情节大纲**：25章详细大纲 + AI合并摘要
- ✅ **风格控制**：5维度自动检查（待集成）
- ✅ **Web前端**：在线阅读 + AI章节标记

---

## 🔮 开发路线图

### 短期（1-2周）

- [ ] 集成质量控制系统到写作流程
- [ ] 提取所有角色的详细信息
- [ ] 生成更多章节（第28-35章）
- [ ] 优化风格检查算法

### 中期（1-2个月）

- [ ] 实现自动风格学习
- [ ] 支持多种写作风格切换
- [ ] 增加人物关系图谱可视化
- [ ] 导出电子书格式（EPUB/MOBI）

### 长期（3-6个月）

- [ ] 支持多部作品续写
- [ ] 实现交互式情节规划
- [ ] 开发桌面应用
- [ ] 社区功能（评论、分享）

---

## 🛠️ 常见问题

### Q: 生成的内容风格不够江南？

**A**: 当前系统还在优化中，建议：
1. 运行 `character_info_extraction.py` 更新角色信息
2. 等待质量控制系统集成完成
3. 或手动调整生成的内容

### Q: 如何修改已生成的章节？

**A**: 
1. 编辑 `chapters_2000_words/XXX_未知章节.txt`
2. 同步更新 `agents/output/chapter_XX_*.txt`
3. 更新数据库（可选）

### Q: 生成速度慢？

**A**: 
- AI生成需要时间，每章约2-5分钟
- 可以调整 `max_iterations` 参数减少改进轮数
- 确保网络连接稳定

### Q: OpenAI API报错？

**A**: 
1. 检查 API Key 是否正确
2. 检查账户余额
3. 检查网络连接
4. 查看错误日志：`agents/output/`

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 贡献方式

1. **报告Bug**：提交Issue，详细描述问题
2. **功能建议**：提交Issue，说明需求场景
3. **代码贡献**：Fork项目，提交PR

### 代码规范

- Python：遵循PEP 8
- JavaScript：使用ES6+语法
- 提交信息：使用中文，简洁明了

---

## 📜 许可证

本项目仅供学习和研究使用。

**版权声明**：
- 原著《龙族Ⅰ火之晨曦》版权归江南所有
- AI生成内容仅供参考，不做商业用途
- 项目代码遵循MIT许可证

---

## 🙏 致谢

- **江南** - 原著作者，提供了丰富的世界观和角色设定
- **OpenAI** - 提供强大的AI技术支持
- **React & Material-UI** - 优秀的前端框架
- **所有贡献者** - 感谢你们的支持

---

## 📧 联系方式

- **Issue**: 项目GitHub Issues
- **讨论**: GitHub Discussions

---

**🐉 卡塞尔学院欢迎你！路明非的故事还在继续...**

