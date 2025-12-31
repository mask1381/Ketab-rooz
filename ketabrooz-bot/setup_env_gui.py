"""
GUI Setup Tool for KetabeRooz Bot Environment Variables
A graphical interface to enter and save .env configuration
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
from pathlib import Path
from utils.env_manager import EnvManager


class EnvSetupGUI:
    """GUI for setting up environment variables"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("KetabeRooz Bot - تنظیمات .env")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Initialize env manager
        self.env_manager = EnvManager('.env')
        
        # Load existing values
        self.existing_vars = self.env_manager.get_all_vars()
        
        # Create UI
        self.create_widgets()
        
        # Load existing values into fields
        self.load_existing_values()
    
    def create_widgets(self):
        """Create GUI widgets"""
        
        # Main container with scroll
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="⚙️ تنظیمات KetabeRooz Bot",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        row = 1
        
        # Telegram Section
        self.create_section(main_frame, "📱 تنظیمات Telegram", row)
        row += 1
        
        self.api_id_var = self.create_field(main_frame, "API_ID:", row, 
                                           help_text="از my.telegram.org دریافت کنید")
        row += 1
        
        self.api_hash_var = self.create_field(main_frame, "API_HASH:", row,
                                            help_text="از my.telegram.org دریافت کنید",
                                            password=True)
        row += 1
        
        self.bot_token_var = self.create_field(main_frame, "BOT_TOKEN:", row,
                                              help_text="از @BotFather دریافت کنید",
                                              password=True)
        row += 1
        
        # Groups & Channels Section
        self.create_section(main_frame, "👥 گروه‌ها و کانال‌ها", row)
        row += 1
        
        self.source_group_var = self.create_field(main_frame, "SOURCE_GROUP_ID:", row,
                                                  help_text="ID گروهی که PDFها در آن آپلود می‌شوند (با - شروع می‌شود)")
        row += 1
        
        self.storage_group_var = self.create_field(main_frame, "STORAGE_GROUP_ID:", row,
                                                   help_text="ID گروه ذخیره‌سازی داخلی (با - شروع می‌شود)")
        row += 1
        
        self.target_channel_var = self.create_field(main_frame, "TARGET_CHANNEL_ID:", row,
                                                    help_text="ID کانال عمومی برای انتشار (با - شروع می‌شود)")
        row += 1
        
        self.admin_user_var = self.create_field(main_frame, "ADMIN_USER_ID:", row,
                                               help_text="ID کاربری شما (عدد مثبت)")
        row += 1
        
        # OpenRouter Section
        self.create_section(main_frame, "🤖 تنظیمات OpenRouter", row)
        row += 1
        
        self.openrouter_key_var = self.create_field(main_frame, "OPENROUTER_API_KEY:", row,
                                                    help_text="از openrouter.ai دریافت کنید",
                                                    password=True)
        row += 1
        
        self.openrouter_model_var = self.create_field(main_frame, "OPENROUTER_MODEL:", row,
                                                     help_text="مثال: google/gemini-2.5-flash:free")
        row += 1
        
        # Database & Settings Section
        self.create_section(main_frame, "💾 تنظیمات دیتابیس و سایر", row)
        row += 1
        
        self.db_path_var = self.create_field(main_frame, "DB_PATH:", row,
                                            help_text="مسیر فایل دیتابیس (پیش‌فرض: database/ketabrooz.db)")
        row += 1
        
        self.timezone_var = self.create_field(main_frame, "TIMEZONE:", row,
                                             help_text="منطقه زمانی (پیش‌فرض: Asia/Tehran)")
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        save_btn = ttk.Button(button_frame, text="💾 ذخیره تنظیمات", 
                             command=self.save_settings, width=20)
        save_btn.grid(row=0, column=0, padx=5)
        
        load_btn = ttk.Button(button_frame, text="📂 بارگذاری از فایل", 
                             command=self.load_from_file, width=20)
        load_btn.grid(row=0, column=1, padx=5)
        
        test_btn = ttk.Button(button_frame, text="✅ تست تنظیمات", 
                             command=self.test_settings, width=20)
        test_btn.grid(row=1, column=0, padx=5, pady=5)
        
        exit_btn = ttk.Button(button_frame, text="❌ خروج", 
                             command=self.root.quit, width=20)
        exit_btn.grid(row=1, column=1, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="آماده")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=row+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_section(self, parent, title, row):
        """Create a section header"""
        section_label = ttk.Label(
            parent, 
            text=title,
            font=("Arial", 12, "bold"),
            foreground="blue"
        )
        section_label.grid(row=row, column=0, columnspan=2, pady=(15, 5), sticky=tk.W)
    
    def create_field(self, parent, label, row, help_text="", password=False):
        """Create a labeled input field"""
        # Label
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        
        # Entry
        if password:
            var = tk.StringVar()
            entry = ttk.Entry(parent, textvariable=var, width=50, show="*")
        else:
            var = tk.StringVar()
            entry = ttk.Entry(parent, textvariable=var, width=50)
        
        entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Help text
        if help_text:
            help_label = ttk.Label(
                parent, 
                text=f"💡 {help_text}",
                font=("Arial", 8),
                foreground="gray"
            )
            help_label.grid(row=row+1, column=1, sticky=tk.W, padx=(0, 0), pady=(0, 5))
        
        return var
    
    def load_existing_values(self):
        """Load existing .env values into fields"""
        if self.existing_vars:
            self.api_id_var.set(self.existing_vars.get('API_ID', ''))
            self.api_hash_var.set(self.existing_vars.get('API_HASH', ''))
            self.bot_token_var.set(self.existing_vars.get('BOT_TOKEN', ''))
            self.source_group_var.set(self.existing_vars.get('SOURCE_GROUP_ID', ''))
            self.storage_group_var.set(self.existing_vars.get('STORAGE_GROUP_ID', ''))
            self.target_channel_var.set(self.existing_vars.get('TARGET_CHANNEL_ID', ''))
            self.admin_user_var.set(self.existing_vars.get('ADMIN_USER_ID', ''))
            self.openrouter_key_var.set(self.existing_vars.get('OPENROUTER_API_KEY', ''))
            self.openrouter_model_var.set(self.existing_vars.get('OPENROUTER_MODEL', 'google/gemini-2.5-flash:free'))
            self.db_path_var.set(self.existing_vars.get('DB_PATH', 'database/ketabrooz.db'))
            self.timezone_var.set(self.existing_vars.get('TIMEZONE', 'Asia/Tehran'))
            self.status_var.set("مقادیر موجود بارگذاری شد")
    
    def validate_settings(self):
        """Validate all settings"""
        errors = []
        
        # Check required fields
        if not self.api_id_var.get().strip():
            errors.append("API_ID الزامی است")
        elif not self.api_id_var.get().strip().isdigit():
            errors.append("API_ID باید عدد باشد")
        
        if not self.api_hash_var.get().strip():
            errors.append("API_HASH الزامی است")
        
        if not self.bot_token_var.get().strip():
            errors.append("BOT_TOKEN الزامی است")
        
        if not self.source_group_var.get().strip():
            errors.append("SOURCE_GROUP_ID الزامی است")
        elif not self.source_group_var.get().strip().lstrip('-').isdigit():
            errors.append("SOURCE_GROUP_ID باید عدد باشد (می‌تواند با - شروع شود)")
        
        if not self.storage_group_var.get().strip():
            errors.append("STORAGE_GROUP_ID الزامی است")
        elif not self.storage_group_var.get().strip().lstrip('-').isdigit():
            errors.append("STORAGE_GROUP_ID باید عدد باشد (می‌تواند با - شروع شود)")
        
        if not self.target_channel_var.get().strip():
            errors.append("TARGET_CHANNEL_ID الزامی است")
        elif not self.target_channel_var.get().strip().lstrip('-').isdigit():
            errors.append("TARGET_CHANNEL_ID باید عدد باشد (می‌تواند با - شروع شود)")
        
        if not self.admin_user_var.get().strip():
            errors.append("ADMIN_USER_ID الزامی است")
        elif not self.admin_user_var.get().strip().isdigit():
            errors.append("ADMIN_USER_ID باید عدد مثبت باشد")
        
        if not self.openrouter_key_var.get().strip():
            errors.append("OPENROUTER_API_KEY الزامی است")
        
        if not self.openrouter_model_var.get().strip():
            errors.append("OPENROUTER_MODEL الزامی است")
        elif 'gemini' not in self.openrouter_model_var.get().lower():
            errors.append("OPENROUTER_MODEL باید شامل 'gemini' باشد")
        
        if not self.db_path_var.get().strip():
            errors.append("DB_PATH الزامی است")
        
        return errors
    
    def save_settings(self):
        """Save settings to .env file"""
        errors = self.validate_settings()
        
        if errors:
            messagebox.showerror(
                "خطا در اعتبارسنجی",
                "لطفا خطاهای زیر را برطرف کنید:\n\n" + "\n".join(f"• {e}" for e in errors)
            )
            return
        
        try:
            # Save all variables
            self.env_manager.set_var('API_ID', self.api_id_var.get().strip(), 'Telegram API ID')
            self.env_manager.set_var('API_HASH', self.api_hash_var.get().strip(), 'Telegram API Hash')
            self.env_manager.set_var('BOT_TOKEN', self.bot_token_var.get().strip(), 'Telegram Bot Token')
            self.env_manager.set_var('SOURCE_GROUP_ID', self.source_group_var.get().strip(), 'Source Group ID')
            self.env_manager.set_var('STORAGE_GROUP_ID', self.storage_group_var.get().strip(), 'Storage Group ID')
            self.env_manager.set_var('TARGET_CHANNEL_ID', self.target_channel_var.get().strip(), 'Target Channel ID')
            self.env_manager.set_var('ADMIN_USER_ID', self.admin_user_var.get().strip(), 'Admin User ID')
            self.env_manager.set_var('OPENROUTER_API_KEY', self.openrouter_key_var.get().strip(), 'OpenRouter API Key')
            self.env_manager.set_var('OPENROUTER_MODEL', self.openrouter_model_var.get().strip(), 'OpenRouter Model')
            self.env_manager.set_var('DB_PATH', self.db_path_var.get().strip() or 'database/ketabrooz.db', 'Database Path')
            self.env_manager.set_var('TIMEZONE', self.timezone_var.get().strip() or 'Asia/Tehran', 'Timezone')
            
            self.status_var.set("✅ تنظیمات با موفقیت ذخیره شد!")
            messagebox.showinfo("موفق", "تنظیمات با موفقیت در فایل .env ذخیره شد!")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره تنظیمات:\n{str(e)}")
            self.status_var.set(f"❌ خطا: {str(e)}")
    
    def load_from_file(self):
        """Load settings from existing .env file"""
        try:
            self.existing_vars = self.env_manager.get_all_vars()
            self.load_existing_values()
            messagebox.showinfo("موفق", "تنظیمات از فایل .env بارگذاری شد!")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری:\n{str(e)}")
    
    def test_settings(self):
        """Test if settings are valid"""
        errors = self.validate_settings()
        
        if errors:
            messagebox.showerror(
                "خطا در تنظیمات",
                "لطفا خطاهای زیر را برطرف کنید:\n\n" + "\n".join(f"• {e}" for e in errors)
            )
        else:
            # Try to import config
            try:
                # Reload environment
                from dotenv import load_dotenv
                load_dotenv('.env', override=True)
                
                # Try to import config
                import importlib
                import config
                importlib.reload(config)
                
                messagebox.showinfo("موفق", "✅ همه تنظیمات معتبر هستند!\n\nربات آماده راه‌اندازی است.")
                self.status_var.set("✅ همه تنظیمات معتبر هستند")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در تست تنظیمات:\n{str(e)}")
                self.status_var.set(f"❌ خطا در تست: {str(e)}")


def main():
    """Main function"""
    root = tk.Tk()
    app = EnvSetupGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()


