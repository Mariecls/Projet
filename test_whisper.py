import whisper
import os

print("[TEST] Loading Whisper model...")
model = whisper.load_model("base")
print("✓ Whisper loaded!\n")

# Chercher vidéos
videos_dir = "mtedx_fr/videos"
if os.path.exists(videos_dir):
    videos = [f for f in os.listdir(videos_dir) if f.endswith(('.flac', '.wav', '.mp3', '.m4a', '.mp4', '.webm'))]
    print(f"✓ Found {len(videos)} videos in {videos_dir}")
    if videos:
        print(f"  First video: {videos[0]}")
    else:
        print("❌ No videos found")
else:
    print(f"❌ Directory not found: {videos_dir}")