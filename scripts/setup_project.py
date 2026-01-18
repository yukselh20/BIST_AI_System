import os
import sys
from pathlib import Path

def create_structure():
    # Base directory is the current working directory
    base_dir = Path.cwd()
    
    # Define directories to create
    directories = [
        "data/raw_logs",
        "data/processed",
        "data/database",
        "models/lstm_price",
        "models/bert_sentiment",
        "models/checkpoints",
        "strategies/risk_management",
        "integration/matriks_bridge",
        "core",
    ]
    
    # Define files to create (path, content)
    files = [
        ("core/config.py", "# System settings\n\nBATCH_SIZE = 32\nDEVICE = 'cuda'\n"),
        ("core/logger.py", "# Logging infrastructure\nfrom loguru import logger\n\nlogger.add('data/raw_logs/system.log', rotation='500 MB')\n"),
        ("main.py", "# System entry point\nimport streamlit as st\nfrom core.logger import logger\n\ndef main():\n    st.title('BIST AI Tahmin Sistemi')\n    logger.info('System started')\n\nif __name__ == '__main__':\n    main()\n"),
    ]
    
    # Define directories that need __init__.py
    init_dirs = [
        "models",
        "models/lstm_price",
        "models/bert_sentiment",
        "strategies",
        "strategies/risk_management",
        "integration",
        "integration/matriks_bridge",
        "core",
    ]

    print(f"Initializing project structure in {base_dir}...")

    # Create directories
    for dir_path in directories:
        full_path = base_dir / dir_path
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {dir_path}")
        except Exception as e:
            print(f"Error creating {dir_path}: {e}")

    # Create __init__.py files
    for dir_path in init_dirs:
        init_file = base_dir / dir_path / "__init__.py"
        try:
            init_file.touch(exist_ok=True)
            print(f"Created __init__.py in: {dir_path}")
        except Exception as e:
            print(f"Error creating __init__.py in {dir_path}: {e}")

    # Create specific files
    for file_path, content in files:
        full_path = base_dir / file_path
        try:
            if not full_path.exists():
                full_path.write_text(content, encoding='utf-8')
                print(f"Created file: {file_path}")
            else:
                print(f"File already exists: {file_path}")
        except Exception as e:
            print(f"Error creating {file_path}: {e}")

    print("Project structure initialization complete!")

if __name__ == "__main__":
    create_structure()
