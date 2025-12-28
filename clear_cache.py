"""
Clear Python cache and restart
"""
import os
import shutil

# Remove __pycache__ directories
for root, dirs, files in os.walk('.'):
    if '__pycache__' in dirs:
        cache_dir = os.path.join(root, '__pycache__')
        print(f"Removing {cache_dir}")
        shutil.rmtree(cache_dir)

print("\n✓ Cache cleared!")
print("\nNow restart the application:")
print("python main.py")
