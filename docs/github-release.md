# GitHub 发布资料

建议仓库名：tech-news-ziyou-10s

Description：把科技素材制作成10秒深蓝竖版快讯的Agent Skill。Python + FFmpeg，支持分镜裁切、ASS字幕与发布文案。

Topics：codex-skill, agent-skills, ffmpeg, video-editing, chinese, short-video, automation

首版标签：v1.0.0

Release标题：v1.0.0 — 科技自由版10秒快讯

Release正文：
- 固定1080×1920、30fps、10秒输出。
- 逐镜头裁切，全宽展示主体。
- 标题与五条信息配置，末行黄色强调。
- Python标准库渲染器、可运行合成示例、安全安装器。
- 用户自备音频，支持显式静音。

## 发布步骤
1. 在GitHub创建同名仓库，选择Public。上传本目录的内容，确保SKILL.md在仓库根部。
2. 不上传output、缓存或私人新闻素材。发布ZIP已排除这些内容。
3. LICENSE采用MIT，版权署名为自由变量；确认这符合你的授权意愿。
4. 检查README中的预览和示例命令，待Actions通过后创建v1.0.0 Release，可附带整理好的ZIP。
5. 如果要附带原固定配音或旧母版，先确认可以公开再分发，再添加素材来源和授权说明。当前公开包不包含这些文件。

本次仅整理本地仓库与ZIP，未创建远端仓库、未上传文件。无需GitHub登录即可运行本地示例。
