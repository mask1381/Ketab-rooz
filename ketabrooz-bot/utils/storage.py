"""
Telegram storage manager for file storage in groups
"""
from typing import Optional, Tuple, Union
from telethon import TelegramClient
from telethon.tl.types import Message


class TelegramStorage:
    """Manages file storage in Telegram groups"""
    
    def __init__(self, bot: TelegramClient, storage_group_id: int):
        self.bot = bot
        self.storage_group_id = storage_group_id
    
    async def save_file(self, file_data: Union[bytes, str], caption: str = "",
                       file_type: str = 'photo') -> Tuple[str, int]:
        """
        Upload file to storage group and return (file_id, message_id)
        
        Args:
            file_data: File data (bytes) or file path (str) or file_id
            caption: Caption for the file
            file_type: 'photo', 'document', 'video', or 'audio'
        
        Returns:
            Tuple of (file_id, message_id)
        """
        try:
            if file_type == 'photo':
                msg = await self.bot.send_file(
                    self.storage_group_id,
                    file_data,
                    caption=caption
                )
            elif file_type == 'document':
                msg = await self.bot.send_file(
                    self.storage_group_id,
                    file_data,
                    caption=caption,
                    force_document=True
                )
            elif file_type == 'video':
                msg = await self.bot.send_file(
                    self.storage_group_id,
                    file_data,
                    caption=caption,
                    video_note=False
                )
            elif file_type == 'audio':
                msg = await self.bot.send_file(
                    self.storage_group_id,
                    file_data,
                    caption=caption,
                    voice_note=False
                )
            else:
                # Default to document
                msg = await self.bot.send_file(
                    self.storage_group_id,
                    file_data,
                    caption=caption,
                    force_document=True
                )
            
            # Get file_id from message
            if msg.media:
                if hasattr(msg.media, 'photo'):
                    file_id = msg.media.photo.id
                elif hasattr(msg.media, 'document'):
                    file_id = msg.media.document.id
                else:
                    file_id = str(msg.id)  # Fallback
            else:
                file_id = str(msg.id)
            
            return str(file_id), msg.id
            
        except Exception as e:
            raise Exception(f"Failed to save file to storage: {str(e)}")
    
    async def get_file(self, file_id: str):
        """
        Get file from storage using file_id
        Returns file_id which can be used directly in send_file
        """
        return file_id
    
    async def delete_file(self, message_id: int) -> bool:
        """
        Delete file from storage group
        
        Args:
            message_id: Message ID in storage group
        
        Returns:
            True if successful
        """
        try:
            await self.bot.delete_messages(self.storage_group_id, message_id)
            return True
        except Exception as e:
            print(f"Failed to delete file: {str(e)}")
            return False
    
    async def get_file_info(self, message_id: int) -> Optional[dict]:
        """
        Get file information from storage group
        
        Args:
            message_id: Message ID in storage group
        
        Returns:
            Dictionary with file info or None
        """
        try:
            messages = await self.bot.get_messages(self.storage_group_id, ids=message_id)
            if messages and messages.media:
                msg = messages if not isinstance(messages, list) else messages[0]
                if msg.media:
                    if hasattr(msg.media, 'photo'):
                        return {
                            'file_id': msg.media.photo.id,
                            'type': 'photo',
                            'caption': msg.message
                        }
                    elif hasattr(msg.media, 'document'):
                        doc = msg.media.document
                        return {
                            'file_id': doc.id,
                            'type': 'document',
                            'mime_type': doc.mime_type,
                            'size': doc.size,
                            'caption': msg.message
                        }
            return None
        except Exception as e:
            print(f"Failed to get file info: {str(e)}")
            return None

