"""
Statistics handler
"""
from telethon import events, Button
from utils.keyboards import stats_menu_keyboard
from utils.helpers import is_admin
from database.db import Database
from config import ADMIN_USER_ID


async def show_stats(event, db: Database):
    """Show bot statistics"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    stats = db.get_stats()
    
    text = f"""
📊 **آمار و گزارش**

📚 **کتاب‌ها:**
• کل کتاب‌ها: {stats.get('total_books', 0)}
• پردازش شده: {stats.get('processed_books', 0)}

📝 **محتوا:**
• کل محتوا: {stats.get('total_content', 0)}
• تایید شده: {stats.get('approved_content', 0)}
• منتشر شده: {stats.get('published_content', 0)}
    """
    
    keyboard = stats_menu_keyboard()
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def show_full_stats(event, db: Database):
    """Show full detailed statistics"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("❌ شما دسترسی به این بخش را ندارید.", alert=True)
        else:
            await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    stats = db.get_stats()
    
    # Get more detailed stats
    all_books = db.get_all_books(limit=1000, offset=0)
    all_content = db.get_content_by_status('', limit=1000, offset=0)  # Get all
    
    # Count by status
    books_by_status = {}
    for book in all_books:
        status = book.get('status', 'unknown')
        books_by_status[status] = books_by_status.get(status, 0) + 1
    
    content_by_status = {}
    content_by_type = {}
    for content in all_content:
        status = content.get('status', 'unknown')
        content_by_status[status] = content_by_status.get(status, 0) + 1
        
        ctype = content.get('type', 'unknown')
        content_by_type[ctype] = content_by_type.get(ctype, 0) + 1
    
    text = f"""
📊 **گزارش کامل آمار**

📚 **کتاب‌ها:**
• کل کتاب‌ها: {stats.get('total_books', 0)}
• پردازش شده: {stats.get('processed_books', 0)}
• در انتظار: {books_by_status.get('pending', 0)}
• در حال پردازش: {books_by_status.get('processing', 0)}
• خطا: {books_by_status.get('error', 0)}

📝 **محتوا:**
• کل محتوا: {stats.get('total_content', 0)}
• پیش‌نویس: {content_by_status.get('draft', 0)}
• تایید شده: {stats.get('approved_content', 0)}
• زمان‌بندی شده: {content_by_status.get('scheduled', 0)}
• منتشر شده: {stats.get('published_content', 0)}
• رد شده: {content_by_status.get('rejected', 0)}

📋 **محتوا بر اساس نوع:**
"""
    
    for ctype, count in content_by_type.items():
        text += f"• {ctype}: {count}\n"
    
    keyboard = [[Button.inline('🔙 بازگشت', b'menu_stats')]]
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')

