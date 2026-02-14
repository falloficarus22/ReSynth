"""
Web interface for ReSynth package
"""

def main():
    """Main web interface entry point"""
    try:
        import streamlit as st
        from ..app import main as app_main
        app_main()
    except ImportError:
        print("❌ Streamlit not installed. Install with: pip install streamlit")
        return

if __name__ == '__main__':
    main()
