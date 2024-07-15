import schedule
import time

def schedule_backup(backup_handler, interval='daily'):
    if interval == 'daily':
        schedule.every().day.at("02:00").do(backup_handler.run)
    elif interval == 'weekly':
        schedule.every().monday.at("02:00").do(backup_handler.run)
    elif interval == 'monthly':
        schedule.every().month.at("02:00").do(backup_handler.run)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def get_file_size(file_path):
    return os.path.getsize(file_path)

def format_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"

def generate_file_tree(root_dir):
    tree = {}
    for root, dirs, files in os.walk(root_dir):
        folder_tree = tree
        for part in root.split(os.sep):
            folder_tree = folder_tree.setdefault(part, {})
        for file in files:
            folder_tree[file] = None
    return tree

def print_file_tree(tree, indent=0):
    for key, value in tree.items():
        print('  ' * indent + key)
        if isinstance(value, dict):
            print_file_tree(value, indent + 1)
