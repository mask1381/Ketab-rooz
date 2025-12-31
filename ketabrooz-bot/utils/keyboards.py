"""
Inline keyboard builders for KetabeRooz bot
"""
from telethon import Button
from typing import List, Optional


def main_menu_keyboard() -> List[List[Button]]:
    """Main menu keyboard"""
    return [
        [Button.inline('📚 مدیریت کتاب‌ها', b'menu_books')],
        [Button.inline('📝 مدیریت محتوا', b'menu_content')],
        [Button.inline('⏰ زمان‌بندی', b'menu_schedule')],
        [Button.inline('📊 آمار و گزارش', b'menu_stats')],
        [Button.inline('⚙️ تنظیمات', b'menu_settings')]
    ]


def books_menu_keyboard() -> List[List[Button]]:
    """Books management menu keyboard"""
    return [
        [Button.inline('🔍 اسکن گروه', b'books_scan'),
         Button.inline('📋 لیست کتاب‌ها', b'books_list_1')],
        [Button.inline('🔄 پردازش کتاب', b'books_process'),
         Button.inline('🏷️ دسته‌بندی', b'books_categories')],
        [Button.inline('🔙 بازگشت', b'main_menu')]
    ]


def content_menu_keyboard() -> List[List[Button]]:
    """Content management menu keyboard"""
    return [
        [Button.inline('📄 محتوای در انتظار', b'content_pending_1'),
         Button.inline('✅ محتوای تایید شده', b'content_approved_1')],
        [Button.inline('📤 محتوای منتشر شده', b'content_published_1'),
         Button.inline('➕ محتوای دستی', b'content_manual')],
        [Button.inline('🔙 بازگشت', b'main_menu')]
    ]


def content_approval_keyboard(content_id: int) -> List[List[Button]]:
    """Content approval keyboard for a specific content"""
    return [
        [Button.inline('✅ تایید', f'content_approve_{content_id}'.encode()),
         Button.inline('❌ رد', f'content_reject_{content_id}'.encode())],
        [Button.inline('✏️ ویرایش', f'content_edit_{content_id}'.encode()),
         Button.inline('⏰ زمان‌بندی', f'content_schedule_{content_id}'.encode())],
        [Button.inline('📤 انتشار فوری', f'content_publish_{content_id}'.encode())],
        [Button.inline('🔙 بازگشت', b'menu_content')]
    ]


def schedule_menu_keyboard() -> List[List[Button]]:
    """Schedule management menu keyboard"""
    return [
        [Button.inline('➕ افزودن زمان‌بندی', b'schedule_add')],
        [Button.inline('📋 لیست زمان‌بندی‌ها', b'schedule_list')],
        [Button.inline('🔙 بازگشت', b'main_menu')]
    ]


def stats_menu_keyboard() -> List[List[Button]]:
    """Statistics menu keyboard"""
    return [
        [Button.inline('🔄 بروزرسانی', b'stats_refresh')],
        [Button.inline('📊 گزارش کامل', b'stats_full')],
        [Button.inline('🔙 بازگشت', b'main_menu')]
    ]


def settings_menu_keyboard() -> List[List[Button]]:
    """Settings menu keyboard"""
    return [
        [Button.inline('⚙️ تنظیمات .env', b'env_settings')],
        [Button.inline('🤖 تنظیمات AI', b'settings_ai')],
        [Button.inline('🎨 تنظیمات طراحی', b'settings_design')],
        [Button.inline('📝 تنظیمات محتوا', b'settings_content')],
        [Button.inline('🏷️ مدیریت هشتگ‌ها', b'hashtags_menu')],
        [Button.inline('📝 تنظیمات پانویس', b'footer_settings')],
        [Button.inline('🔙 بازگشت', b'main_menu')]
    ]


def env_settings_keyboard() -> List[List[Button]]:
    """Environment settings keyboard"""
    return [
        [Button.inline('📱 تنظیمات Telegram', b'env_telegram')],
        [Button.inline('👥 گروه‌ها و کانال‌ها', b'env_groups')],
        [Button.inline('🤖 تنظیمات OpenRouter', b'env_openrouter')],
        [Button.inline('💾 تنظیمات دیتابیس', b'env_database')],
        [Button.inline('🌐 سایر تنظیمات', b'env_other')],
        [Button.inline('📋 نمایش همه', b'env_view_all')],
        [Button.inline('🔙 بازگشت', b'menu_settings')]
    ]


def env_category_keyboard(category: str) -> List[List[Button]]:
    """Keyboard for specific env category"""
    buttons = []
    
    if category == 'telegram':
        buttons = [
            [Button.inline('🔑 API_ID', b'env_edit_API_ID')],
            [Button.inline('🔐 API_HASH', b'env_edit_API_HASH')],
            [Button.inline('🤖 BOT_TOKEN', b'env_edit_BOT_TOKEN')]
        ]
    elif category == 'groups':
        buttons = [
            [Button.inline('📥 SOURCE_GROUP_ID', b'env_edit_SOURCE_GROUP_ID')],
            [Button.inline('📤 TARGET_CHANNEL_ID', b'env_edit_TARGET_CHANNEL_ID')],
            [Button.inline('👤 ADMIN_USER_ID', b'env_edit_ADMIN_USER_ID')]
        ]
    elif category == 'openrouter':
        buttons = [
            [Button.inline('🔑 OPENROUTER_API_KEY', b'env_edit_OPENROUTER_API_KEY')],
            [Button.inline('🤖 OPENROUTER_MODEL', b'env_edit_OPENROUTER_MODEL')]
        ]
    elif category == 'database':
        buttons = [
            [Button.inline('📁 DB_PATH', b'env_edit_DB_PATH')]
        ]
    elif category == 'other':
        buttons = [
            [Button.inline('🌐 TIMEZONE', b'env_edit_TIMEZONE')]
        ]
    
    buttons.append([Button.inline('🔙 بازگشت', b'env_settings')])
    return buttons


def pagination_keyboard(current_page: int, total_pages: int, 
                       prefix: str, back_button: bytes = b'main_menu') -> List[List[Button]]:
    """
    Create pagination keyboard
    
    Args:
        current_page: Current page number (1-based)
        total_pages: Total number of pages
        prefix: Button data prefix (e.g., 'books_list')
        back_button: Back button data
    
    Returns:
        List of button rows
    """
    buttons = []
    nav = []
    
    if current_page > 1:
        nav.append(Button.inline('◀️ قبلی', f'{prefix}_{current_page-1}'.encode()))
    
    # Page indicator
    nav.append(Button.inline(f'{current_page}/{total_pages}', b'noop'))
    
    if current_page < total_pages:
        nav.append(Button.inline('بعدی ▶️', f'{prefix}_{current_page+1}'.encode()))
    
    if nav:
        buttons.append(nav)
    
    buttons.append([Button.inline('🔙 بازگشت', back_button)])
    return buttons


def confirm_keyboard(action: str, item_id: Optional[int] = None) -> List[List[Button]]:
    """
    Create confirmation keyboard
    
    Args:
        action: Action name (e.g., 'delete', 'approve')
        item_id: Optional item ID
    
    Returns:
        List of button rows
    """
    if item_id:
        confirm_data = f'{action}_{item_id}'.encode()
        cancel_data = f'{action}_cancel_{item_id}'.encode()
    else:
        confirm_data = f'{action}_confirm'.encode()
        cancel_data = f'{action}_cancel'.encode()
    
    return [
        [Button.inline('✅ تایید', confirm_data),
         Button.inline('❌ لغو', cancel_data)]
    ]


def book_list_keyboard(books: list, page: int = 1, per_page: int = 10) -> List[List[Button]]:
    """
    Create keyboard for book list
    
    Args:
        books: List of book dictionaries
        page: Current page
        per_page: Items per page
    
    Returns:
        List of button rows
    """
    buttons = []
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    for book in books[start_idx:end_idx]:
        title = book.get('title', 'بدون عنوان')[:30]
        buttons.append([
            Button.inline(f"📖 {title}", f"book_view_{book['id']}".encode())
        ])
    
    # Pagination
    total_pages = (len(books) + per_page - 1) // per_page
    if total_pages > 1:
        nav = []
        if page > 1:
            nav.append(Button.inline('◀️', f'books_list_{page-1}'.encode()))
        nav.append(Button.inline(f'{page}/{total_pages}', b'noop'))
        if page < total_pages:
            nav.append(Button.inline('▶️', f'books_list_{page+1}'.encode()))
        buttons.append(nav)
    
    buttons.append([Button.inline('🔙 بازگشت', b'menu_books')])
    return buttons

