import os
import subprocess
from pytubefix import YouTube

# 影片的URL
video_url = "https://youtu.be/Fwmm-fW0fFY?si=RLsrVGAemRccQalL"

# 下載檔案的輸出目錄
output_dir = "downloads"

# 如果輸出目錄不存在，則創建它
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 初始化Pytube物件
yt = YouTube(video_url)

# 獲取非進行式流（最高品質的音頻和影片分開）
non_progressive_stream = yt.streams.filter(progressive=False).first()

# 下載非進行式流
non_progressive_stream.download(output_path=output_dir)

# 獲取已下載的影片和音頻檔案路徑
video_file = os.path.join(output_dir, non_progressive_stream.default_filename)
audio_file = os.path.join(output_dir, non_progressive_stream.default_filename.replace(".webm", ".m4a"))

# 使用ffmpeg將影片和音頻檔案合併
output_file = os.path.join(output_dir, "merged.mp4")
subprocess.run(["ffmpeg", "-i", video_file, "-i", audio_file, "-c:v", "copy", "-c:a", "aac", output_file])

# 列印成功訊息
print(f"已將影片和音頻檔案合併為 {output_file}")
