#!/usr/bin/env python3
"""Render a fixed 10-second news video. Python standard library + FFmpeg."""
import argparse
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

def run(args):
    subprocess.run([str(x) for x in args], check=True)

def probe(path, ffprobe):
    return json.loads(subprocess.check_output(
        [ffprobe, "-v", "error", "-show_streams", "-of", "json", str(path)],
        encoding="utf-8"))

def number(value):
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value)

def check_config(c, width, height, duration):
    title = c.get("title", [])
    rows = c.get("rows", [])
    if not 2 <= len(title) <= 4 or len(rows) != 5:
        raise ValueError("title must have 2-4 lines; rows must have exactly 5 pairs")
    values = list(title)
    for row in rows:
        if not isinstance(row, list) or len(row) != 2:
            raise ValueError("Each row must be [label, body]")
        values.extend(row)
    if any(not isinstance(s, str) or not s.strip() or any(x in s for x in "\r\n{}\\") for s in values):
        raise ValueError("Text must be nonempty and cannot contain line breaks or ASS control characters")
    scales = c.get("title_scale", [100] * len(title))
    if len(scales) != len(title) or any(not number(s) or not 40 <= s <= 100 for s in scales):
        raise ValueError("title_scale must match title, with values 40..100")
    segments = c.get("segments", [])
    if not segments:
        raise ValueError("Provide at least one crop segment")
    last = 0
    for s in segments:
        if any(not number(s.get(k)) for k in ("start", "end", "x", "y", "width", "height")):
            raise ValueError("Crop fields must be finite numbers")
        if not (last <= s["start"] < s["end"] <= duration + 0.05):
            raise ValueError("Segments must be ordered, nonoverlapping and within source duration")
        if s["end"] - s["start"] < 0.1:
            raise ValueError("Each segment must be at least 0.1 seconds")
        if any(int(s[k]) != s[k] for k in ("x", "y", "width", "height")):
            raise ValueError("Crop coordinates must be integers")
        if s["x"] < 0 or s["y"] < 0 or s["width"] < 2 or s["height"] < 2:
            raise ValueError("Invalid crop rectangle")
        if s["x"] + s["width"] > width or s["y"] + s["height"] > height:
            raise ValueError("Crop rectangle exceeds source bounds")
        last = s["end"]

def subtitles(c, font):
    if any(x in font for x in ",\r\n{}\\"):
        raise ValueError("Invalid font family")
    lines = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920",
             "WrapStyle: 2", "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
             "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding"]
    for name, size, color, outline, italic, align in [
        ("Title",78,"&H00FFFFFF","&H00D86600",-1,5),
        ("Yellow",93.6,"&H0000FFFF","&H002A477B",-1,5),
        ("Label",51,"&H007CA0FF","&H00342A78",0,7),
        ("Body",51,"&H00FFFFFF","&H00342A78",0,7),
        ("Icon",42,"&H00FFF000","&H006D2500",0,7)]:
        lines.append(f"Style: {name},{font},{size},{color},{color},{outline},&H70000000,-1,{italic},0,0,100,100,0,0,1,2.5,1, {align},0,0,0,1")
    lines += ["", "[Events]", "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text"]
    def add(style, x, y, text, scale=100):
        tags = chr(92) + f"pos({x},{y})" + chr(92) + f"fscx{scale}"
        lines.append(f"Dialogue: 0,0:00:00.00,0:00:10.00,{style},,0,0,0,,{{{tags}}}{text}")
    ys = {2:[355,470], 3:[310,405,505], 4:[230,325,415,510]}[len(c["title"])]
    for i, (text, y) in enumerate(zip(c["title"], ys)):
        add("Yellow" if i == len(ys)-1 else "Title",540,y,text,c.get("title_scale",[100]*len(ys))[i])
    for i,(label,body) in enumerate(c["rows"]):
        y = 1490 + 65*i
        add("Icon",105,y,"◇")
        add("Label",170,y,label+"：")
        add("Body",365,y,body,95)
    return "\n".join(lines)+"\n"

def render(source, config, output, audio=None, silent=False, font="Microsoft YaHei", ffmpeg="ffmpeg", ffprobe="ffprobe", overwrite=False):
    if output.resolve() in [p.resolve() for p in [source, config] + ([audio] if audio else [])]:
        raise ValueError("Output must not replace an input file")
    if bool(audio) == bool(silent):
        raise ValueError("Choose one: --audio YOUR_AUDIO or --silent")
    if output.exists() and not overwrite:
        raise FileExistsError(f"Output exists: {output}; choose another path or --overwrite")
    for item in [source, config] + ([audio] if audio else []):
        if not item.is_file():
            raise FileNotFoundError(item)
    video = next(s for s in probe(source,ffprobe)["streams"] if s["codec_type"]=="video")
    duration = float(video["duration"])
    c = json.loads(config.read_text(encoding="utf-8-sig"))
    check_config(c,int(video["width"]),int(video["height"]),duration)
    output.parent.mkdir(parents=True,exist_ok=True)
    segments = c["segments"]
    selected = sum(s["end"]-s["start"] for s in segments)
    factor = (10-1/30)/(selected-1/30)
    graph = [f"[0:v]split={len(segments)}"+ "".join(f"[s{i}]" for i in range(len(segments)))]
    for i,s in enumerate(segments):
        graph.append(f"[s{i}]trim=start={s['start']}:end={s['end']},setpts=PTS-STARTPTS,format=yuv444p,crop={s['width']}:{s['height']}:{s['x']}:{s['y']}:exact=1,scale=1080:831:force_original_aspect_ratio=increase,crop=1080:831:exact=1,setsar=1[seg{i}]")
    graph += ["".join(f"[seg{i}]" for i in range(len(segments)))+
              f"concat=n={len(segments)}:v=1:a=0,setpts={factor:.10f}*PTS,fps=30,tpad=stop_mode=clone:stop_duration=10,trim=duration=10[mid]",
              "color=c=0x020a35:s=1080x1920:r=30:d=10,format=yuv444p,drawbox=x=0:y=552:w=230:h=7:color=0x7118d8:t=fill,drawbox=x=0:y=565:w=175:h=5:color=0x075cff:t=fill,drawbox=x=650:y=1840:w=430:h=10:color=0x7118d8:t=fill,drawbox=x=760:y=1860:w=320:h=7:color=0x075cff:t=fill[bg]",
              "[bg][mid]overlay=0:578:shortest=1:format=yuv444,drawbox=x=0:y=576:w=1080:h=3:color=0xff2f9d:t=fill,drawbox=x=0:y=1407:w=1080:h=3:color=0x195cff:t=fill,subtitles=captions.ass[v]"]
    inputs = ["-i",str(source.resolve())]
    if audio:
        streams=probe(audio,ffprobe)["streams"]
        if not any(s["codec_type"]=="audio" for s in streams):
            raise ValueError("Audio file has no audio stream")
        inputs += ["-i",str(audio.resolve())]
        graph.append("[1:a]apad,atrim=duration=10,asetpts=PTS-STARTPTS,alimiter=limit=0.79:level=0[a]")
    else:
        graph.append("anullsrc=r=44100:cl=stereo,atrim=duration=10[a]")
    # Use a temporary cwd so ASS paths with spaces, apostrophes or colons never enter filter syntax.
    with tempfile.TemporaryDirectory(prefix="tech-news-") as tmp:
        Path(tmp,"captions.ass").write_text(subtitles(c,font),encoding="utf-8")
        candidate=Path(tmp,"result.mp4")
        command=[ffmpeg,"-hide_banner","-loglevel","error","-y",*inputs,"-filter_complex",";".join(graph),"-map","[v]","-map","[a]","-t","10","-r","30","-c:v","libx264","-crf","18","-preset","medium","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-ar","44100","-ac","2","-movflags","+faststart",str(candidate)]
        subprocess.run(command,cwd=tmp,check=True)
        result=probe(candidate,ffprobe)
        v=next(s for s in result["streams"] if s["codec_type"]=="video")
        if int(v["nb_frames"]) != 300 or abs(float(v["duration"])-10)>0.001:
            raise RuntimeError("Output must be 300 frames / 10 seconds")
        shutil.copyfile(candidate,output)
        output.with_suffix(".ass").write_text(subtitles(c,font),encoding="utf-8")
    print(f"OK: {output} (1080x1920, 300 frames, 10s)")

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("source","config","output"):
        p.add_argument("--"+key,type=Path,required=True)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--audio",type=Path)
    group.add_argument("--silent",action="store_true")
    p.add_argument("--font",default="Microsoft YaHei")
    p.add_argument("--ffmpeg",default="ffmpeg")
    p.add_argument("--ffprobe",default="ffprobe")
    p.add_argument("--overwrite",action="store_true")
    try:
        render(**vars(p.parse_args()))
    except (ValueError,KeyError,StopIteration,FileNotFoundError,FileExistsError,subprocess.CalledProcessError) as exc:
        p.exit(1,f"Error: {exc}\n")

