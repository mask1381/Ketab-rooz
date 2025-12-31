"""
Image generation with Pillow for quote images
"""
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
from typing import Optional
import os


class ImageCreator:
    """Image creator for quote and content images"""
    
    def __init__(self, font_path: str, settings: dict):
        self.font_path = font_path
        self.settings = settings
    
    def reshape_persian(self, text: str) -> str:
        """Reshape Persian text for correct display"""
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except Exception:
            return text
    
    def hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def create_quote_image(self, quote_text: str, book_title: str, 
                           author: Optional[str] = None) -> Image.Image:
        """
        Create quote image with Persian text
        
        Args:
            quote_text: Quote text
            book_title: Book title
            author: Optional author name
        
        Returns:
            PIL Image object
        """
        # Image size
        width, height = 1080, 1080
        
        # Background color from settings
        bg_color = self.hex_to_rgb(self.settings.get('bg_color', '#1a1a2e'))
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Load font
        font_size = int(self.settings.get('font_size', 60))
        try:
            if os.path.exists(self.font_path):
                font = ImageFont.truetype(self.font_path, font_size)
                font_small = ImageFont.truetype(self.font_path, font_size // 2)
            else:
                # Fallback to default font
                font = ImageFont.load_default()
                font_small = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Reshape Persian text
        quote_reshaped = self.reshape_persian(quote_text)
        title_text = f"— {book_title}"
        if author:
            title_text += f" ({author})"
        title_reshaped = self.reshape_persian(title_text)
        
        # Calculate text position (centered)
        # Simple text wrapping for quote
        words = quote_text.split()
        lines = []
        current_line = []
        max_width = width - 200
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            # Rough estimate of text width
            if len(test_line) * (font_size // 2) > max_width and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw quote text (centered vertically)
        y_start = height // 2 - (len(lines) * font_size) // 2
        for i, line in enumerate(lines):
            line_reshaped = self.reshape_persian(line)
            # Get text bbox for centering
            bbox = draw.textbbox((0, 0), line_reshaped, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = y_start + i * font_size
            draw.text((x, y), line_reshaped, font=font, fill='white')
        
        # Draw book title (bottom)
        title_bbox = draw.textbbox((0, 0), title_reshaped, font=font_small)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        title_y = height - 150
        draw.text((title_x, title_y), title_reshaped, font=font_small, fill='gray')
        
        # Watermark
        watermark = self.reshape_persian('@KetabehRooz')
        draw.text((width - 20, height - 20), watermark, font=font_small, 
                 fill='gray', anchor='rb')
        
        return img

