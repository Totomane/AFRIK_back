# Test video creation script - creates a simple MP4 file for testing
import os

# Create a small test video file (we'll just create a placeholder file for now)
test_video_content = b'This is a test video file for YouTube upload testing'

# Ensure media directory exists
media_dir = r'c:\Users\PC\Desktop\Backend\media'
if not os.path.exists(media_dir):
    os.makedirs(media_dir)

# Create test video file
test_video_path = os.path.join(media_dir, 'test_video.mp4')
with open(test_video_path, 'wb') as f:
    f.write(test_video_content)

print(f"Test video created at: {test_video_path}")
print(f"File size: {len(test_video_content)} bytes")