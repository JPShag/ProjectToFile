import os

def get_file_size(file_path):
    """
    Get the size of a file in bytes.
    """
    return os.path.getsize(file_path)

def format_size(size_in_bytes):
    """
    Format file size in human-readable format.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"

def count_files_in_directory(directory, include_subdirs=True):
    """
    Count the number of files in a directory.
    """
    count = 0
    for root, dirs, files in os.walk(directory):
        if not include_subdirs and root != directory:
            continue
        count += len(files)
    return count

def get_total_size(paths, include_subdirs=True):
    """
    Get the total size of files and directories.
    """
    total_size = 0
    for path in paths:
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                if not include_subdirs and root != path:
                    continue
                total_size += sum(get_file_size(os.path.join(root, file)) for file in files)
        elif os.path.isfile(path):
            total_size += get_file_size(path)
    return total_size