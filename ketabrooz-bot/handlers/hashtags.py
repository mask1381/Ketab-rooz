"""
Hashtag management handler
"""
from telethon import events, Button, TelegramClient
from utils.helpers import is_admin
from database.db import Database
from config import ADMIN_USER_ID
from typing import List


async def show_hashtags_menu(event, db: Database):
    """Show hashtags management menu"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("❌ شما دسترسی به این بخش را ندارید.", alert=True)
        else:
            await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    stats = db.get_stats()
    
    text = f"""
🏷️ **مدیریت هشتگ‌ها**

📊 آمار:
• کل هشتگ‌ها: {stats.get('total_hashtags', 0)}
• تایید شده: {stats.get('approved_hashtags', 0)}

گزینه مورد نظر را انتخاب کنید:
    """
    
    keyboard = [
        [Button.inline('➕ افزودن هشتگ', b'hashtag_add')],
        [Button.inline('📋 لیست هشتگ‌ها', b'hashtag_list')],
        [Button.inline('✅ هشتگ‌های تایید شده', b'hashtag_approved')],
        [Button.inline('⏳ هشتگ‌های در انتظار', b'hashtag_pending')],
        [Button.inline('🔙 بازگشت', b'menu_settings')]
    ]
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def show_add_hashtag_form(event, db: Database):
    """Show form for adding hashtag"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("❌ شما دسترسی به این بخش را ندارید.", alert=True)
        return
    
    text = """
➕ **افزودن هشتگ جدید**

لطفا هشتگ را به فرمت زیر ارسال کنید:

**فرمت:** `#هشتگ|نوع|تعداد`

**مثال:**
```
#کتاب|general|3
#نقل_قول|quote|5
#ادبیات|category|2
```

**نوع‌های هشتگ:**
• `general` - عمومی
• `quote` - نقل‌قول
• `book` - کتاب
• `category` - دسته‌بندی
• `author` - نویسنده

**تعداد:** تعداد هشتگ‌هایی که می‌خواهید استفاده شود (1-10)

برای لغو، /cancel را ارسال کنید.
    """
    
    keyboard = [[Button.inline('🔙 بازگشت', b'hashtags_menu')]]
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def show_hashtags_list(event, db: Database, page: int = 1, filter_type: str = 'all'):
    """Show list of hashtags"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    # Get hashtags based on filter
    if filter_type == 'approved':
        hashtags = db.get_all_hashtags(is_approved=True)
    elif filter_type == 'pending':
        hashtags = db.get_all_hashtags(is_approved=False)
    else:
        hashtags = db.get_all_hashtags()
    
    # Pagination
    per_page = 10
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_hashtags = hashtags[start_idx:end_idx]
    total_pages = (len(hashtags) + per_page - 1) // per_page
    
    if not paginated_hashtags:
        text = "🏷️ هیچ هشتگی یافت نشد."
        keyboard = [[Button.inline('🔙 بازگشت', b'hashtags_menu')]]
    else:
        text = f"🏷️ **لیست هشتگ‌ها**\n\n"
        keyboard_rows = []
        
        for tag in paginated_hashtags:
            status = "✅" if tag.get('is_approved') else "⏳"
            tag_text = tag.get('tag', '')
            text += f"{status} `#{tag_text}`\n"
            text += f"   نوع: {tag.get('tag_type', 'general')} | تعداد: {tag.get('count', 1)}\n\n"
            
            # Add buttons for each tag
            tag_id = tag.get('id')
            if tag_id:
                if not tag.get('is_approved'):
                    keyboard_rows.append([
                        Button.inline(f'✅ تایید #{tag_text}', f'hashtag_approve_{tag_id}'.encode()),
                        Button.inline('❌ حذف', f'hashtag_delete_{tag_id}'.encode())
                    ])
                else:
                    keyboard_rows.append([
                        Button.inline('❌ حذف', f'hashtag_delete_{tag_id}'.encode())
                    ])
        
        # Pagination keyboard
        from utils.keyboards import pagination_keyboard
        pagination = pagination_keyboard(page, total_pages, f'hashtag_list_{filter_type}', b'hashtags_menu')
        keyboard = keyboard_rows + pagination
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def handle_hashtag_input(event, db: Database):
    """Handle hashtag input from user"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        return False
    
    try:
        # Check if it's a file (if file, it's NOT a hashtag)
        if event.file:
            return False
            
        text = event.message.text.strip() if event.message.text else ""
        if not text:
            return False
        
        # ONLY process if it starts with # OR is in the pipe format (#tag|type|count)
        if not text.startswith('#'):
            return False
            
        # Parse hashtag input
        # Format: #tag|type|count
        tag = text
        tag_type = 'general'
        count = 1
        
        if '|' in text:
            parts = text.split('|')
            tag = parts[0].replace('#', '').strip()
            if len(parts) > 1:
                tag_type = parts[1].strip() or 'general'
            if len(parts) > 2:
                try:
                    count = int(parts[2].strip())
                    count = max(1, min(10, count))  # Limit between 1-10
                except:
                    count = 1
        else:
            tag = text.replace('#', '').strip()
        
        if not tag:
            return False
        
        # Add hashtag
        tag_id = db.add_hashtag(tag, tag_type, count)
        
        if tag_id:
            await event.respond(
                f"✅ هشتگ `#{tag}` با موفقیت اضافه شد!\n\n"
                f"نوع: {tag_type}\n"
                f"تعداد: {count}\n"
                f"وضعیت: ⏳ در انتظار تایید"
            )
        else:
            await event.respond("⚠️ این هشتگ قبلا وجود دارد.")
        
        return True
        
    except Exception as e:
        print(f"Error handling hashtag input: {str(e)}")
        return False


async def approve_hashtag(event, db: Database, tag_id: int):
    """Approve a hashtag"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("❌ شما دسترسی به این بخش را ندارید.", alert=True)
        return
    
    try:
        db.approve_hashtag(tag_id)
        tag = db.get_hashtag(tag_id)
        
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer(f"✅ هشتگ #{tag.get('tag', '')} تایید شد!")
        else:
            await event.respond(f"✅ هشتگ #{tag.get('tag', '')} تایید شد!")
        
        # Show hashtags list again
        await show_hashtags_list(event, db, 1, 'all')
    
    except Exception as e:
        print(f"Error approving hashtag: {str(e)}")
        await event.answer(f"❌ خطا: {str(e)}", alert=True)


async def delete_hashtag(event, db: Database, tag_id: int):
    """Delete a hashtag"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("❌ شما دسترسی به این بخش را ندارید.", alert=True)
        return
    
    try:
        tag = db.get_hashtag(tag_id)
        db.delete_hashtag(tag_id)
        
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer(f"✅ هشتگ #{tag.get('tag', '')} حذف شد!")
        else:
            await event.respond(f"✅ هشتگ #{tag.get('tag', '')} حذف شد!")
        
        # Show hashtags list again
        await show_hashtags_list(event, db, 1, 'all')
    
    except Exception as e:
        print(f"Error deleting hashtag: {str(e)}")
        await event.answer(f"❌ خطا: {str(e)}", alert=True)
