"""
Quick dependency checker
Shows which packages need to be installed
"""
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

missing = []
installed = []

packages = [
    'telethon',
    'python-dotenv',
    'PIL',  # pillow
    'arabic_reshaper',
    'bidi',  # python-bidi
    'aiohttp',
    'fitz',  # pymupdf
]

print("Checking dependencies...\n")

for package in packages:
    try:
        if package == 'PIL':
            __import__('PIL')
            installed.append('pillow')
        elif package == 'fitz':
            __import__('fitz')
            installed.append('pymupdf')
        elif package == 'bidi':
            __import__('bidi')
            installed.append('python-bidi')
        else:
            __import__(package)
            installed.append(package)
    except ImportError:
        if package == 'PIL':
            missing.append('pillow')
        elif package == 'fitz':
            missing.append('pymupdf')
        elif package == 'bidi':
            missing.append('python-bidi')
        else:
            missing.append(package)

if installed:
    print("✅ Installed packages:")
    for pkg in installed:
        print(f"  - {pkg}")

if missing:
    print("\n❌ Missing packages:")
    for pkg in missing:
        print(f"  - {pkg}")
    print("\n💡 Install with: pip install -r requirements.txt")
else:
    print("\n✅ All dependencies are installed!")

sys.exit(0 if not missing else 1)

