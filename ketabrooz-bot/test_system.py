"""
System diagnostic and testing tool for KetabeRooz bot
Checks if all files work together correctly
"""
import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple
import traceback

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class SystemChecker:
    """Comprehensive system checker"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []
        self.base_path = Path(__file__).parent
    
    def check(self) -> bool:
        """Run all checks"""
        print("🔍 شروع بررسی سیستم...\n")
        
        # Check file structure
        self.check_file_structure()
        
        # Check Python imports
        self.check_imports()
        
        # Check configuration
        self.check_configuration()
        
        # Check database
        self.check_database()
        
        # Check handlers
        self.check_handlers()
        
        # Check utilities
        self.check_utilities()
        
        # Check core modules
        self.check_core_modules()
        
        # Print results
        self.print_results()
        
        return len(self.errors) == 0
    
    def check_file_structure(self):
        """Check if all required files exist"""
        print("📁 بررسی ساختار فایل‌ها...")
        
        required_files = [
            'bot.py',
            'config.py',
            'requirements.txt',
            'database/__init__.py',
            'database/db.py',
            'database/schema.sql',
            'handlers/__init__.py',
            'handlers/menu.py',
            'handlers/books.py',
            'handlers/content.py',
            'handlers/schedule.py',
            'handlers/stats.py',
            'handlers/settings.py',
            'handlers/env_settings.py',
            'core/__init__.py',
            'core/pdf_processor.py',
            'core/ai_generator.py',
            'core/image_creator.py',
            'core/publisher.py',
            'utils/__init__.py',
            'utils/keyboards.py',
            'utils/helpers.py',
            'utils/storage.py',
            'utils/env_manager.py',
        ]
        
        for file_path in required_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                self.success.append(f"✅ {file_path}")
            else:
                self.errors.append(f"❌ فایل یافت نشد: {file_path}")
        
        # Check optional files
        optional_files = [
            '.env',
            '.env.example',
            'fonts/Vazir-Bold.ttf'
        ]
        
        for file_path in optional_files:
            full_path = self.base_path / file_path
            if not full_path.exists():
                self.warnings.append(f"⚠️ فایل اختیاری یافت نشد: {file_path}")
    
    def check_imports(self):
        """Check if all imports work"""
        print("\n📦 بررسی importها...")
        
        imports_to_check = [
            ('telethon', 'TelegramClient'),
            ('dotenv', 'load_dotenv'),
            ('sqlite3', None),
            ('PIL', 'Image'),
            ('arabic_reshaper', None),
            ('bidi', None),  # python-bidi
            ('aiohttp', None),
            ('fitz', None),  # PyMuPDF
        ]
        
        # Special check for bidi.algorithm
        try:
            from bidi.algorithm import get_display
            self.success.append("✅ bidi.algorithm")
        except ImportError:
            self.warnings.append("⚠️ bidi.algorithm قابل import نیست (python-bidi نصب نشده)")
        
        for module_name, attr in imports_to_check:
            try:
                mod = __import__(module_name)
                if attr:
                    getattr(mod, attr)
                self.success.append(f"✅ {module_name}")
            except ImportError as e:
                self.errors.append(f"❌ Import خطا: {module_name} - {str(e)}")
            except AttributeError as e:
                self.errors.append(f"❌ Attribute خطا: {module_name}.{attr} - {str(e)}")
            except Exception as e:
                self.warnings.append(f"⚠️ {module_name}: {str(e)}")
    
    def check_configuration(self):
        """Check configuration module"""
        print("\n⚙️ بررسی تنظیمات...")
        
        try:
            from config import (
                API_ID, API_HASH, BOT_TOKEN,
                SOURCE_GROUP_ID, STORAGE_GROUP_ID, TARGET_CHANNEL_ID, ADMIN_USER_ID,
                OPENROUTER_API_KEY, OPENROUTER_MODEL,
                DB_PATH, TIMEZONE
            )
            
            # Check if required values are set (not default empty values)
            config_checks = {
                'API_ID': API_ID != 0,
                'API_HASH': bool(API_HASH),
                'BOT_TOKEN': bool(BOT_TOKEN),
                'SOURCE_GROUP_ID': SOURCE_GROUP_ID != 0,
                'STORAGE_GROUP_ID': STORAGE_GROUP_ID != 0,
                'TARGET_CHANNEL_ID': TARGET_CHANNEL_ID != 0,
                'ADMIN_USER_ID': ADMIN_USER_ID != 0,
                'OPENROUTER_API_KEY': bool(OPENROUTER_API_KEY),
            }
            
            for key, is_set in config_checks.items():
                if is_set:
                    self.success.append(f"✅ {key} تنظیم شده")
                else:
                    self.warnings.append(f"⚠️ {key} تنظیم نشده (مقدار پیش‌فرض)")
            
            # Check model format
            if OPENROUTER_MODEL and 'gemini' in OPENROUTER_MODEL.lower():
                self.success.append(f"✅ مدل OpenRouter: {OPENROUTER_MODEL}")
            else:
                self.warnings.append(f"⚠️ مدل OpenRouter ممکن است نامعتبر باشد: {OPENROUTER_MODEL}")
            
        except Exception as e:
            self.errors.append(f"❌ خطا در بارگذاری config: {str(e)}")
            self.errors.append(traceback.format_exc())
    
    def check_database(self):
        """Check database module"""
        print("\n💾 بررسی دیتابیس...")
        
        try:
            from database.db import Database
            from config import DB_PATH
            
            # Try to initialize database
            db = Database(DB_PATH)
            self.success.append("✅ Database class قابل بارگذاری است")
            
            # Check if database file exists or can be created
            db_path = Path(DB_PATH)
            if db_path.exists():
                self.success.append(f"✅ فایل دیتابیس موجود است: {DB_PATH}")
            else:
                # Check if directory exists
                if db_path.parent.exists():
                    self.warnings.append(f"⚠️ فایل دیتابیس وجود ندارد (در اولین اجرا ایجاد می‌شود): {DB_PATH}")
                else:
                    self.errors.append(f"❌ دایرکتوری دیتابیس وجود ندارد: {db_path.parent}")
            
            # Try to get settings (tests database connection)
            try:
                settings = db.get_all_settings()
                self.success.append("✅ اتصال به دیتابیس موفق")
            except Exception as e:
                self.errors.append(f"❌ خطا در اتصال به دیتابیس: {str(e)}")
            
        except Exception as e:
            self.errors.append(f"❌ خطا در بارگذاری database: {str(e)}")
            self.errors.append(traceback.format_exc())
    
    def check_handlers(self):
        """Check handler modules"""
        print("\n📝 بررسی handlerها...")
        
        handlers = [
            'handlers.menu',
            'handlers.books',
            'handlers.content',
            'handlers.schedule',
            'handlers.stats',
            'handlers.settings',
            'handlers.env_settings',
        ]
        
        for handler_name in handlers:
            try:
                __import__(handler_name)
                self.success.append(f"✅ {handler_name}")
            except Exception as e:
                self.errors.append(f"❌ خطا در {handler_name}: {str(e)}")
    
    def check_utilities(self):
        """Check utility modules"""
        print("\n🛠️ بررسی ابزارها...")
        
        utilities = [
            'utils.keyboards',
            'utils.helpers',
            'utils.storage',
            'utils.env_manager',
        ]
        
        for util_name in utilities:
            try:
                mod = __import__(util_name)
                self.success.append(f"✅ {util_name}")
            except Exception as e:
                self.errors.append(f"❌ خطا در {util_name}: {str(e)}")
    
    def check_core_modules(self):
        """Check core modules"""
        print("\n🔧 بررسی ماژول‌های هسته...")
        
        core_modules = [
            ('core.pdf_processor', 'PDFProcessor'),
            ('core.ai_generator', 'AIGenerator'),
            ('core.image_creator', 'ImageCreator'),
            ('core.publisher', 'Publisher'),
        ]
        
        for module_name, class_name in core_modules:
            try:
                mod = __import__(module_name, fromlist=[class_name])
                cls = getattr(mod, class_name)
                self.success.append(f"✅ {module_name}.{class_name}")
            except Exception as e:
                self.errors.append(f"❌ خطا در {module_name}.{class_name}: {str(e)}")
    
    def print_results(self):
        """Print all results"""
        print("\n" + "="*60)
        print("📊 نتایج بررسی:")
        print("="*60)
        
        if self.success:
            print(f"\n✅ موفق ({len(self.success)}):")
            for msg in self.success[:20]:  # Show first 20
                print(f"  {msg}")
            if len(self.success) > 20:
                print(f"  ... و {len(self.success) - 20} مورد دیگر")
        
        if self.warnings:
            print(f"\n⚠️ هشدارها ({len(self.warnings)}):")
            for msg in self.warnings:
                print(f"  {msg}")
        
        if self.errors:
            print(f"\n❌ خطاها ({len(self.errors)}):")
            for msg in self.errors:
                print(f"  {msg}")
        
        print("\n" + "="*60)
        
        # Count critical vs non-critical errors
        critical_errors = [e for e in self.errors if 'Import' in e or 'خطا در بارگذاری' in e]
        non_critical_errors = [e for e in self.errors if e not in critical_errors]
        
        print(f"\n📈 خلاصه:")
        print(f"  ✅ موفق: {len(self.success)}")
        print(f"  ⚠️ هشدار: {len(self.warnings)}")
        print(f"  ❌ خطا: {len(self.errors)}")
        if critical_errors:
            print(f"    - خطاهای بحرانی: {len(critical_errors)}")
        if non_critical_errors:
            print(f"    - خطاهای غیربحرانی: {len(non_critical_errors)}")
        
        if critical_errors:
            print("\n❌ سیستم دارای خطاهای بحرانی است!")
            print("💡 راه حل:")
            print("  1. وابستگی‌ها را نصب کنید: pip install -r requirements.txt")
            print("  2. فایل .env را ایجاد و تنظیم کنید")
            print("  3. دوباره تست کنید: python test_system.py")
            return False
        elif self.errors:
            print("\n⚠️ سیستم دارای خطاهای غیربحرانی است.")
            print("سیستم ممکن است کار کند اما توصیه می‌شود خطاها را برطرف کنید.")
            return True
        elif self.warnings:
            print("\n⚠️ سیستم کار می‌کند اما هشدارهایی وجود دارد.")
            print("توصیه می‌شود هشدارها را بررسی کنید.")
            return True
        else:
            print("\n✅ همه چیز درست است! سیستم آماده استفاده است.")
            return True


def main():
    """Main function"""
    checker = SystemChecker()
    success = checker.check()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

