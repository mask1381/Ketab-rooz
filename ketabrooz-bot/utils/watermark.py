"""
Watermarking utility for images and videos
"""
import os
import tempfile
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from config import TARGET_CHANNEL_ID

def add_watermark_image(image_bytes: bytes, text: str = None) -> bytes:
    """
    Add transparent watermark to image
    
    Args:
        image_bytes: Input image bytes
        text: Watermark text (defaults to TARGET_CHANNEL_ID)
    
    Returns:
        Watermarked image bytes
    """
    if not text:
        text = str(TARGET_CHANNEL_ID).replace('-100', '').replace('-', '')
        text = f"@{text}" if not text.startswith('@') else text
        
    try:
        # Open image
        import io
        base_image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        
        # Make a blank image for the text, initialized to transparent text color
        txt = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
        
        # Get a font
        font_size = int(base_image.size[1] / 20) # Responsive font size
        try:
            # Try to load a font, otherwise default
            font = ImageFont.truetype("fonts/Vazir.ttf", font_size)
        except:
            font = ImageFont.load_default()
            
        # Initialize ImageDraw
        d = ImageDraw.Draw(txt)
        
        # Calculate text position (Center or Bottom Right)
        # We'll go with bottom right with some padding
        # bbox = d.textbbox((0, 0), text, font=font) # Python 3.10+
        # width = bbox[2] - bbox[0]
        # height = bbox[3] - bbox[1]
        
        # Compatibility with older Pillow
        width, height = d.textsize(text, font=font)
        
        x = base_image.size[0] - width - 20
        y = base_image.size[1] - height - 20
        
        # Draw text with transparency (White with alpha=128)
        d.text((x, y), text, font=font, fill=(255, 255, 255, 128))
        
        # Overlay
        out = Image.alpha_composite(base_image, txt)
        
        # Convert back to RGB
        out = out.convert("RGB")
        
        # Save to bytes
        output_buffer = io.BytesIO()
        out.save(output_buffer, format="JPEG", quality=90)
        return output_buffer.getvalue()
        
    except Exception as e:
        print(f"Watermark Error: {e}")
        return image_bytes

def add_watermark_video(video_path: str, text: str = None) -> str:
    """
    Add watermark to video using ffmpeg
    
    Args:
        video_path: Path to input video
        text: Watermark text
        
    Returns:
        Path to output video (or input path if failed)
    """
    # Check for ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("FFmpeg not found. Skipping video watermark.")
        return video_path

    if not text:
        text = str(TARGET_CHANNEL_ID).replace('-100', '').replace('-', '')
        text = f"@{text}" if not text.startswith('@') else text
        
    try:
        output_path = video_path.replace('.mp4', '_watermarked.mp4')
        
        # FFmpeg command to add text watermark
        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-vf', f"drawtext=text='{text}':fontcolor=white@0.5:fontsize=h/20:x=w-tw-10:y=h-th-10",
            '-c:a', 'copy', output_path
        ]
        
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(output_path):
            return output_path
        return video_path
        
    except Exception as e:
        print(f"Video Watermark Error: {e}")
        return video_path
