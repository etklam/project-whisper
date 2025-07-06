import os
import logging

def clean_directory(directory, keep_extensions=None):
    """Clean files in directory not matching specified extensions
    
    Args:
        directory (str): Path to the directory to clean
        keep_extensions (list): List of file extensions to keep (e.g., ['.md'])
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("cleaner")
    
    # Ensure directory exists
    if not os.path.exists(directory):
        logger.error(f"Directory does not exist: {directory}")
        return False
    
    # Default to keeping .md files
    if keep_extensions is None:
        keep_extensions = ['.md']
    
    try:
        # Iterate over all files in directory
        files_deleted = 0
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
            
            # Check if file extension should be kept
            _, ext = os.path.splitext(file)
            if ext.lower() in keep_extensions:
                logger.info(f"Keeping file: {file}")
                continue
            
            # Delete file
            try:
                os.remove(file_path)
                logger.info(f"Deleted: {file}")
                files_deleted += 1
                
                # 檢查是否為 urls.txt 並重建
                if file == 'urls.txt':
                    open(file_path, 'w').close()  # 建立空文件
                    logger.info(f"Recreated empty file: {file}")
            except Exception as e:
                logger.error(f"Failed to delete file {file}: {e}")
        
        logger.info(f"Cleaning complete: Deleted {files_deleted} files")
        return True
    except Exception as e:
        logger.error(f"Error cleaning directory: {e}")
        return False

# Test code
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python cleaner.py <directory> [keep_extensions]")
        sys.exit(1)
    
    dir_path = sys.argv[1]
    extensions = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    clean_directory(dir_path, extensions)