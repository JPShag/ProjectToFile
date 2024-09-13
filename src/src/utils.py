import schedule
import time
import os
import logging

def schedule_backup(backup_handler, interval='daily'):
    try:
        if interval == 'daily':
            schedule.every().day.at("02:00").do(backup_handler.run)
        elif interval == 'weekly':
            schedule.every().monday.at("02:00").do(backup_handler.run)
        elif interval == 'monthly':
            schedule.every().month.at("02:00").do(backup_handler.run)
    except Exception as e:
        logging.error(f"Error in scheduling backup: {e}", exc_info=True)

def run_scheduler():
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logging.error(f"Error in scheduler: {e}", exc_info=True)

def get_file_size(file_path):
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        logging.error(f"Error getting file size for {file_path}: {e}", exc_info=True)
        return 0

def format_size(size_in_bytes):
    try:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_in_bytes < 1024.0:
                return f"{size_in_bytes:.2f} {unit}"
            size_in_bytes /= 1024.0
        return f"{size_in_bytes:.2f} PB"
    except Exception as e:
        logging.error(f"Error formatting size: {e}", exc_info=True)
        return "Unknown size"

def generate_file_tree(root_dir):
    try:
        tree = {}
        for root, dirs, files in os.walk(root_dir):
            folder_tree = tree
            for part in root.split(os.sep):
                folder_tree = folder_tree.setdefault(part, {})
            for file in files:
                folder_tree[file] = None
        return tree
    except Exception as e:
        logging.error(f"Error generating file tree for {root_dir}: {e}", exc_info=True)
        return {}

def print_file_tree(tree, indent=0):
    try:
        for key, value in tree.items():
            print('  ' * indent + key)
            if isinstance(value, dict):
                print_file_tree(value, indent + 1)
    except Exception as e:
        logging.error(f"Error printing file tree: {e}", exc_info=True)
