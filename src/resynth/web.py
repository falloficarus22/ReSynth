"""
Web interface for ReSynth package
"""

def main():
    """Main web interface entry point"""
    try:
        import streamlit as st
        import sys
        import os
        
        # Add the project root to Python path for imports
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, project_root)
        
        from app import main as app_main
        app_main()
    except ImportError:
        print("❌ Streamlit not installed. Install with: pip install streamlit")
        return

if __name__ == '__main__':
    main()
