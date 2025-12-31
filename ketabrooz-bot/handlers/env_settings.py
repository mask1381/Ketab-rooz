"""
Environment settings (.env) management handler
"""
from telethon import events, TelegramClient
from utils.keyboards import env_settings_keyboard, env_category_keyboard
from utils.helpers import is_admin
from utils.env_manager import EnvManager
from config import ADMIN_USER_ID
from typing import Dict


# Store pending edits (user_id -> {key: value})
pending_edits: Dict[int, Dict[str, str]] = {}


async def show_env_settings_menu(event, env_manager: EnvManager):
    """Show environment settings main menu"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    text = """
⚙️ **مدیریت تنظیمات .env**

از این بخش می‌توانید تمام تنظیمات ربات را مدیریت کنید.

⚠️ **هشدار:** تغییرات در تنظیمات حساس (مثل API keys) نیاز به راه‌اندازی مجدد ربات دارد.
    """
    
    keyboard = env_settings_keyboard()
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def show_env_category(event, env_manager: EnvManager, category: str):
    """Show environment variables for a specific category"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    categories_info = {
        'telegram': {
            'name': '📱 تنظیمات Telegram',
            'vars': ['API_ID', 'API_HASH', 'BOT_TOKEN']
        },
        'groups': {
            'name': '👥 گروه‌ها و کانال‌ها',
            'vars': ['SOURCE_GROUP_ID', 'TARGET_CHANNEL_ID', 'ADMIN_USER_ID']
        },
        'openrouter': {
            'name': '🤖 تنظیمات OpenRouter',
            'vars': ['OPENROUTER_API_KEY', 'OPENROUTER_MODEL']
        },
        'database': {
            'name': '💾 تنظیمات دیتابیس',
            'vars': ['DB_PATH']
        },
        'other': {
            'name': '🌐 سایر تنظیمات',
            'vars': ['TIMEZONE']
        }
    }
    
    if category not in categories_info:
        await event.answer("دسته‌بندی نامعتبر است.", alert=True)
        return
    
    info = categories_info[category]
    all_vars = env_manager.get_all_vars()
    
    text = f"{info['name']}\n\n"
    
    sensitive_keys = ['API_HASH', 'BOT_TOKEN', 'OPENROUTER_API_KEY']
    
    for var_key in info['vars']:
        value = all_vars.get(var_key, '(تنظیم نشده)')
        if var_key in sensitive_keys and value != '(تنظیم نشده)':
            value = env_manager.mask_sensitive_value(value)
        text += f"**{var_key}:** `{value}`\n"
    
    keyboard = env_category_keyboard(category)
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def show_all_env_vars(event, env_manager: EnvManager):
    """Show all environment variables"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    categories = env_manager.get_env_categories()
    all_vars = env_manager.get_all_vars()
    
    text = "📋 **همه تنظیمات .env**\n\n"
    
    sensitive_keys = ['API_HASH', 'BOT_TOKEN', 'OPENROUTER_API_KEY']
    
    for category_name, vars_dict in categories.items():
        text += f"**{category_name}:**\n"
        for key, value in vars_dict.items():
            display_value = value if value else '(خالی)'
            if key in sensitive_keys and display_value != '(خالی)':
                display_value = env_manager.mask_sensitive_value(display_value)
            text += f"  • {key}: `{display_value}`\n"
        text += "\n"
    
    from telethon import Button
    keyboard = [[Button.inline('🔙 بازگشت', b'env_settings')]]
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def start_edit_env_var(event, env_manager: EnvManager, var_key: str):
    """Start editing an environment variable"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    current_value = env_manager.get_var(var_key) or ''
    
    # Mask sensitive values
    sensitive_keys = ['API_HASH', 'BOT_TOKEN', 'OPENROUTER_API_KEY']
    if var_key in sensitive_keys and current_value:
        display_value = env_manager.mask_sensitive_value(current_value)
    else:
        display_value = current_value if current_value else '(خالی)'
    
    text = f"""
✏️ **ویرایش {var_key}**

مقدار فعلی:
`{display_value}`

لطفا مقدار جدید را ارسال کنید:
(برای لغو، /cancel را ارسال کنید)
    """
    
    # Store that we're waiting for this variable
    if user_id not in pending_edits:
        pending_edits[user_id] = {}
    pending_edits[user_id][var_key] = 'waiting'
    
    await event.respond(text, parse_mode='md')


async def handle_env_var_input(event, env_manager: EnvManager, bot: TelegramClient):
    """Handle user input for environment variable"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        return False
    
    # Check if user is editing a variable
    if user_id not in pending_edits:
        return False
    
    # Find which variable is being edited
    var_key = None
    for key, status in pending_edits[user_id].items():
        if status == 'waiting':
            var_key = key
            break
    
    if not var_key:
        return False
    
    # Get new value
    new_value = event.message.text.strip()
    
    # Validate based on variable type
    validation_error = None
    
    if var_key == 'API_ID':
        try:
            int(new_value)
        except ValueError:
            validation_error = "API_ID باید یک عدد باشد."
    elif var_key in ['SOURCE_GROUP_ID', 'TARGET_CHANNEL_ID', 'ADMIN_USER_ID']:
        try:
            int(new_value)
        except ValueError:
            validation_error = f"{var_key} باید یک عدد باشد."
    elif var_key == 'DB_PATH':
        if not new_value:
            validation_error = "DB_PATH نمی‌تواند خالی باشد."
    elif var_key == 'OPENROUTER_MODEL':
        if not new_value.startswith('google/gemini-'):
            validation_error = "مدل باید با 'google/gemini-' شروع شود."
    
    if validation_error:
        await event.respond(f"❌ خطا: {validation_error}\n\nلطفا دوباره تلاش کنید:")
        return True
    
    # Save the variable
    try:
        env_manager.set_var(var_key, new_value)
        
        # Clear pending edit
        del pending_edits[user_id][var_key]
        if not pending_edits[user_id]:
            del pending_edits[user_id]
        
        await event.respond(
            f"✅ **{var_key}** با موفقیت به‌روزرسانی شد!\n\n"
            f"مقدار جدید: `{env_manager.mask_sensitive_value(new_value) if var_key in ['API_HASH', 'BOT_TOKEN', 'OPENROUTER_API_KEY'] else new_value}`\n\n"
            f"⚠️ برای اعمال تغییرات، ربات را راه‌اندازی مجدد کنید."
        )
        
        return True
    
    except Exception as e:
        await event.respond(f"❌ خطا در ذخیره: {str(e)}")
        return True


async def cancel_edit(event):
    """Cancel current edit operation"""
    user_id = event.sender_id
    
    if user_id in pending_edits:
        del pending_edits[user_id]
        await event.respond("❌ ویرایش لغو شد.")
    else:
        await event.respond("هیچ ویرایشی در حال انجام نیست.")

