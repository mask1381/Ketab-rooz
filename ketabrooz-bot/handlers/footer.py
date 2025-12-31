"""
Footer settings handler
"""
from telethon import events, Button
from utils.helpers import is_admin
from database.db import Database
from config import ADMIN_USER_ID
from datetime import datetime
from typing import Dict

# Store pending footer edits (user_id -> {'action': 'edit_format'|'edit_custom'})
pending_footer_edits: Dict[int, Dict[str, str]] = {}

async def show_footer_settings(event, db: Database):
    """Show footer settings menu"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("❌ شما دسترسی به این بخش را ندارید.", alert=True)
        else:
            await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    settings = db.get_all_footer_settings()
    
    show_id = settings.get('show_content_id', '1') == '1'
    id_format = settings.get('id_format', '🆔 شناسه: {id}')
    custom_text = settings.get('custom_text', '')
    
    text = f"""
📝 **تنظیمات پانویس (Footer)**

پانویس در انتهای هر پیام منتشر شده نمایش داده می‌شود.

**تنظیمات فعلی:**
• نمایش ID: {'✅ فعال' if show_id else '❌ غیرفعال'}
• فرمت ID: `{id_format}`
• متن دلخواه: `{custom_text or '(خالی)'}`

**متغیرهای قابل استفاده:**
• `{{id}}` - ID محتوا
• `{{type}}` - نوع محتوا (فارسی)
• `{{date}}` - تاریخ امروز

گزینه مورد نظر را انتخاب کنید:
    """
    
    keyboard = [
        [Button.inline('👁️ نمایش/مخفی کردن ID', b'footer_toggle_id')],
        [Button.inline('✏️ ویرایش فرمت ID', b'footer_edit_format')],
        [Button.inline('📝 ویرایش متن دلخواه', b'footer_edit_custom')],
        [Button.inline('🔙 بازگشت', b'menu_settings')]
    ]
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def toggle_footer_id(event, db: Database):
    """Toggle footer ID display"""
    user_id = event.sender_id
    if not is_admin(user_id, ADMIN_USER_ID): return
    
    current = db.get_footer_setting('show_content_id', '1')
    new_value = '0' if current == '1' else '1'
    db.set_footer_setting('show_content_id', new_value)
    
    status = 'فعال' if new_value == '1' else 'غیرفعال'
    await event.answer(f"✅ نمایش ID {status} شد!")
    await show_footer_settings(event, db)


async def show_edit_footer_format(event, db: Database):
    """Show form for editing footer format"""
    user_id = event.sender_id
    if not is_admin(user_id, ADMIN_USER_ID): return
    
    current_format = db.get_footer_setting('id_format', '🆔 شناسه: {id}')
    
    text = f"""
✏️ **ویرایش فرمت ID**

فرمت فعلی: `{current_format}`

لطفا فرمت جدید را ارسال کنید (مثلاً `شناسه کتاب: {{id}}`).
برای لغو /cancel را بفرستید.
    """
    pending_footer_edits[user_id] = {'action': 'edit_format'}
    await event.respond(text)


async def show_edit_footer_custom(event, db: Database):
    """Show form for editing custom footer text"""
    user_id = event.sender_id
    if not is_admin(user_id, ADMIN_USER_ID): return
    
    current_text = db.get_footer_setting('custom_text', '')
    
    text = f"""
📝 **ویرایش متن دلخواه پانویس**

متن فعلی: `{current_text or '(خالی)'}`

لطفا متن جدید را ارسال کنید. 
عبارت `حذف` را برای پاک کردن پانویس بفرستید.

برای لغو /cancel را بفرستید.
    """
    pending_footer_edits[user_id] = {'action': 'edit_custom'}
    await event.respond(text)


async def handle_footer_input(event, db: Database):
    """Handle user input for footer settings"""
    user_id = event.sender_id
    if user_id not in pending_footer_edits:
        return False
        
    action = pending_footer_edits[user_id]['action']
    text = event.message.text.strip()
    
    if text == '/cancel':
        del pending_footer_edits[user_id]
        return False

    if action == 'edit_format':
        db.set_footer_setting('id_format', text)
        await event.respond(f"✅ فرمت ID با موفقیت تغییر کرد:\n`{text}`")
    
    elif action == 'edit_custom':
        if text == 'حذف':
            db.set_footer_setting('custom_text', '')
            await event.respond("✅ متن دلخواه پانویس حذف شد.")
        else:
            db.set_footer_setting('custom_text', text)
            await event.respond(f"✅ متن دلخواه پانویس ثبت شد:\n\n{text}")
            
    del pending_footer_edits[user_id]
    await show_footer_settings(event, db)
    return True


def format_footer(content_id: int, content_type: str, db: Database) -> str:
    """Format footer text based on settings"""
    try:
        settings = db.get_all_footer_settings()
        footer_parts = []
        
        type_fa = {
            'quote': 'نقل‌قول', 'description': 'توضیحات', 'summary': 'خلاصه',
            'image': 'تصویر', 'video': 'ویدیو', 'audio': 'صوت'
        }.get(content_type, 'محتوا')
        
        date_str = datetime.now().strftime('%Y/%m/%d')
        
        if settings.get('show_content_id', '1') == '1':
            id_format = settings.get('id_format', '🆔 شناسه: {id}')
            formatted_id = id_format.replace('{id}', str(content_id))\
                                    .replace('{type}', type_fa)\
                                    .replace('{date}', date_str)
            footer_parts.append(formatted_id)
        
        custom_text = settings.get('custom_text', '')
        if custom_text:
            formatted_custom = custom_text.replace('{id}', str(content_id))\
                                        .replace('{type}', type_fa)\
                                        .replace('{date}', date_str)
            footer_parts.append(formatted_custom)
        
        return '\n'.join(footer_parts) if footer_parts else ''
    except Exception as e:
        print(f"Error formatting footer: {e}")
        return ""
