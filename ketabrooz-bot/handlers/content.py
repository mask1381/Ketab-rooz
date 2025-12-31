"""
Content management handler - Fix for AI content preview
"""
from telethon import events, Button, TelegramClient
from utils.keyboards import content_menu_keyboard, content_approval_keyboard, pagination_keyboard
from utils.helpers import format_content_info, is_admin
from database.db import Database
from config import ADMIN_USER_ID, TARGET_CHANNEL_ID
from core.publisher import Publisher
from datetime import datetime


async def show_content_menu(event, db: Database):
    """Show content management menu"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    text = """
📝 **مدیریت محتوا**

گزینه مورد نظر را انتخاب کنید:
    """
    
    keyboard = content_menu_keyboard()
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def show_pending_content(event, db: Database, page: int = 1):
    """Show pending content for approval"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    # Get both draft and pending_approval content
    draft_content = db.get_content_by_status('draft', limit=1000, offset=0)
    pending_content = db.get_content_by_status('pending_approval', limit=1000, offset=0)
    all_content = draft_content + pending_content
    
    # Sort by created_date
    all_content.sort(key=lambda x: x.get('created_date', ''), reverse=True)
    
    # Apply pagination
    total_count = len(all_content)
    start_idx = (page - 1) * 10
    end_idx = start_idx + 10
    content_list = all_content[start_idx:end_idx]
    
    if not content_list:
        text = "📝 هیچ محتوای در انتظاری یافت نشد."
        from telethon import Button
        keyboard = [[Button.inline('🔙 بازگشت', b'menu_content')]]
    else:
        text = f"📝 **محتوای در انتظار تایید**\n\n"
        keyboard_rows = []
        
        for content_item in content_list:
            content_id = content_item.get('id')
            content_type = content_item.get('type', 'text')
            content_preview = content_item.get('text', content_item.get('caption', ''))[:50]
            
            text += f"🆔 {content_id} - {content_type}"
            if content_preview:
                text += f": {content_preview}...\n"
            else:
                text += "\n"
            
            # Add button for each item
            if content_id:
                keyboard_rows.append([
                    Button.inline(f"📋 مشاهده {content_id}", f'content_view_{content_id}'.encode())
                ])
        
        # Add pagination
        total_pages = (total_count + 9) // 10
        pagination = pagination_keyboard(page, total_pages, 'content_pending', b'menu_content')
        keyboard = keyboard_rows + pagination
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def approve_content(event, db: Database, content_id: int):
    """Approve content"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("❌ شما دسترسی به این بخش را ندارید.", alert=True)
        else:
            await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    from datetime import datetime
    
    db.update_content(content_id, status='approved', approved_date=datetime.now())
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.answer("✅ محتوا تایید شد.")
    else:
        await event.respond("✅ محتوا تایید شد.")
    
    # Show content menu again
    await show_content_menu(event, db)


async def reject_content(event, db: Database, content_id: int):
    """Reject content"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("❌ شما دسترسی به این بخش را ندارید.", alert=True)
        else:
            await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    db.update_content(content_id, status='rejected')
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.answer("❌ محتوا رد شد.")
    else:
        await event.respond("❌ محتوا رد شد.")
    
    # Show content menu again
    await show_content_menu(event, db)


async def show_approved_content(event, db: Database, page: int = 1):
    """Show approved content list"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    content_list = db.get_content_by_status('approved', limit=10, offset=(page - 1) * 10)
    
    if not content_list:
        text = "✅ هیچ محتوای تایید شده‌ای یافت نشد."
        from telethon import Button
        keyboard = [[Button.inline('🔙 بازگشت', b'menu_content')]]
    else:
        text = f"✅ **محتوای تایید شده**\n\n"
        for content in content_list[:5]:  # Show first 5
            text += f"• {format_content_info(content)}\n\n"
        
        total_pages = (len(content_list) + 9) // 10
        keyboard = pagination_keyboard(page, total_pages, 'content_approved', b'menu_content')
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def show_published_content(event, db: Database, page: int = 1):
    """Show published content list"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    content_list = db.get_content_by_status('published', limit=10, offset=(page - 1) * 10)
    
    if not content_list:
        text = "📤 هیچ محتوای منتشر شده‌ای یافت نشد."
        from telethon import Button
        keyboard = [[Button.inline('🔙 بازگشت', b'menu_content')]]
    else:
        text = f"📤 **محتوای منتشر شده**\n\n"
        for content in content_list[:5]:  # Show first 5
            text += f"• {format_content_info(content)}\n\n"
        
        total_pages = (len(content_list) + 9) // 10
        keyboard = pagination_keyboard(page, total_pages, 'content_published', b'menu_content')
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def show_manual_content_form(event, db: Database):
    """Show form for creating manual content"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("❌ شما دسترسی به این بخش را ندارید.", alert=True)
        else:
            await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    text = """
➕ **ارسال محتوای آماده**

حالا می‌توانید محتوای آماده خود را ارسال کنید:

📝 **متن** - برای نقل‌قول و متن
🖼️ **عکس** - با کپشن (اختیاری)
🎥 **ویدیو** - با کپشن (اختیاری)
🎵 **صوت** - با کپشن (اختیاری)

پس از ارسال، محتوا برای تایید و انتشار نمایش داده می‌شود.

برای لغو، /cancel را ارسال کنید.
    """
    
    keyboard = [
        [Button.inline('🤖 تولید با AI', b'content_ai_generate')],
        [Button.inline('🔙 بازگشت', b'menu_content')]
    ]
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def show_ai_content_generator(event, db: Database, bot: TelegramClient):
    """Show AI content generator menu"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("❌ شما دسترسی به این بخش را ندارید.", alert=True)
        else:
            await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    # Get published content history for pattern learning
    published_count = db.get_content_count_by_status('published')
    
    text = f"""
🤖 **تولید محتوا با AI**

این قابلیت با استفاده از تاریخچه پیام‌های منتشر شده در کانال، الگوی پیام‌های شما را یاد می‌گیرد و محتوای مشابه تولید می‌کند.

📊 تعداد پیام‌های منتشر شده: {published_count}

لطفا نوع محتوای مورد نظر را انتخاب کنید:
    """
    
    keyboard = [
        [Button.inline('💬 نقل‌قول', b'ai_generate_quote')],
        [Button.inline('📝 توضیحات', b'ai_generate_description')],
        [Button.inline('📄 خلاصه', b'ai_generate_summary')],
        [Button.inline('🔙 بازگشت', b'content_manual')]
    ]
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def generate_ai_content(event, db: Database, bot: TelegramClient, content_type: str):
    """Generate content using AI based on history"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("❌ شما دسترسی به این بخش را ندارید.", alert=True)
        return
    
    try:
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("🤖 در حال تولید محتوا با AI...")
        
        # Get published content history
        published_content = db.get_content_by_status('published', limit=20, offset=0)
        
        if not published_content:
            await event.respond(
                "⚠️ هیچ محتوای منتشر شده‌ای یافت نشد. لطفا ابتدا چند محتوا منتشر کنید تا AI بتواند الگو را یاد بگیرد.",
                buttons=[[Button.inline('🔙 بازگشت', b'content_ai_generate')]]
            )
            return
        
        # Get book info - use processed books first
        books = db.get_all_books(status='processed', limit=10, offset=0)
        if not books:
            books = db.get_all_books(limit=10, offset=0)
        
        book = None
        book_title = None
        book_author = None
        book_id = None
        book_text = None
        
        # Use first processed book, or first available
        if books:
            book = books[0]
            book_title = book.get('title')
            book_author = book.get('author')
            book_id = book.get('id')
            
            # Get book text from notes (stored during PDF processing)
            book_text = book.get('notes', '') or ''
        
        # Initialize AI generator
        from config import OPENROUTER_API_KEY, OPENROUTER_MODEL
        from core.ai_generator import AIGenerator
        
        ai = AIGenerator(OPENROUTER_API_KEY, OPENROUTER_MODEL)
        
        # Generate content based on history and book text
        result = await ai.generate_content_from_history(
            published_content_history=published_content,
            content_type=content_type,
            book_title=book_title,
            book_author=book_author,
            book_text=book_text
        )
        
        if 'error' in result:
            await event.respond(f"❌ خطا در تولید محتوا: {result['error']}")
            return
        
        # Extract generated content
        if content_type == 'quote':
            text_content = result.get('quote', '')
            caption = result.get('context', '')
        elif content_type == 'description':
            text_content = result.get('description', '')
            caption = f"کتاب {book_title}" if book_title else "کتاب"
        else:  # summary
            text_content = result.get('summary', '')
            caption = f"خلاصه {book_title}" if book_title else "خلاصه کتاب"
        
        if not text_content:
            await event.respond("❌ محتوای تولید شده خالی است.")
            return
        
        # Get book cover if available
        use_cover = False
        cover_file_id = None
        if book_id:
            book = db.get_book(book_id)
            if book and book.get('cover_file_id'):
                use_cover = True
                cover_file_id = book.get('cover_file_id')
        
        # Save to database
        content_id = db.add_content(
            book_id=book_id,
            content_type=content_type,
            text=text_content,
            caption=caption,
            file_id=cover_file_id if use_cover else None,
            is_manual=False,
            use_cover=use_cover,
            status='pending_approval'
        )
        
        # Show preview
        await show_content_preview(event, db, bot, content_id)
        
    except Exception as e:
        print(f"Error generating AI content: {str(e)}")
        await event.respond(f"❌ خطا در تولید محتوا: {str(e)}")


async def handle_content_submission(event, db: Database, bot: TelegramClient):
    """
    Handle content submission from user (text, photo, video, etc.)
    This will save it and show for approval before publishing
    """
    user_id = event.sender_id
    if not is_admin(user_id, ADMIN_USER_ID): return False
    
    try:
        content_type = 'text'
        text_content = event.message.text
        caption = None
        
        # Correctly detect media in Telethon (skip PDF files - they should be handled as books)
        if event.message.media:
            # Check if it's a PDF - skip it (should be handled by books handler)
            if hasattr(event.message.media, 'document'):
                doc = event.message.media.document
                if hasattr(doc, 'mime_type') and doc.mime_type == 'application/pdf':
                    return False  # PDF should be handled by books handler
            
            if event.message.photo:
                content_type = 'image'
            elif event.message.video:
                content_type = 'video'
            elif event.message.audio or event.message.voice:
                content_type = 'audio'
            else:
                content_type = 'file'
            
            caption = event.message.text
            text_content = None # Text is in caption for media

        if not text_content and not event.message.media:
            return False
        
        # Save to database with current message reference
        content_id = db.add_content(
            book_id=None,
            content_type=content_type,
            text=text_content,
            file_id=None, 
            message_id=event.message.id,
            caption=caption,
            is_manual=True,
            status='pending_approval'
        )
        
        # Show preview for approval
        await show_content_preview(event, db, bot, content_id)
        return True
        
    except Exception as e:
        print(f"Error handling content submission: {str(e)}")
        return False


async def show_content_preview(event, db: Database, bot: TelegramClient, content_id: int):
    """Show content preview for approval before publishing"""
    content = db.get_content(content_id)
    if not content:
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("❌ محتوا یافت نشد.", alert=True)
        else:
            await event.respond("❌ محتوا یافت نشد.")
        return
    
    preview_text = f"📋 **پیش‌نمایش محتوا** (ID: {content_id})\n"
    preview_text += f"📝 نوع: {content.get('type', 'text')}\n"
    
    keyboard = [
        [Button.inline('✅ تایید و انتشار', f'content_publish_confirm_{content_id}'.encode()),
         Button.inline('❌ رد', f'content_reject_{content_id}'.encode())],
        [Button.inline('🔙 بازگشت', b'menu_content')]
    ]
    
    # Check if there's a valid message to forward
    source_msg_id = content.get('message_id')
    
    # Handle cover image if use_cover is True
    use_cover = content.get('use_cover', False)
    book_id = content.get('book_id')
    
    # Get book info early for use in all branches
    book = None
    if book_id:
        book = db.get_book(book_id)
    
    # If use_cover, send cover image with text
    if use_cover and book_id and book:
        try:
            book = db.get_book(book_id)
            if book:
                cover_sent = False
                
                # Try to get cover from admin's chat using cover_message_id
                if book and book.get('cover_message_id'):
                    try:
                        from config import ADMIN_USER_ID
                        cover_msg = await bot.get_messages(ADMIN_USER_ID, ids=book.get('cover_message_id'))
                        if cover_msg and cover_msg.media:
                            # Build preview text with book info
                            text_body = content.get('text', '') or content.get('caption', '')
                            
                            # Add book info to preview
                            book_info = ""
                            if book.get('title'):
                                book_info += f"📖 کتاب: {book.get('title')}\n"
                            if book.get('author'):
                                book_info += f"✍️ نویسنده: {book.get('author')}\n"
                            if book.get('category'):
                                book_info += f"🏷️ دسته: {book.get('category')}\n"
                            
                            full_text = f"{preview_text}"
                            if book_info:
                                full_text += f"\n{book_info}"
                            full_text += f"\n📄 متن:\n{text_body[:800]}"
                            
                            await bot.send_file(event.chat_id, cover_msg.media, caption=full_text, buttons=keyboard, parse_mode='md')
                            cover_sent = True
                    except Exception as e:
                        print(f"Error getting cover from storage: {e}")
                
                # Fallback: try using file_id directly if cover_message_id failed
                if not cover_sent and book.get('cover_file_id'):
                    try:
                        # For file_id, we need to send it differently - but Telethon needs message reference
                        # So we'll fall through to text-only preview
                        print(f"Cover file_id available but cover_message_id not accessible")
                    except Exception as e:
                        print(f"Error with cover_file_id: {e}")
                
                if cover_sent:
                    return
        except Exception as e:
            print(f"Error sending cover: {e}")
            import traceback
            traceback.print_exc()
    
    if content.get('type') != 'text' and source_msg_id:
        try:
            await bot.send_message(event.chat_id, preview_text)
            await bot.forward_messages(event.chat_id, source_msg_id, event.sender_id)
            await bot.send_message(event.chat_id, "👆 این محتوا تایید می‌شود؟", buttons=keyboard)
        except Exception as e:
            print(f"Forward error: {e}")
            # Fallback for AI content or if forward fails
            text_body = content.get('text', '') or content.get('caption', '')
            
            # Add book info if available
            book_info = ""
            if book:
                if book.get('title'):
                    book_info += f"📖 کتاب: {book.get('title')}\n"
                if book.get('author'):
                    book_info += f"✍️ نویسنده: {book.get('author')}\n"
                if book.get('category'):
                    book_info += f"🏷️ دسته: {book.get('category')}\n"
            
            full_text = f"{preview_text}"
            if book_info:
                full_text += f"\n{book_info}"
            full_text += f"\n📄 متن:\n{text_body[:1000]}"
            
            await bot.send_message(event.chat_id, full_text, buttons=keyboard, parse_mode='md')
    else:
        # For pure text (or AI generated text without source message)
        text_body = content.get('text', '') or content.get('caption', '')
        
        # Add book info if available (book is already loaded earlier)
        book_info = ""
        if book:
            if book.get('title'):
                book_info += f"📖 کتاب: {book.get('title')}\n"
            if book.get('author'):
                book_info += f"✍️ نویسنده: {book.get('author')}\n"
            if book.get('category'):
                book_info += f"🏷️ دسته: {book.get('category')}\n"
        
        full_text = f"{preview_text}"
        if book_info:
            full_text += f"\n{book_info}"
        full_text += f"\n📄 متن:\n{text_body[:1000]}"
        
        await bot.send_message(event.chat_id, full_text, buttons=keyboard, parse_mode='md')


async def publish_content_to_channel(event, db: Database, bot: TelegramClient, content_id: int):
    """Publish content to target channel after approval"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("❌ شما دسترسی به این بخش را ندارید.", alert=True)
        return
    
    try:
        content = db.get_content(content_id)
        if not content:
            await event.answer("❌ محتوا یافت نشد.", alert=True)
            return
        
        # Initialize publisher
        publisher = Publisher(bot, TARGET_CHANNEL_ID, db)
        
        # Update content to approved first
        db.update_content(content_id, status='approved', approved_date=datetime.now())
        
        # Publish to channel
        published_msg_id = await publisher.publish_content(content_id)
        
        if published_msg_id:
            if isinstance(event, events.CallbackQuery.Event):
                await event.answer("✅ محتوا با موفقیت در کانال منتشر شد!", alert=False)
            else:
                await event.respond("✅ محتوا با موفقیت در کانال منتشر شد!")
            
            # Show success message
            await event.respond(
                f"✅ **محتوا منتشر شد**\n\n"
                f"🆔 ID محتوا: {content_id}\n"
                f"📤 ID پیام در کانال: {published_msg_id}\n"
                f"📝 نوع: {content.get('type', 'text')}"
            )
        else:
            await event.answer("❌ خطا در انتشار محتوا.", alert=True)
    
    except Exception as e:
        print(f"Error publishing content: {str(e)}")
        await event.answer(f"❌ خطا: {str(e)}", alert=True)


async def show_content_for_approval(event, db: Database, content_id: int):
    """Show content details for approval"""
    await show_content_preview(event, db, event.client, content_id)
