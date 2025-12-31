"""
Main entry point for KetabeRooz Telegram bot - Full Restored Version
"""
import asyncio
import sys
from telethon import TelegramClient, events, Button

# Import configuration
from config import (
    API_ID, API_HASH, BOT_TOKEN, SOURCE_GROUP_ID, 
    ADMIN_USER_ID, DB_PATH, TARGET_CHANNEL_ID, validate_config
)

# Import database
from database.db import Database

# Import handlers
from handlers import menu, books, content, schedule, stats, settings, env_settings, hashtags, footer

# Import utilities
from utils.helpers import parse_callback_data, is_admin
from utils.env_manager import EnvManager
from utils.state_manager import StateManager


# Initialize bot
bot = TelegramClient('ketabrooz_bot', API_ID, API_HASH)
db = Database(DB_PATH)
env_manager = EnvManager('.env')


@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Handle /start command"""
    if not is_admin(event.sender_id, ADMIN_USER_ID):
        await event.respond("❌ شما دسترسی به این ربات را ندارید.")
        return
    await menu.show_main_menu(event, db)


@bot.on(events.CallbackQuery)
async def callback_handler(event):
    """Handle all callback queries with full routing"""
    user_id = event.sender_id
    if not is_admin(user_id, ADMIN_USER_ID):
        await event.answer("❌ شما دسترسی ندارید.", alert=True)
        return
    
    try:
        data = event.data.decode('utf-8')
        
        # --- Main & Sub-Menus ---
        if data == 'main_menu': await menu.show_main_menu(event, db)
        elif data == 'menu_books': await books.show_books_menu(event, db)
        elif data == 'menu_content': await content.show_content_menu(event, db)
        elif data == 'menu_schedule': await schedule.show_schedule_menu(event, db)
        elif data == 'menu_stats': await stats.show_stats(event, db)
        elif data == 'menu_settings': await settings.show_settings_menu(event, db)

        # --- Books Management ---
        elif data.startswith('books_list_'):
            page = int(data.split('_')[-1])
            await books.show_books_list(event, db, page)
        elif data == 'books_scan':
            await books.scan_group_for_pdfs(event, db, bot)
        elif data == 'books_process':
            await books.show_process_book_list(event, db)
        elif data.startswith('books_process_list_'):
            page = int(data.split('_')[-1])
            await books.show_process_book_list(event, db, page)
        elif data.startswith('book_process_'):
            book_id = int(data.split('_')[-1])
            await books.process_existing_book(event, db, bot, book_id)
        elif data.startswith('book_view_'):
            book_id = int(data.split('_')[-1])
            await books.show_book_details(event, db, book_id)
        elif data.startswith('book_analyze_'):
            book_id = int(data.split('_')[-1])
            await books.analyze_book_content(event, db, bot, book_id)

        # --- Content Management ---
        elif data.startswith('content_pending_'):
            page = int(data.split('_')[-1])
            await content.show_pending_content(event, db, page)
        elif data.startswith('content_approved_'):
            page = int(data.split('_')[-1])
            await content.show_approved_content(event, db, page)
        elif data.startswith('content_published_'):
            page = int(data.split('_')[-1])
            await content.show_published_content(event, db, page)
        elif data.startswith('content_approve_'):
            content_id = int(data.split('_')[-1])
            await content.approve_content(event, db, content_id)
        elif data.startswith('content_reject_'):
            content_id = int(data.split('_')[-1])
            await content.reject_content(event, db, content_id)
        elif data.startswith('content_publish_confirm_'):
            content_id = int(data.split('_')[-1])
            await content.publish_content_to_channel(event, db, bot, content_id)
        elif data.startswith('content_view_'):
            content_id = int(data.split('_')[-1])
            await content.show_content_for_approval(event, db, content_id)
        elif data == 'content_manual':
            await content.show_manual_content_form(event, db)
        elif data == 'content_ai_generate':
            await content.show_ai_content_generator(event, db, bot)
        elif data == 'ai_generate_quote':
            await content.generate_ai_content(event, db, bot, 'quote')
        elif data == 'ai_generate_description':
            await content.generate_ai_content(event, db, bot, 'description')
        elif data == 'ai_generate_summary':
            await content.generate_ai_content(event, db, bot, 'summary')

        # --- Schedule & Stats ---
        elif data == 'schedule_add': await schedule.show_add_schedule_form(event, db)
        elif data == 'schedule_list': await schedule.show_schedule_list(event, db)
        elif data == 'stats_refresh': await stats.show_stats(event, db)
        elif data == 'stats_full': await stats.show_full_stats(event, db)

        # --- Detailed Settings (DB Settings) ---
        elif data == 'settings_ai': await settings.show_ai_settings(event, db)
        elif data == 'settings_design': await settings.show_design_settings(event, db)
        elif data == 'settings_content': await settings.show_content_settings(event, db)
        elif data.startswith('set_edit_'):
            key = data.replace('set_edit_', '')
            label_map = {
                'ai_model': 'مدل AI', 'quote_count': 'تعداد نقل‌قول',
                'summary_length_min': 'حداقل خلاصه', 'summary_length_max': 'حداکثر خلاصه',
                'design_template': 'قالب طراحی', 'font_size': 'اندازه فونت', 'bg_color': 'رنگ پس‌زمینه'
            }
            await settings.start_edit_setting(event, db, key, label_map.get(key, key))

        # --- Hashtags & Footer ---
        elif data == 'hashtags_menu': await hashtags.show_hashtags_menu(event, db)
        elif data == 'hashtag_add': await hashtags.show_add_hashtag_form(event, db)
        elif data == 'hashtag_list': await hashtags.show_hashtags_list(event, db, 1, 'all')
        elif data == 'hashtag_approved': await hashtags.show_hashtags_list(event, db, 1, 'approved')
        elif data == 'hashtag_pending': await hashtags.show_hashtags_list(event, db, 1, 'pending')
        elif data.startswith('hashtag_approve_'):
            await hashtags.approve_hashtag(event, db, int(data.split('_')[-1]))
        elif data.startswith('hashtag_delete_'):
            await hashtags.delete_hashtag(event, db, int(data.split('_')[-1]))

        elif data == 'footer_settings': await footer.show_footer_settings(event, db)
        elif data == 'footer_toggle_id': await footer.toggle_footer_id(event, db)
        elif data == 'footer_edit_format': await footer.show_edit_footer_format(event, db)
        elif data == 'footer_edit_custom': await footer.show_edit_footer_custom(event, db)

        # --- Env Settings (.env) ---
        elif data == 'env_settings': await env_settings.show_env_settings_menu(event, env_manager)
        elif data == 'env_telegram': await env_settings.show_env_category(event, env_manager, 'telegram')
        elif data == 'env_groups': await env_settings.show_env_category(event, env_manager, 'groups')
        elif data == 'env_openrouter': await env_settings.show_env_category(event, env_manager, 'openrouter')
        elif data == 'env_database': await env_settings.show_env_category(event, env_manager, 'database')
        elif data == 'env_other': await env_settings.show_env_category(event, env_manager, 'other')
        elif data == 'env_view_all': await env_settings.show_all_env_vars(event, env_manager)
        elif data.startswith('env_edit_'):
            await env_settings.start_edit_env_var(event, env_manager, data.replace('env_edit_', ''))
        
        elif data == 'noop': await event.answer()
        else: await event.answer("دستور نامعتبر است.", alert=True)

    except Exception as e:
        print(f"Callback error: {e}")
        await event.answer("خطا در پردازش درخواست.", alert=True)


@bot.on(events.NewMessage(pattern='/cancel'))
async def cancel_handler(event):
    """Handle /cancel to clear all states"""
    StateManager.clear_state(event.sender_id)
    if event.sender_id in env_settings.pending_edits: del env_settings.pending_edits[event.sender_id]
    if event.sender_id in footer.pending_footer_edits: del footer.pending_footer_edits[event.sender_id]
    await event.respond("❌ تمام عملیات‌های جاری لغو شد.")


@bot.on(events.NewMessage(func=lambda e: e.is_private and not e.message.text.startswith('/')))
async def global_input_handler(event):
    """Smart input handler for all states and content"""
    user_id = event.sender_id
    if not is_admin(user_id, ADMIN_USER_ID): return

    # 0. Check if PDF file - highest priority for file handling
    if event.message.media:
        # Check if it's a PDF file
        if hasattr(event.message.media, 'document'):
            doc = event.message.media.document
            if hasattr(doc, 'mime_type') and doc.mime_type == 'application/pdf':
                # It's a PDF - handle as book
                await books.process_new_pdf(event, db, bot)
                return

    # 1. State-based Input (Highest Priority)
    if StateManager.is_waiting(user_id, 'EDIT_SETTING'):
        if await settings.handle_setting_input(event, db): return
        
    if user_id in env_settings.pending_edits:
        if await env_settings.handle_env_var_input(event, env_manager, bot): return
        
    if user_id in footer.pending_footer_edits:
        if await footer.handle_footer_input(event, db): return

    # 2. Specific Functional Input
    if event.message.text and event.message.text.startswith('#'):
        if await hashtags.handle_hashtag_input(event, db): return
        
    # 3. Default: Handle as Content (Photos, Videos, or plain text)
    await content.handle_content_submission(event, db, bot)




async def main():
    """Start the bot"""
    validate_config()
    print("🤖 Bot is starting...")
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ Bot is online!")
    await bot.run_until_disconnected()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Stopped.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
