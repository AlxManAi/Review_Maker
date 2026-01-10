import zipfile
import os
import datetime

def make_backup():
    source_dir = r"c:\review_generator"
    # Create backups folder
    backup_folder = os.path.join(source_dir, "backups")
    os.makedirs(backup_folder, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    backup_name = f"review_generator_backup_{timestamp}.zip"
    destination_zip = os.path.join(backup_folder, backup_name)

    print(f"Creating backup: {destination_zip}")
    
    # Explicit list of what to backup (SAFE and FAST)
    includes = [
        "core",
        "ui", 
        "styles",
        "config",
        "assets",
        "logs",
        "database",
        "review_generator.db",
        "main.py",
        "requirements.txt",
        "README.md",
        ".env",
        "create_backup.py",
        "create_icon.py",
        "column_widths.json"
    ]
    
    try:
        with zipfile.ZipFile(destination_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for item in includes:
                item_path = os.path.join(source_dir, item)
                
                if not os.path.exists(item_path):
                    continue
                    
                if os.path.isfile(item_path):
                    # Add file
                    print(f"Adding file: {item}")
                    zipf.write(item_path, item)
                elif os.path.isdir(item_path):
                    # Add directory recursively
                    print(f"Adding folder: {item}")
                    for root, dirs, files in os.walk(item_path):
                        # Filter out pycache
                        dirs[:] = [d for d in dirs if d != "__pycache__"]
                        
                        for file in files:
                            if file.endswith(".pyc") or file.endswith(".pyo"):
                                continue
                            
                            file_full_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_full_path, start=source_dir)
                            zipf.write(file_full_path, arcname)

        print(f"SUCCESS: Backup created at {destination_zip}")
        print(f"Size: {os.path.getsize(destination_zip) / 1024:.2f} KB")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    make_backup()
