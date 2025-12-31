"""
Quick launcher for GUI setup tool
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from setup_env_gui import main
    main()
except ImportError as e:
    print(f"Error: {e}")
    print("\nMake sure you're running from the ketabrooz-bot directory")
    sys.exit(1)
except Exception as e:
    print(f"Error starting GUI: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


