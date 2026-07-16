import os
import static_ffmpeg
static_ffmpeg.add_paths()
from pydub import AudioSegment

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "static", "stadium_crowd.mp3")
dest_mp3 = os.path.join(current_dir, "static", "stadium_crowd_low.mp3")
dest_webp = os.path.join(current_dir, "static", "stadium_crowd_low.webp")

print(f"Loading {src_path}...")
sound = AudioSegment.from_mp3(src_path)

# ลดระดับเสียงลง -23 dB (เพื่อเสียงเชียร์สนามกล่อมๆ เบาๆ พรีเมียมขั้นสุด)
print("Reducing volume by -23 dB...")
sound_low = sound - 23

print(f"Exporting to {dest_mp3}...")
sound_low.export(dest_mp3, format="mp3")

print(f"Copying to {dest_webp}...")
import shutil
shutil.copyfile(dest_mp3, dest_webp)
print("Successfully adjusted background volume!")
