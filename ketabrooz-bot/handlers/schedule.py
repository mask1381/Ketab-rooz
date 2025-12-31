"""
Schedule management handler
"""
from telethon import events, Button
from utils.keyboards import schedule_menu_keyboard, pagination_keyboard
from utils.helpers import is_admin
from database.db import Database
from config import ADMIN_USER_ID


async def show_schedule_menu(event, db: Database):
    """Show schedule management menu"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    text = """
⏰ **مدیریت زمان‌بندی**

گزینه مورد نظر را انتخاب کنید:
    """
    
    keyboard = schedule_menu_keyboard()
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def show_add_schedule_form(event, db: Database):
    """Show form for adding schedule"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("❌ شما دسترسی به این بخش را ندارید.", alert=True)
        else:
            await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    text = """
➕ **افزودن زمان‌بندی جدید**

برای افزودن زمان‌بندی، لطفا اطلاعات زیر را به ترتیب ارسال کنید:

1️⃣ **روز هفته** (0=شنبه، 1=یکشنبه، ...، 6=جمعه)
2️⃣ **ساعت** (فرمت: HH:MM مثل 14:30)
3️⃣ **نوع محتوا** (مثل: quote,summary یا همه)
4️⃣ **تعداد پست** (پیش‌فرض: 1)

مثال:
```
1
14:30
quote,summary
2
```

برای لغو، /cancel را ارسال کنید.
    """
    
    keyboard = [[Button.inline('🔙 بازگشت', b'menu_schedule')]]
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def show_schedule_list(event, db: Database):
    """Show list of schedule patterns"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    schedules = db.get_schedule_patterns(is_active=True)
    
    if not schedules:
        text = "⏰ هیچ زمان‌بندی فعالی یافت نشد."
        keyboard = [[Button.inline('🔙 بازگشت', b'menu_schedule')]]
    else:
        text = "⏰ **لیست زمان‌بندی‌ها**\n\n"
        days = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه']
        
        for schedule in schedules:
            day_name = days[schedule.get('day_of_week', 0)] if schedule.get('day_of_week', 0) < 7 else 'نامشخص'
            text += f"📅 **{day_name}** - {schedule.get('time', 'N/A')}\n"
            text += f"   نوع: {schedule.get('content_types', 'همه')}\n"
            text += f"   تعداد: {schedule.get('posts_count', 1)}\n"
            text += f"   وضعیت: {'✅ فعال' if schedule.get('is_active') else '❌ غیرفعال'}\n\n"
        
        keyboard = [[Button.inline('🔙 بازگشت', b'menu_schedule')]]
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')

