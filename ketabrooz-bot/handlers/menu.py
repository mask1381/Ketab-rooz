"""
Main menu handler for KetabeRooz bot
"""
from telethon import events
from telethon.tl.types import User
from utils.keyboards import main_menu_keyboard
from utils.helpers import is_admin
from config import ADMIN_USER_ID


async def show_main_menu(event, db):
    """
    Show main menu to user
    
    Args:
        event: Telegram event
        db: Database instance
    """
    user_id = event.sender_id
    
    # Check if user is admin
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این ربات را ندارید.")
        return
    
    welcome_text = """
🤖 **ربات مدیریت کانال کتاب روز**

به پنل مدیریت خوش آمدید!

لطفا یکی از گزینه‌های زیر را انتخاب کنید:
    """
    
    keyboard = main_menu_keyboard()
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(welcome_text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(welcome_text, buttons=keyboard, parse_mode='md')

