"""
Books management handler
"""
import asyncio
from telethon import events, TelegramClient, Button
from telethon.tl.types import MessageMediaDocument, InputMessagesFilterDocument, Chat, Channel
from telethon import errors
from telethon.sessions import StringSession
import io
from utils.keyboards import books_menu_keyboard, book_list_keyboard
from utils.helpers import format_book_info, is_admin
from utils.storage import TelegramStorage
from config import ADMIN_USER_ID, OPENROUTER_API_KEY, OPENROUTER_MODEL
from database.db import Database
from core.ai_generator import AIGenerator
from core.pdf_processor import PDFProcessor


# Placeholder functions - need to be restored from backup
async def show_books_menu(event, db: Database):
    """Show books management menu"""
    user_id = event.sender_id
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    text = """
📚 **مدیریت کتاب‌ها (آرشیو)**

گزینه مورد نظر را انتخاب کنید:
    """
    keyboard = books_menu_keyboard()
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def show_books_list(event, db: Database, page: int = 1):
    """Show list of books with pagination"""
    user_id = event.sender_id
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    books = db.get_all_books(limit=10, offset=(page - 1) * 10)
    if not books:
        text = "📚 هیچ کتابی یافت نشد."
        keyboard = [[Button.inline('🔙 بازگشت', b'menu_books')]]
    else:
        text = f"📚 **لیست کتاب‌ها**\n\n"
        for book in books:
            text += f"• {book.get('title', 'بدون عنوان')}\n"
        keyboard = book_list_keyboard(books, page)
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def scan_group_for_pdfs(event, db: Database, bot: TelegramClient):
    """Scan source group for PDF files"""
    # Placeholder - needs full implementation
    await event.answer("در حال توسعه...", alert=True)


async def process_new_pdf(event, db: Database, bot: TelegramClient):
    """Process new PDF file: Save to database, extract data, analyze with AI"""
    user_id = event.sender_id
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    # Check if message has PDF
    if not event.message.media or not hasattr(event.message.media, 'document'):
        await event.respond("❌ لطفا یک فایل PDF ارسال کنید.")
        return
    
    doc = event.message.media.document
    if not hasattr(doc, 'mime_type') or doc.mime_type != 'application/pdf':
        await event.respond("❌ لطفا یک فایل PDF ارسال کنید.")
        return
    
    try:
        # Check if book already exists
        file_id = str(doc.id)
        existing_book = db.get_book_by_file_id(file_id)
        if existing_book:
            await event.respond(f"⚠️ این کتاب قبلا اضافه شده است (ID: {existing_book['id']})")
            return
        
        # Send status message
        status_msg = await event.respond("📥 در حال پردازش فایل PDF...")
        
        # Download PDF
        await status_msg.edit("💾 در حال دانلود فایل...")
        import io
        file_bytes = await bot.download_media(event.message.media, file=io.BytesIO())
        if isinstance(file_bytes, io.BytesIO):
            pdf_data = file_bytes.getvalue()
        elif isinstance(file_bytes, bytes):
            pdf_data = file_bytes
        else:
            with open(file_bytes, 'rb') as f:
                pdf_data = f.read()
        
        # Extract basic info
        await status_msg.edit("📖 در حال استخراج اطلاعات...")
        try:
            extracted_text = PDFProcessor.extract_text(pdf_data, max_pages=50)
            total_pages = PDFProcessor.get_page_count(pdf_data)
            cover_image = PDFProcessor.extract_cover(pdf_data)
        except Exception as e:
            print(f"Error extracting PDF: {str(e)}")
            extracted_text = ""
            total_pages = 0
            cover_image = None
        
        # Get title from filename or default
        title = "کتاب بدون عنوان"
        if hasattr(doc, 'file_name') and doc.file_name:
            title = doc.file_name.replace('.pdf', '').replace('_', ' ')
        
        # Save book to database (without cover for now)
        book_id = db.add_book(
            title=title,
            pdf_file_id=file_id,
            pdf_message_id=event.message.id,
            total_pages=total_pages,
            status='pending'
        )
        
        # Save extracted text to notes
        if extracted_text:
            db.update_book(book_id, notes=extracted_text[:5000])
        
        # Save cover if available (store file_id only, no storage group)
        if cover_image:
            try:
                # Send cover to same chat and get file_id
                cover_msg = await bot.send_file(
                    user_id,
                    cover_image,
                    caption=f"📖 جلد: {title}",
                    force_document=False
                )
                if hasattr(cover_msg.media, 'photo'):
                    cover_file_id = str(cover_msg.media.photo.id)
                elif hasattr(cover_msg.media, 'document'):
                    cover_file_id = str(cover_msg.media.document.id)
                else:
                    cover_file_id = None
                
                if cover_file_id:
                    db.update_book(book_id, cover_file_id=cover_file_id, cover_message_id=cover_msg.id)
            except Exception as e:
                print(f"Error saving cover: {str(e)}")
        
        # Success message
        await status_msg.edit(
            f"✅ **کتاب با موفقیت اضافه شد**\n\n"
            f"📖 عنوان: {title}\n"
            f"🆔 ID: {book_id}\n"
            f"📄 صفحات: {total_pages}\n\n"
            f"💡 از منوی \"پردازش کتاب\" می‌توانید این کتاب را پردازش کنید."
        )
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        await event.respond(f"❌ خطا در پردازش فایل: {str(e)}")


async def show_book_details(event, db: Database, book_id: int):
    """Show book details"""
    # Placeholder - needs full implementation
    await event.answer("در حال توسعه...", alert=True)


async def analyze_book_content(event, db: Database, bot: TelegramClient, book_id: int):
    """Analyze book text content using AI"""
    # Placeholder - needs full implementation
    await event.answer("در حال توسعه...", alert=True)


async def show_process_book_list(event, db: Database, page: int = 1):
    """Show list of books that need processing (pending status)"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("❌ شما دسترسی به این بخش را ندارید.", alert=True)
        else:
            await event.respond("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    # Get books that need processing (pending status)
    books_list = db.get_all_books(status='pending', limit=10, offset=(page - 1) * 10)
    
    if not books_list:
        text = "📚 **پردازش کتاب**\n\n❌ هیچ کتابی در انتظار پردازش یافت نشد.\n\n💡 می‌توانید از \"اسکن گروه\" برای یافتن کتاب‌های جدید استفاده کنید."
        keyboard = [[Button.inline('🔙 بازگشت', b'menu_books')]]
        
        if isinstance(event, events.CallbackQuery.Event):
            await event.edit(text, buttons=keyboard, parse_mode='md')
        else:
            await event.respond(text, buttons=keyboard, parse_mode='md')
        return
    
    # Format list
    text = f"📚 **پردازش کتاب**\n\n"
    text += f"📋 کتاب‌های در انتظار پردازش (صفحه {page}):\n\n"
    
    keyboard = []
    for book in books_list:
        book_id = book['id']
        title = book.get('title', 'بدون عنوان')[:40]
        keyboard.append([Button.inline(f"📖 {title}", f'book_process_{book_id}'.encode())])
    
    # Pagination
    total_books = len(db.get_all_books(status='pending', limit=1000, offset=0))
    total_pages = (total_books + 9) // 10
    
    nav_buttons = []
    if page > 1:
        nav_buttons.append(Button.inline('◀️ قبلی', f'books_process_list_{page - 1}'.encode()))
    if page < total_pages:
        nav_buttons.append(Button.inline('▶️ بعدی', f'books_process_list_{page + 1}'.encode()))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([Button.inline('🔙 بازگشت', b'menu_books')])
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=keyboard, parse_mode='md')
    else:
        await event.respond(text, buttons=keyboard, parse_mode='md')


async def process_existing_book(event, db: Database, bot: TelegramClient, book_id: int):
    """Process an existing book (re-analyze)"""
    user_id = event.sender_id
    
    if not is_admin(user_id, ADMIN_USER_ID):
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("❌ شما دسترسی به این بخش را ندارید.", alert=True)
        return
    
    try:
        book = db.get_book(book_id)
        if not book:
            await event.answer("❌ کتاب یافت نشد.", alert=True)
            return
        
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("📥 در حال پردازش کتاب...", alert=True)
        
        # Show status message
        status_msg = await bot.send_message(
            ADMIN_USER_ID,
            f"📥 پردازش کتاب: {book.get('title', 'بدون عنوان')}\n\nدر حال پردازش..."
        )
        
        # Download PDF from admin's chat (where it was originally sent)
        await status_msg.edit("💾 در حال دانلود فایل PDF...")
        try:
            msg = await bot.get_messages(ADMIN_USER_ID, ids=book['pdf_message_id'])
            if not msg or not msg.media:
                await status_msg.edit("❌ فایل کتاب یافت نشد.")
                return
            
            import io
            file_bytes = await bot.download_media(msg.media, file=io.BytesIO())
            if isinstance(file_bytes, io.BytesIO):
                pdf_data = file_bytes.getvalue()
            elif isinstance(file_bytes, bytes):
                pdf_data = file_bytes
            else:
                with open(file_bytes, 'rb') as f:
                    pdf_data = f.read()
        except Exception as e:
            await status_msg.edit(f"❌ خطا در دانلود فایل: {str(e)}")
            return
        
        # Extract data
        await status_msg.edit("📖 در حال استخراج متن...")
        try:
            from core.pdf_processor import PDFProcessor
            extracted_text = PDFProcessor.extract_text(pdf_data, max_pages=50)
            total_pages = PDFProcessor.get_page_count(pdf_data)
            cover_image = PDFProcessor.extract_cover(pdf_data)
        except Exception as e:
            print(f"Error extracting PDF: {str(e)}")
            extracted_text = ""
            total_pages = book.get('total_pages', 0)
            cover_image = None
        
        # Analyze with AI
        await status_msg.edit("🤖 در حال تحلیل با هوش مصنوعی...")
        book_metadata = {}
        
        try:
            from core.ai_generator import AIGenerator
            from config import OPENROUTER_API_KEY, OPENROUTER_MODEL
            ai = AIGenerator(OPENROUTER_API_KEY, OPENROUTER_MODEL)
            
            # Analyze cover if available
            if cover_image:
                try:
                    cover_analysis = await ai.analyze_image(cover_image)
                    if cover_analysis.get('author'):
                        book_metadata['author'] = cover_analysis['author']
                    if cover_analysis.get('category'):
                        book_metadata['category'] = cover_analysis['category']
                    if cover_analysis.get('tags'):
                        tags_list = cover_analysis['tags'] if isinstance(cover_analysis['tags'], list) else [cover_analysis['tags']]
                        book_metadata['tags'] = ', '.join(tags_list)
                except Exception as e:
                    print(f"Cover analysis error: {str(e)}")
            
            # Analyze text if available
            if extracted_text and len(extracted_text) > 200:
                try:
                    summary_result = await ai.generate_summary(extracted_text, min_words=150, max_words=300)
                    if summary_result.get('genre') and not book_metadata.get('category'):
                        book_metadata['category'] = summary_result['genre']
                except Exception as e:
                    print(f"Text analysis error: {str(e)}")
        except Exception as e:
            print(f"AI analysis error: {str(e)}")
        
        # Save cover if extracted
        cover_file_id = book.get('cover_file_id')
        cover_message_id = book.get('cover_message_id')
        
        if cover_image and not cover_file_id:
            try:
                # Send cover to admin's chat and get file_id
                cover_msg = await bot.send_file(
                    ADMIN_USER_ID,
                    cover_image,
                    caption=f"📖 جلد: {book.get('title', 'کتاب')}",
                    force_document=False
                )
                if hasattr(cover_msg.media, 'photo'):
                    cover_file_id = str(cover_msg.media.photo.id)
                elif hasattr(cover_msg.media, 'document'):
                    cover_file_id = str(cover_msg.media.document.id)
                cover_message_id = cover_msg.id
                book_metadata['cover_file_id'] = cover_file_id
                book_metadata['cover_message_id'] = cover_message_id
            except Exception as e:
                print(f"Error saving cover: {str(e)}")
        
        # Update book in database
        book_metadata['total_pages'] = total_pages
        book_metadata['status'] = 'processed'
        if extracted_text:
            book_metadata['notes'] = extracted_text[:5000]
        
        db.update_book(book_id, **book_metadata)
        
        # Build base result text
        base_result_text = f"✅ **کتاب با موفقیت پردازش شد**\n\n"
        base_result_text += f"📖 **عنوان:** {book.get('title')}\n"
        base_result_text += f"🆔 **ID:** {book_id}\n"
        if book_metadata.get('author'):
            base_result_text += f"✍️ **نویسنده:** {book_metadata['author']}\n"
        if book_metadata.get('category'):
            base_result_text += f"🏷️ **دسته:** {book_metadata['category']}\n"
        if total_pages:
            base_result_text += f"📄 **صفحات:** {total_pages}\n"
        
        # Step: Generate content for the book
        await status_msg.edit(base_result_text + "\n\n🤖 در حال تولید محتوا با AI...")
        
        try:
            # Get published content history for style learning
            published_content = db.get_content_by_status('published', limit=20, offset=0)
            
            # Generate a quote from the book
            content_type = 'quote'
            # Use extracted text (full) or notes (limited) - prefer extracted_text as it's more complete
            book_text_for_gen = extracted_text if extracted_text else (book.get('notes', '') or '')
            
            # Use more text for better quality (up to 3000 chars for variety)
            if book_text_for_gen and len(book_text_for_gen) > 3000:
                # Use middle section for variety (not always from start)
                start_pos = len(book_text_for_gen) // 4  # Start from 25% into the text
                book_text_for_gen = book_text_for_gen[start_pos:start_pos+3000]
            
            if published_content or book_text_for_gen:
                try:
                    # Generate content using AI with enhanced context
                    ai = AIGenerator(OPENROUTER_API_KEY, OPENROUTER_MODEL)
                    
                    result = await ai.generate_content_from_history(
                        published_content_history=published_content if published_content else [],
                        content_type=content_type,
                        book_title=book_title_for_ai,
                        book_author=book_author_for_ai,
                        book_text=book_text_for_gen
                    )
                    
                    if 'error' not in result:
                        # Extract generated content
                        text_content = result.get('quote', '')
                        caption = result.get('context', f"از کتاب {book.get('title')}")
                        
                        if text_content:
                            # Get book cover for content - use the updated book data
                            updated_book = db.get_book(book_id)  # Get fresh data after update
                            use_cover = bool(updated_book and updated_book.get('cover_file_id'))
                            final_cover_file_id = updated_book.get('cover_file_id') if updated_book else cover_file_id
                            
                            # Build better caption with book info
                            enhanced_caption = caption
                            if book_metadata.get('author') or updated_book.get('author'):
                                author_name = book_metadata.get('author') or updated_book.get('author')
                                enhanced_caption = f"از کتاب {book.get('title')}\n✍️ نویسنده: {author_name}"
                            elif book.get('title'):
                                enhanced_caption = f"از کتاب {book.get('title')}"
                            
                            # Save content to database with all book info
                            content_id = db.add_content(
                                book_id=book_id,
                                content_type=content_type,
                                text=text_content,
                                caption=enhanced_caption,
                                file_id=final_cover_file_id if use_cover else None,
                                is_manual=False,
                                use_cover=use_cover,
                                status='pending_approval'
                            )
                            
                            # Update status message
                            final_text = base_result_text + "\n\n✅ محتوا تولید شد!"
                            await status_msg.edit(final_text)
                            
                            # Show preview to admin - import here to avoid circular import
                            from handlers.content import show_content_preview
                            # Create a simple event-like object for preview
                            class PreviewEvent:
                                def __init__(self, chat_id, sender_id):
                                    self.chat_id = chat_id
                                    self.sender_id = sender_id
                            
                            preview_event = PreviewEvent(ADMIN_USER_ID, ADMIN_USER_ID)
                            await show_content_preview(preview_event, db, bot, content_id)
                        else:
                            await status_msg.edit(
                                base_result_text + "\n\n⚠️ محتوا تولید شد اما خالی است."
                            )
                    else:
                        await status_msg.edit(
                            base_result_text + f"\n\n⚠️ خطا در تولید محتوا: {result.get('error', 'خطای نامشخص')}"
                        )
                except Exception as e:
                    print(f"Error generating content: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    await status_msg.edit(
                        base_result_text + f"\n\n⚠️ خطا در تولید محتوا: {str(e)}"
                    )
            else:
                await status_msg.edit(
                    base_result_text + "\n\n⚠️ نمی‌توان محتوا تولید کرد (نیاز به تاریخچه یا متن کتاب)"
                )
        except Exception as e:
            print(f"Error in content generation step: {str(e)}")
            import traceback
            traceback.print_exc()
            # Don't fail the whole process if content generation fails
            await status_msg.edit(
                base_result_text + "\n\n✅ کتاب پردازش شد (تولید محتوا با خطا مواجه شد)"
            )
        
    except Exception as e:
        print(f"Error processing book: {str(e)}")
        import traceback
        traceback.print_exc()
        try:
            await bot.send_message(
                ADMIN_USER_ID,
                f"❌ خطا در پردازش کتاب:\n{str(e)}"
            )
        except:
            pass
