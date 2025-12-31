"""
Environment variables manager for .env file
"""
import os
import re
from typing import Dict, Optional, List
from pathlib import Path


class EnvManager:
    """Manages .env file operations"""
    
    def __init__(self, env_path: str = '.env'):
        self.env_path = Path(env_path)
        self._ensure_env_file()
    
    def _ensure_env_file(self):
        """Create .env file if it doesn't exist"""
        if not self.env_path.exists():
            self.env_path.touch()
    
    def get_all_vars(self) -> Dict[str, str]:
        """Get all environment variables from .env file"""
        vars_dict = {}
        
        if not self.env_path.exists():
            return vars_dict
        
        with open(self.env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    vars_dict[key] = value
        
        return vars_dict
    
    def get_var(self, key: str) -> Optional[str]:
        """Get a specific environment variable"""
        vars_dict = self.get_all_vars()
        return vars_dict.get(key)
    
    def set_var(self, key: str, value: str, comment: Optional[str] = None):
        """Set or update an environment variable"""
        vars_dict = self.get_all_vars()
        vars_dict[key] = value
        
        # Read all lines to preserve comments and structure
        lines = []
        if self.env_path.exists():
            with open(self.env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        # Create new content
        new_lines = []
        found = False
        key_pattern = re.compile(rf'^{re.escape(key)}\s*=')
        
        for line in lines:
            stripped = line.strip()
            # If this is the key we're updating
            if key_pattern.match(stripped):
                # Add comment if provided
                if comment:
                    new_lines.append(f"# {comment}\n")
                # Escape value if it contains spaces or special chars
                if ' ' in value or any(char in value for char in ['#', '=', '$']):
                    new_lines.append(f'{key}="{value}"\n')
                else:
                    new_lines.append(f'{key}={value}\n')
                found = True
            # Skip old value line if we already added it
            elif not found or not stripped.startswith(key):
                new_lines.append(line)
        
        # If key wasn't found, add it
        if not found:
            if comment:
                new_lines.append(f"# {comment}\n")
            if ' ' in value or any(char in value for char in ['#', '=', '$']):
                new_lines.append(f'{key}="{value}"\n')
            else:
                new_lines.append(f'{key}={value}\n')
        
        # Write back to file
        with open(self.env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    
    def delete_var(self, key: str):
        """Delete an environment variable"""
        if not self.env_path.exists():
            return
        
        lines = []
        with open(self.env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        key_pattern = re.compile(rf'^{re.escape(key)}\s*=')
        new_lines = [line for line in lines if not key_pattern.match(line.strip())]
        
        with open(self.env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    
    def get_env_categories(self) -> Dict[str, List[str]]:
        """Get environment variables grouped by category"""
        all_vars = self.get_all_vars()
        
        categories = {
            'Telegram': ['API_ID', 'API_HASH', 'BOT_TOKEN'],
            'Groups & Channels': ['SOURCE_GROUP_ID', 'TARGET_CHANNEL_ID', 'ADMIN_USER_ID'],
            'OpenRouter': ['OPENROUTER_API_KEY', 'OPENROUTER_MODEL'],
            'Database': ['DB_PATH'],
            'Settings': ['TIMEZONE']
        }
        
        result = {}
        for category, keys in categories.items():
            result[category] = {key: all_vars.get(key, '') for key in keys}
        
        return result
    
    def mask_sensitive_value(self, value: str, show_chars: int = 4) -> str:
        """Mask sensitive values for display"""
        if not value:
            return '(خالی)'
        if len(value) <= show_chars * 2:
            return '*' * len(value)
        return value[:show_chars] + '*' * (len(value) - show_chars * 2) + value[-show_chars:]


