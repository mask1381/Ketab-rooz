"""
Helper functions for KetabeRooz bot
"""
import arabic_reshaper
from bidi.algorithm import get_display
from typing import Optional


def reshape_persian(text: str) -> str:
    """
    Reshape Persian text for correct display
    
    Args:
        text: Persian text
    
    Returns:
        Reshaped text ready for display
    """
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        # Fallback to original text if reshaping fails
        return text


def format_book_info(book: dict) -> str:
    """
    Format book information for display
    
    Args:
        book: Book dictionary from database
    
    Returns:
        Formatted string
    """
    lines = []
    lines.append(f"📖 **{book.get('title', 'بدون عنوان')}**")
    
    if book.get('author'):
        lines.append(f"✍️ نویسنده: {book['author']}")
    
    if book.get('category'):
        lines.append(f"🏷️ دسته: {book['category']}")
    
    if book.get('total_pages'):
        lines.append(f"📄 صفحات: {book['total_pages']}")
    
    status_emoji = {
        'pending': '⏳',
        'processing': '🔄',
        'processed': '✅',
        'error': '❌'
    }
    status = book.get('status', 'pending')
    emoji = status_emoji.get(status, '❓')
    lines.append(f"{emoji} وضعیت: {status}")
    
    return "\n".join(lines)


def format_content_info(content: dict) -> str:
    """
    Format content information for display
    
    Args:
        content: Content dictionary from database
    
    Returns:
        Formatted string
    """
    lines = []
    
    type_emoji = {
        'quote': '💬',
        'summary': '📝',
        'image': '🖼️',
        'video': '🎥',
        'audio': '🎵'
    }
    
    content_type = content.get('type', 'unknown')
    emoji = type_emoji.get(content_type, '📄')
    lines.append(f"{emoji} نوع: {content_type}")
    
    if content.get('book_title'):
        lines.append(f"📖 کتاب: {content['book_title']}")
    
    status_emoji = {
        'draft': '📝',
        'approved': '✅',
        'scheduled': '⏰',
        'published': '📤',
        'rejected': '❌'
    }
    status = content.get('status', 'draft')
    emoji = status_emoji.get(status, '❓')
    lines.append(f"{emoji} وضعیت: {status}")
    
    if content.get('caption'):
        caption = content['caption'][:100]
        lines.append(f"\n{caption}...")
    
    return "\n".join(lines)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def parse_callback_data(data: bytes) -> tuple:
    """
    Parse callback data into action and parameters
    
    Args:
        data: Callback data bytes
    
    Returns:
        Tuple of (action, *params)
    """
    try:
        decoded = data.decode('utf-8')
        parts = decoded.split('_')
        return tuple(parts)
    except Exception:
        return (data.decode('utf-8'),)


def is_admin(user_id: int, admin_id: int) -> bool:
    """
    Check if user is admin
    
    Args:
        user_id: User ID to check
        admin_id: Admin user ID
    
    Returns:
        True if user is admin
    """
    return user_id == admin_id

