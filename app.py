import os
import sys
import runpy

# Add project root to system path
current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add backend directory to system path
backend_dir = os.path.join(current_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Set path for ui/main.py
main_script_path = os.path.join(current_dir, "ui", "main.py")

# Run the application
if os.path.exists(main_script_path):
    sys.argv[0] = main_script_path
    runpy.run_path(main_script_path, run_name="__main__")
else:
    import streamlit as st
    st.error(f"Required file not found: {main_script_path}")
  
