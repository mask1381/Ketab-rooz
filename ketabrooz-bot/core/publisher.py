"""
Publisher for sending content to target channel
"""
from telethon import TelegramClient
from typing import Optional, List
from datetime import datetime
from database.db import Database
from handlers.footer import format_footer
from handlers.footer import format_footer
from config import ADMIN_USER_ID
from utils.watermark import add_watermark_image, add_watermark_video
import os
import io


class Publisher:
    """Publisher for content to target channel"""
    
    def __init__(self, bot: TelegramClient, target_channel_id: int, db: Database):
        self.bot = bot
        self.target_channel_id = target_channel_id
        self.db = db
    
    async def publish_content(self, content_id: int) -> Optional[int]:
        """
        Publish content to target channel
        """
        try:
            content = self.db.get_content(content_id)
            if not content:
                raise Exception("Content not found")
            
            if content['status'] != 'approved':
                raise Exception(f"Content status is {content['status']}, must be 'approved'")
            
            # Get data
            file_id = content.get('file_id')
            source_msg_id = content.get('message_id')
            content_type = content.get('type', 'text')
            
            # Format message text (hashtags and footer)
            # Priorities: text field -> caption field -> empty
            original_text = content.get('text') or content.get('caption') or ''
            
            # Get hashtags
            hashtags = self._get_hashtags_for_content(content_type)
            message_text = original_text
            
            if hashtags:
                hashtag_text = ' '.join([f'#{tag}' for tag in hashtags])
                if message_text:
                    message_text += f'\n\n{hashtag_text}'
                else:
                    message_text = hashtag_text
            
            # Add footer
            footer_text = format_footer(content_id, content_type, self.db)
            if footer_text:
                if message_text:
                    message_text += f'\n\n{footer_text}'
                else:
                    message_text = footer_text
            
            msg = None
            
            # Check if we should use book cover
            use_cover = content.get('use_cover', False)
            book_id = content.get('book_id')
            
            # If use_cover is True, get cover from book
            if use_cover and book_id:
                try:
                    book = self.db.get_book(book_id)
                    if book and book.get('cover_file_id'):
                        file_id = book.get('cover_file_id')
                        # Change content_type to 'image' so it's sent as photo
                        content_type = 'image'
                except Exception as e:
                    print(f"Error getting book cover: {str(e)}")
            
            # 1. Handle media files (images, videos) or book covers
            if file_id or (content_type != 'text' and source_msg_id) or use_cover:
                file_to_send = None
                
                # Download media if needed for watermarking
                if content_type in ['image', 'video', 'cover'] or use_cover:
                    try:
                        # Determine source - priority: book cover -> file_id -> source_msg
                        media_source = None
                        if use_cover and book_id:
                            # Get cover from admin's chat
                            book = self.db.get_book(book_id)
                            if book and book.get('cover_message_id'):
                                try:
                                    cover_msg = await self.bot.get_messages(
                                        ADMIN_USER_ID,
                                        ids=book.get('cover_message_id')
                                    )
                                    if cover_msg and cover_msg.media:
                                        media_source = cover_msg.media
                                except Exception as e:
                                    print(f"Error getting cover from storage: {str(e)}")
                        
                        if not media_source and file_id:
                            media_source = file_id
                        
                        if not media_source and source_msg_id:
                            source_msg = await self.bot.get_messages(ADMIN_USER_ID, ids=source_msg_id)
                            if source_msg and source_msg.media:
                                media_source = source_msg.media
                        
                        if media_source:
                            # Download
                            path = await self.bot.download_media(media_source)
                            
                            if content_type == 'image' or content_type == 'cover':
                                with open(path, 'rb') as f:
                                    img_data = f.read()
                                
                                # Watermark
                                watermarked_data = add_watermark_image(img_data)
                                file_to_send = watermarked_data
                                
                                # Cleanup
                                os.remove(path)
                                
                            elif content_type == 'video':
                                # Watermark video (if ffmpeg exists)
                                watermarked_path = add_watermark_video(path)
                                file_to_send = watermarked_path
                                # Cleanup if different
                                if watermarked_path != path:
                                    # We will remove original, send watermarked
                                    # Note: send_file with path usually works
                                    pass
                                
                    except Exception as e:
                        print(f"Watermark failed, sending original: {e}")
                        # Fallback to original logic happens if file_to_send is None
                
                # Send
                if file_to_send:
                   msg = await self.bot.send_file(
                        self.target_channel_id,
                        file_to_send,
                        caption=message_text
                   )
                   # Clean up video file if it was a path
                   if isinstance(file_to_send, str) and os.path.exists(file_to_send):
                       try:
                           os.remove(file_to_send)
                           if content_type == 'video':
                               original_path = file_to_send.replace('_watermarked.mp4', '.mp4')
                               if os.path.exists(original_path): os.remove(original_path)
                       except: pass
                
                # Fallback to original method (no watermark or failed)
                elif file_id:
                    msg = await self.bot.send_file(
                        self.target_channel_id,
                        file_id,
                        caption=message_text
                    )
                elif source_msg_id:
                    source_msg = await self.bot.get_messages(ADMIN_USER_ID, ids=source_msg_id)
                    if source_msg and source_msg.media:
                        msg = await self.bot.send_file(
                            self.target_channel_id,
                            source_msg.media,
                            caption=message_text
                        )
                    else:
                        msg = await self.bot.send_message(self.target_channel_id, message_text)
            
            # 3. Handle pure text
            else:
                if message_text:
                    msg = await self.bot.send_message(
                        self.target_channel_id,
                        message_text
                    )
            
            if not msg:
                raise Exception("Failed to send message")

            # Update database
            self.db.update_content(
                content_id,
                status='published',
                published_date=datetime.now(),
                published_message_id=msg.id
            )
            
            return msg.id
        
        except Exception as e:
            print(f"Error publishing content: {str(e)}")
            return None
    
    def _get_hashtags_for_content(self, content_type: str) -> List[str]:
        """
        Get hashtags for content based on type
        """
        try:
            type_mapping = {
                'quote': 'quote',
                'description': 'general',
                'summary': 'general',
                'image': 'general',
                'video': 'general',
                'audio': 'general'
            }
            
            tag_type = type_mapping.get(content_type, 'general')
            hashtags = self.db.get_approved_hashtags_by_type(tag_type, count=5)
            
            if tag_type != 'general':
                general_tags = self.db.get_approved_hashtags_by_type('general', count=3)
                hashtags.extend(general_tags)
            
            return list(dict.fromkeys(hashtags))[:8]
        except Exception as e:
            print(f"Error getting hashtags: {str(e)}")
            return []
