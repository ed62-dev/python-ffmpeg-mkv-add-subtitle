import os
import subprocess
import json
import tkinter as tk
from tkinter import filedialog

# ---------------------------
# 🔍 Obține info video
# ---------------------------
def get_video_info(video_path):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=bit_rate,r_frame_rate",
        "-show_entries", "format=duration",
        "-of", "json",
        video_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    try:
        data = json.loads(result.stdout)
    except:
        return 0, 0, 24

    duration = data.get("format", {}).get("duration")
    if duration in (None, "N/A"):
        duration = 0
    else:
        duration = float(duration)

    streams = data.get("streams", [])
    bitrate = 0
    fps = 24

    if streams:
        bitrate = int(streams[0].get("bit_rate", 0) or 0)

        fps_str = streams[0].get("r_frame_rate", "24/1")
        try:
            num, den = fps_str.split("/")
            fps = float(num) / float(den)
        except:
            fps = 24

    return duration, bitrate, fps


# ---------------------------
# 🧠 Alege CRF
# ---------------------------
def choose_crf(bitrate):
    if bitrate < 2_000_000:
        return "22"
    elif bitrate < 5_000_000:
        return "20"
    else:
        return "18"


# ---------------------------
# 🎬 UI
# ---------------------------
root = tk.Tk()
root.withdraw()

video_path = filedialog.askopenfilename(
    title="Selectează video",
    filetypes=[("Video files", "*.mp4 *.mkv *.avi *.mov")]
)

if not video_path:
    exit()

srt_path = filedialog.askopenfilename(
    title="Selectează subtitrarea",
    filetypes=[("Subtitle files", "*.srt")]
)

if not srt_path:
    exit()

folder = os.path.dirname(video_path)
video_name = os.path.splitext(os.path.basename(video_path))[0]

output_path = filedialog.asksaveasfilename(
    title="Salvează ca",
    initialdir=folder,
    initialfile=f"{video_name}.mkv",
    defaultextension=".mkv"
)

if not output_path:
    exit()


# ---------------------------
# 🔍 Analiză
# ---------------------------
duration, bitrate, fps = get_video_info(video_path)

print(f"\n📊 Durată: {duration} sec")
print(f"📊 Bitrate: {bitrate}")
print(f"📊 FPS: {fps:.3f}")

corupt = (
    duration <= 0 or
    duration > 20000 or
    duration > 100000 or
    bitrate == 0
)

# ---------------------------
# ⚙️ Construire comandă
# ---------------------------
if corupt:
    print("⚠️ Video CORUPT → REBUILD COMPLET")

    crf = choose_crf(bitrate)
    print(f"🎯 CRF: {crf}")

    cmd = [
        "ffmpeg",

        "-fflags", "+genpts+igndts",
        "-i", video_path,
        "-i", srt_path,

        "-map", "0:v",
        "-map", "0:a",
        "-map", "1:0",

        # 🔥 video
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", crf,

        # 🔥 timeline nou (modern)
        "-fps_mode", "cfr",
        "-r", str(round(fps, 3)),

        # 🔥 audio (IMPORTANT)
        "-c:a", "aac",
        "-b:a", "192k",

        # subtitrare
        "-c:s", "srt",

        "-metadata:s:s:0", "language=ron",
        "-disposition:s:0", "default",

        output_path
    ]

else:
    print("✅ Video OK → COPY")

    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-i", srt_path,

        "-map", "0:v",
        "-map", "0:a",
        "-map", "1:0",

        "-c:v", "copy",
        "-c:a", "copy",
        "-c:s", "srt",

        "-metadata:s:s:0", "language=ron",
        "-disposition:s:0", "default",

        output_path
    ]


# ---------------------------
# ▶️ Execuție
# ---------------------------
print("\n🚀 Rulez ffmpeg...\n")
subprocess.run(cmd)

print("\n✔ Gata!")
print("📁 Output:", output_path)
