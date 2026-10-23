# tech-news-ziyou-10s

**把科技素材做成固定 10 秒、1080×1920 的深蓝竖版快讯。**

面向可读写文件、执行命令的 AI Agent，也可以直接在终端运行。顶部标题、中部全宽画面、底部五条信息，字幕由 ASS 渲染，避免图片生成文字错字。

![版式预览：中部为合成测试画面](docs/preview.jpg)

## 你会得到
- H.264 MP4，30fps，300帧，10.00秒；AAC 44.1kHz 双声道。
- 2–4行标题，末行黄色放大20%；中部等比裁切铺满1080×831。
- 五行底部信息和可编辑 ASS；Agent 使用时同时整理发布文案。
- 分镜裁切JSON，支持从多个片段提取有效主体。
- 无API密钥、无付费服务、Python标准库实现。

## 依赖
1. Python 3.10或更新版本。
2. FFmpeg 和 FFprobe 加入 PATH，FFmpeg必须支持 libx264、AAC和subtitles/libass。
3. 中文字体：Windows可使用系统微软雅黑；macOS/Linux可安装 Noto Sans CJK SC 并传 `--font "Noto Sans CJK SC"`。字体不随仓库分发。
4. AI分析内容和选择裁切需要Agent；脚本不会自动理解新闻或识别标题位置。

检查：`python --version`、`ffmpeg -version`、`ffprobe -version`。Windows如Python命令为py，可将示例中的python替换为py。

## 先跑通示例（无需下载视频）
下载仓库ZIP并解压，进入包含本README的目录：
```sh
python scripts/demo.py
```
生成 output/demo.mp4 和 output/demo.ass。它使用FFmpeg合成测试图，**示例为静音**。
非Windows系统：
```sh
python scripts/demo.py --font "Noto Sans CJK SC"
```
Windows已实测；macOS/Linux采用同一Python脚本，但未在本次发布准备中实机验证。自动检查见GitHub Actions。

## 安装为 Codex Skill
```sh
python scripts/install.py
```
安装到 CODEX_HOME/skills/tech-news-ziyou-10s；未设置CODEX_HOME时为用户目录下 .codex/skills/tech-news-ziyou-10s。已有同名目录时停止，不覆盖你的修改。安装后开启新会话或重新加载技能。

也可手动将本仓库目录复制为该目录。其他支持SKILL.md的Agent可手动添加，具体发现机制以其客户端为准；普通网页聊天环境不能直接执行本地渲染。

**示例提问：**
> 使用 tech-news-ziyou-10s，把 input.mp4 做成10秒科技快讯，使用 narration.wav，保存在 output/新闻-未发，附发布文案。

只有截图或链接时：
> 根据这条资讯先核验事实、找官方素材，再做10秒快讯。没有配音时先交付静音版。

## 直接渲染自己的视频
1. 将 examples/news.json 复制为 news.json。
2. 填写标题、底部文案，并按实际视频坐标填写 segments。**示例裁切不能盲目套用到其他尺寸。**
3. 传入你有权使用的音频（前10秒，短音频尾部补静音，不自动改语速）：
```sh
python scripts/render.py --source input.mp4 --config news.json --audio narration.wav --output output/news.mp4
```
明确不要配音时把 `--audio narration.wav` 替换为 `--silent`。不使用来源视频音轨。已有输出默认拒绝覆盖；确认替换时加 `--overwrite`。

配置说明：[references/config.md](references/config.md)。版式：[references/b-layout-spec.md](references/b-layout-spec.md)。

## 配音与素材
本公开版使用代码绘制背景，不依赖旧母版。作者本机固定配音、参考成片和用户新闻素材没有纳入开源包，其再分发权未作确认。MIT授权仅覆盖仓库内代码和文档，不为外部视频、人物肖像、音乐或字体授予许可。
需要固定配音风格时，准备自己的10秒音频，后续每次通过 --audio 传入。

## 常见问题
- 找不到ffmpeg：加入PATH，或给渲染器传 --ffmpeg 和 --ffprobe 绝对路径。
- Unknown filter subtitles：换用包含libass的FFmpeg构建。
- 中文方框：安装中文字体，使用 --font 指定实际字体族；字体缺失可能被FFmpeg静默替换，必须看预览。
- 标题越界：先缩短文案，再调 title_scale（40–100）；不要降低黄色标题字高。底部建议2字标签和12字以内正文。
- 中部被裁掉：cover会裁掉部分内容；重新选择每个镜头的坐标。不会拉伸或模糊补边。
- 不支持某些输入：当前要求视频流有可读取的duration，建议MP4。先转换成常规MP4再处理。
- 脚本不生成发布文案：由Agent根据内容撰写；纯CLI只负责渲染。
- 中间短暂停帧：为稳定输出300帧，尾部可能补极短末帧；裁切时避免无意义静帧。

## 仓库结构
```text
SKILL.md                 Agent入口
scripts/render.py        跨平台渲染器
scripts/demo.py          合成素材快速验收
scripts/install.py       不覆盖的安装器
examples/news.json       可编辑配置
references/              版式与配置说明
tests/                   配置和渲染回归检查
.github/workflows/       Linux自动化检查
LICENSE                  MIT
```

## 验证
```sh
python -m unittest discover -s tests -v
python scripts/demo.py
```
再打开 output/demo.mp4 检查中文字体、文字边界和转场。代码检查不替代成片审核。

## 贡献
提交问题请附系统、Python/FFmpeg版本、去除敏感信息的JSON、完整错误及裁切截图。不要上传无权公开的视频或密钥。修改渲染逻辑后跑测试及示例。

License: MIT。署名：自由变量。

