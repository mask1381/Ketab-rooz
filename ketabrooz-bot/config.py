"""
Configuration management for KetabeRooz bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_int_list(env_var, default='0'):
    """Helper to parse a list of integers from environment variable"""
    value = os.getenv(env_var, default)
    if not value:
        return []
    return [int(x.strip()) for x in value.split(',') if x.strip().isdigit()]

# Telegram Configuration
# API_ID should be a single integer from my.telegram.org
raw_api_id = os.getenv('API_ID', '0').split(',')[0].strip()
API_ID = int(raw_api_id) if raw_api_id.isdigit() else 0
API_HASH = os.getenv('API_HASH', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
USERBOT_SESSION = os.getenv('USERBOT_SESSION', '')
USER_PHONE = os.getenv('USER_PHONE', '')

# Groups & Channels
SOURCE_GROUP_ID = int(os.getenv('SOURCE_GROUP_ID', '0'))
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID', '0'))

# Support for multiple Admin IDs
ADMIN_USER_IDS = get_int_list('ADMIN_USER_ID', '0')
# For backward compatibility with code using single ADMIN_USER_ID
ADMIN_USER_ID = ADMIN_USER_IDS[0] if ADMIN_USER_IDS else 0

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'google/gemini-2.5-flash:free')

# Database Configuration
DB_PATH = os.getenv('DB_PATH', 'database/ketabrooz.db')

# Settings
TIMEZONE = os.getenv('TIMEZONE', 'Asia/Tehran')

# Validate required configuration
def validate_config():
    """Validate that all required configuration is present"""
    required = {
        'API_ID': API_ID,
        'API_HASH': API_HASH,
        'BOT_TOKEN': BOT_TOKEN,
        'SOURCE_GROUP_ID': SOURCE_GROUP_ID,
        'TARGET_CHANNEL_ID': TARGET_CHANNEL_ID,
        'ADMIN_USER_ID': ADMIN_USER_ID,
        'OPENROUTER_API_KEY': OPENROUTER_API_KEY,
    }
    
    missing = [key for key, value in required.items() if not value]
    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")
    
    return True
