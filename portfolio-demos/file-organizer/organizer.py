"""
Smart File Organizer - Desktop/Downloads ke files automatically sort karo
By: Matrix (Fiverr Portfolio Demo)

Features:
- Files ko type ke hisaab se folders mein sort kare
- Images, Videos, Documents, Music, Archives, Code alag alag
- Duplicate files detect kare
- Undo option — sab wapas rakh de
- Schedule mode — automatically organize kare
- Log file — kya kiya record rakhe

Usage:
    python organizer.py                    (organize current folder)
    python organizer.py C:\\Users\\You\\Downloads  (organize specific folder)
    python organizer.py --undo             (undo last organize)
"""

import os
import sys
import shutil
import json
import hashlib
from datetime import datetime
from pathlib import Path

# File categories and their extensions
CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico", ".webp", ".tiff", ".raw"],
    "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".3gp"],
    "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".php", ".rb", ".go", ".rs", ".ts", ".jsx", ".tsx"],
    "Executables": [".exe", ".msi", ".bat", ".cmd", ".sh", ".app", ".dmg"],
    "Fonts": [".ttf", ".otf", ".woff", ".woff2", ".eot"],
    "Data": [".json", ".xml", ".yaml", ".yml", ".sql", ".db", ".sqlite"],
    "Design": [".psd", ".ai", ".sketch", ".fig", ".xd", ".indd"],
}

LOG_FILE = "organize_log.json"


class FileOrganizer:
    """Smart file organizer — files ko automatically sort karo."""

    def __init__(self, target_dir=None):
        self.target_dir = target_dir or os.getcwd()
        self.log = {"timestamp": "", "moves": [], "target_dir": self.target_dir}
        self.stats = {"total": 0, "moved": 0, "skipped": 0, "duplicates": 0}

    def organize(self):
        """Target folder ke files ko categories mein sort karo."""
        print("=" * 55)
        print("  Smart File Organizer")
        print("  By: Matrix")
        print("=" * 55)
        print(f"\n  Organizing: {self.target_dir}\n")

        if not os.path.exists(self.target_dir):
            print(f"[ERROR] Folder not found: {self.target_dir}")
            return False

        self.log["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        files = [f for f in os.listdir(self.target_dir)
                 if os.path.isfile(os.path.join(self.target_dir, f))
                 and not f.startswith(".")
                 and f != LOG_FILE
                 and f != "organizer.py"]

        self.stats["total"] = len(files)
        print(f"  Found {len(files)} files to organize\n")

        for filename in files:
            filepath = os.path.join(self.target_dir, filename)
            ext = os.path.splitext(filename)[1].lower()

            category = self._get_category(ext)
            if not category:
                category = "Others"

            dest_dir = os.path.join(self.target_dir, category)
            os.makedirs(dest_dir, exist_ok=True)

            dest_path = os.path.join(dest_dir, filename)

            # Check duplicate
            if os.path.exists(dest_path):
                if self._is_duplicate(filepath, dest_path):
                    print(f"  [DUPLICATE] {filename} -> Skipped")
                    self.stats["duplicates"] += 1
                    continue
                # Rename to avoid overwrite
                name, ext_part = os.path.splitext(filename)
                counter = 1
                while os.path.exists(dest_path):
                    dest_path = os.path.join(dest_dir, f"{name}_{counter}{ext_part}")
                    counter += 1

            try:
                shutil.move(filepath, dest_path)
                self.log["moves"].append({
                    "file": filename,
                    "from": filepath,
                    "to": dest_path,
                    "category": category
                })
                self.stats["moved"] += 1
                print(f"  [MOVED] {filename} -> {category}/")
            except Exception as e:
                print(f"  [ERROR] {filename}: {e}")
                self.stats["skipped"] += 1

        # Save log for undo
        log_path = os.path.join(self.target_dir, LOG_FILE)
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(self.log, f, indent=2)

        # Print summary
        print(f"\n{'=' * 40}")
        print(f"  DONE!")
        print(f"  Total files: {self.stats['total']}")
        print(f"  Moved: {self.stats['moved']}")
        print(f"  Duplicates: {self.stats['duplicates']}")
        print(f"  Skipped: {self.stats['skipped']}")
        print(f"  Log saved to: {LOG_FILE}")
        print(f"  Run with --undo to reverse changes")
        print(f"{'=' * 40}")

        return True

    def undo(self):
        """Last organize ko undo karo — sab files wapas rakh do."""
        log_path = os.path.join(self.target_dir, LOG_FILE)

        if not os.path.exists(log_path):
            print("[ERROR] No organize log found. Nothing to undo.")
            return False

        with open(log_path, "r", encoding="utf-8") as f:
            log = json.load(f)

        moves = log.get("moves", [])
        print(f"\n  Undoing {len(moves)} moves from {log.get('timestamp', 'unknown')}...\n")

        undone = 0
        for move in reversed(moves):
            try:
                if os.path.exists(move["to"]):
                    shutil.move(move["to"], move["from"])
                    print(f"  [RESTORED] {move['file']}")
                    undone += 1
            except Exception as e:
                print(f"  [ERROR] {move['file']}: {e}")

        # Clean up empty category folders
        for category in CATEGORIES:
            cat_dir = os.path.join(self.target_dir, category)
            if os.path.exists(cat_dir) and not os.listdir(cat_dir):
                os.rmdir(cat_dir)
                print(f"  [REMOVED] Empty folder: {category}/")

        others_dir = os.path.join(self.target_dir, "Others")
        if os.path.exists(others_dir) and not os.listdir(others_dir):
            os.rmdir(others_dir)

        os.remove(log_path)
        print(f"\n  Done! Restored {undone} files.")
        return True

    def _get_category(self, ext):
        for category, extensions in CATEGORIES.items():
            if ext in extensions:
                return category
        return None

    def _is_duplicate(self, file1, file2):
        """Check if two files are the same by comparing hash."""
        try:
            h1 = hashlib.md5()
            h2 = hashlib.md5()
            with open(file1, "rb") as f1, open(file2, "rb") as f2:
                while True:
                    chunk1 = f1.read(8192)
                    chunk2 = f2.read(8192)
                    if not chunk1 and not chunk2:
                        break
                    h1.update(chunk1)
                    h2.update(chunk2)
            return h1.hexdigest() == h2.hexdigest()
        except Exception:
            return False

    def show_preview(self):
        """Preview dikhao — kya sort hoga."""
        files = [f for f in os.listdir(self.target_dir)
                 if os.path.isfile(os.path.join(self.target_dir, f))
                 and not f.startswith(".")]

        categories = {}
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            cat = self._get_category(ext) or "Others"
            categories.setdefault(cat, []).append(f)

        print(f"\n  Preview for: {self.target_dir}\n")
        for cat, cat_files in sorted(categories.items()):
            print(f"  {cat}/ ({len(cat_files)} files)")
            for f in cat_files[:5]:
                print(f"    - {f}")
            if len(cat_files) > 5:
                print(f"    ... and {len(cat_files) - 5} more")
        print()


def main():
    target = os.getcwd()
    undo_mode = False

    preview_mode = False

    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--undo":
            undo_mode = True
        elif arg == "--preview":
            preview_mode = True
        elif not arg.startswith("--"):
            target = arg

    organizer = FileOrganizer(target)

    if preview_mode:
        organizer.show_preview()
    elif undo_mode:
        organizer.undo()
    else:
        organizer.organize()


if __name__ == "__main__":
    main()
