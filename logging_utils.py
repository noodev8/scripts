#!/usr/bin/env python3
"""
Shared logging utilities for all scripts
Provides consistent log management across the codebase
"""

import os
import shutil
from datetime import datetime, timedelta

# --- LOGGING CONFIGURATION ---
LOG_ARCHIVE_DAYS = 3  # Keep 3 days of archived logs

def setup_logging_directories():
    """Create logs and archive_logs directories if they don't exist"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "logs")
    archive_dir = os.path.join(script_dir, "archive_logs")
    
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)
    
    return logs_dir, archive_dir

def manage_log_files(script_name):
    """Manage log files: archive current log and cleanup old archives"""
    logs_dir, archive_dir = setup_logging_directories()
    
    current_log = os.path.join(logs_dir, f"{script_name}.log")
    date_str = datetime.now().strftime("%Y-%m-%d")
    archived_log = os.path.join(archive_dir, f"{script_name}_{date_str}.log")
    
    # Archive current log if it exists and is from a previous day
    if os.path.exists(current_log):
        # Check if log is from today by looking at modification time
        log_mtime = datetime.fromtimestamp(os.path.getmtime(current_log))
        if log_mtime.date() < datetime.now().date():
            # Archive the previous day's log
            prev_date = log_mtime.strftime("%Y-%m-%d")
            prev_archived_log = os.path.join(archive_dir, f"{script_name}_{prev_date}.log")
            if not os.path.exists(prev_archived_log):
                shutil.copy2(current_log, prev_archived_log)
            # Clear the current log for today
            open(current_log, 'w').close()
    
    # Cleanup old archived logs (keep only LOG_ARCHIVE_DAYS)
    cutoff_date = datetime.now().date() - timedelta(days=LOG_ARCHIVE_DAYS)
    
    for filename in os.listdir(archive_dir):
        if filename.startswith(f"{script_name}_") and filename.endswith(".log"):
            try:
                # Extract date from filename
                date_part = filename.replace(f"{script_name}_", "").replace(".log", "")
                file_date = datetime.strptime(date_part, "%Y-%m-%d").date()
                
                if file_date < cutoff_date:
                    old_log_path = os.path.join(archive_dir, filename)
                    os.remove(old_log_path)
                    print(f"Removed old log: {filename}")
            except (ValueError, OSError):
                # Skip files that don't match expected format or can't be removed
                continue

def create_logger(script_name):
    """Create a logger function for a specific script"""
    def log(message):
        """Log message to current log file and archive copy"""
        logs_dir, archive_dir = setup_logging_directories()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp}  {message}\n"
        
        # Write to current log
        current_log = os.path.join(logs_dir, f"{script_name}.log")
        with open(current_log, "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        # Also write to today's archive (allows for duplicate during the day)
        date_str = datetime.now().strftime("%Y-%m-%d")
        archived_log = os.path.join(archive_dir, f"{script_name}_{date_str}.log")
        with open(archived_log, "a", encoding="utf-8") as f:
            f.write(log_entry)
    
    return log

def save_report_file(filename, content):
    """Save a report file to the logs directory"""
    logs_dir, _ = setup_logging_directories()
    file_path = os.path.join(logs_dir, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return file_path

def get_logs_directory():
    """Get the logs directory path"""
    logs_dir, _ = setup_logging_directories()
    return logs_dir

def get_archive_directory():
    """Get the archive logs directory path"""
    _, archive_dir = setup_logging_directories()
    return archive_dir

# Example usage:
if __name__ == "__main__":
    # Test the logging system
    script_name = "test_script"
    
    # Setup logging
    manage_log_files(script_name)
    log = create_logger(script_name)
    
    # Test logging
    log("=== TEST SCRIPT STARTED ===")
    log("This is a test message")
    log("=== TEST SCRIPT COMPLETED ===")
    
    print(f"Test logs written to logs/{script_name}.log")
    print(f"Archive logs in archive_logs/{script_name}_*.log")
