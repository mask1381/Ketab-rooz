"""
Settings handler with StateManager - Full Version
"""
from telethon import events, Button
from utils.keyboards import settings_menu_keyboard
from utils.helpers import is_admin
from utils.state_manager import StateManager
from database.db import Database
from config import ADMIN_USER_ID


async def show_settings_menu(event, db: Database):
    """Show settings menu"""
    user_id = event.sender_id
    if not is_admin(user_id, ADMIN_USER_ID): return
    
    StateManager.clear_state(user_id)
    
    text = "⚙️ **تنظیمات**\n\nگزینه مورد نظر را انتخاب کنید:"
    keyboard = settings_menu_keyboard()
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def start_edit_setting(event, db: Database, setting_key: str, label: str):
    """Start editing a setting"""
    user_id = event.sender_id
    current_value = db.get_setting(setting_key, "تعریف نشده")
    
    text = f"✏️ **ویرایش {label}**\n\nمقدار فعلی: `{current_value}`\n\nلطفا مقدار جدید را بفرستید:"
    
    StateManager.set_state(user_id, 'EDIT_SETTING', {'key': setting_key, 'label': label})
    await event.respond(text)


async def handle_setting_input(event, db: Database):
    """Process text input for settings"""
    user_id = event.sender_id
    if StateManager.get_state(user_id) != 'EDIT_SETTING':
        return False
        
    metadata = StateManager.get_metadata(user_id)
    new_value = event.message.text.strip()
    
    db.set_setting(metadata['key'], new_value)
    StateManager.clear_state(user_id)
    
    await event.respond(f"✅ تنظیم **{metadata['label']}** بروزرسانی شد.")
    # Show the relevant menu again based on the key
    if metadata['key'] in ['ai_model', 'quote_count']: await show_ai_settings(event, db)
    elif metadata['key'] in ['design_template', 'font_size', 'bg_color']: await show_design_settings(event, db)
    else: await show_settings_menu(event, db)
    return True


async def show_ai_settings(event, db: Database):
    """Show AI settings"""
    settings = db.get_all_settings()
    text = "🤖 **تنظیمات AI**\n\n"
    
    items = [
        ('ai_model', 'مدل AI'),
        ('quote_count', 'تعداد نقل‌قول'),
        ('summary_length_min', 'حداقل طول خلاصه'),
        ('summary_length_max', 'حداکثر طول خلاصه')
    ]
    
    for key, label in items:
        val = settings.get(key, {}).get('value', 'تعریف نشده')
        text += f"• **{label}:** `{val}`\n"
        
    keyboard = [
        [Button.inline('✏️ مدل AI', b'set_edit_ai_model'), Button.inline('✏️ تعداد نقل‌قول', b'set_edit_quote_count')],
        [Button.inline('✏️ حداقل خلاصه', b'set_edit_summary_length_min'), Button.inline('✏️ حداکثر خلاصه', b'set_edit_summary_length_max')],
        [Button.inline('🔙 بازگشت', b'menu_settings')]
    ]
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def show_design_settings(event, db: Database):
    """Show design settings"""
    settings = db.get_all_settings()
    text = "🎨 **تنظیمات طراحی**\n\n"
    
    items = [
        ('design_template', 'قالب طراحی'),
        ('font_size', 'اندازه فونت'),
        ('bg_color', 'رنگ پس‌زمینه')
    ]
    
    for key, label in items:
        val = settings.get(key, {}).get('value', 'تعریف نشده')
        text += f"• **{label}:** `{val}`\n"
        
    keyboard = [
        [Button.inline('✏️ قالب', b'set_edit_design_template'), Button.inline('✏️ فونت', b'set_edit_font_size')],
        [Button.inline('✏️ رنگ پس‌زمینه', b'set_edit_bg_color')],
        [Button.inline('🔙 بازگشت', b'menu_settings')]
    ]
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def show_content_settings(event, db: Database):
    """Show content settings"""
    settings = db.get_all_settings()
    text = "📝 **تنظیمات محتوا**\n\n"
    
    # You can add more specific content settings here
    items = [
        ('hashtag_enabled', 'هشتگ خودکار'),
        ('footer_enabled', 'پانویس خودکار')
    ]
    
    for key, label in items:
        val = settings.get(key, {}).get('value', 'تعریف نشده')
        status = "✅ فعال" if val == '1' else "❌ غیرفعال"
        text += f"• **{label}:** {status}\n"
        
    keyboard = [
        [Button.inline('🏷️ تغییر وضعیت هشتگ', b'set_toggle_hashtag_enabled')],
        [Button.inline('📝 تغییر وضعیت پانویس', b'set_toggle_footer_enabled')],
        [Button.inline('🔙 بازگشت', b'menu_settings')]
    ]
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')
