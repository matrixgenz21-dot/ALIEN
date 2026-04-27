"""
Mini Devin - Project Builder
AI ke generate kiye hue code ko files mein likhta hai.
Folder structure banata hai, files create karta hai.
"""

import os
import subprocess

from config import PROJECTS_DIR


class ProjectBuilder:
    """AI generated code ko disk pe likhta hai aur run karta hai."""

    def __init__(self):
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        self.current_project_dir = None
        print(f"[ProjectBuilder] Ready. Projects at: {PROJECTS_DIR}")

    def build_project(self, project_data):
        """
        AI ke output se poora project disk pe banao.
        Returns: project directory path, or None on failure.
        """
        project_name = project_data.get("project_name", "my-project")
        files = project_data.get("files", [])
        setup_commands = project_data.get("setup_commands", [])

        # Clean project name
        project_name = "".join(
            c if c.isalnum() or c in "-_" else "-"
            for c in project_name
        ).strip("-")

        if not project_name:
            project_name = "my-project"

        project_dir = os.path.join(PROJECTS_DIR, project_name)

        # Agar folder pehle se hai to number add karo
        counter = 1
        original_dir = project_dir
        while os.path.exists(project_dir):
            project_dir = f"{original_dir}-{counter}"
            counter += 1

        os.makedirs(project_dir, exist_ok=True)
        self.current_project_dir = project_dir

        print(f"\n[ProjectBuilder] Building: {project_name}")
        print(f"[ProjectBuilder] Location: {project_dir}")
        print(f"[ProjectBuilder] Files: {len(files)}")

        # Create all files
        created_files = []
        for file_info in files:
            file_path = file_info.get("path", "")
            content = file_info.get("content", "")

            if not file_path:
                continue

            full_path = os.path.join(project_dir, file_path)

            # Create parent directories
            parent_dir = os.path.dirname(full_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            # Write file
            try:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                created_files.append(file_path)
                print(f"  Created: {file_path}")
            except Exception as e:
                print(f"  ERROR creating {file_path}: {e}")

        # Run setup commands
        if setup_commands:
            print(f"\n[ProjectBuilder] Running setup ({len(setup_commands)} commands)...")
            for cmd in setup_commands:
                print(f"  Running: {cmd}")
                try:
                    subprocess.run(
                        cmd, shell=True, cwd=project_dir,
                        timeout=60, capture_output=True, text=True
                    )
                except subprocess.TimeoutExpired:
                    print(f"  Setup timed out: {cmd}")
                except Exception as e:
                    print(f"  Setup error: {e}")

        print(f"\n[ProjectBuilder] Project ready at: {project_dir}")
        return project_dir

    def run_project(self, project_dir, run_command):
        """
        Project ko run karo aur output dikhao.
        Returns: (success, output) tuple.
        """
        if not run_command:
            return False, "No run command specified"

        print(f"\n[ProjectBuilder] Running: {run_command}")
        print(f"[ProjectBuilder] In: {project_dir}")
        print("-" * 40)

        try:
            result = subprocess.run(
                run_command, shell=True, cwd=project_dir,
                timeout=30, capture_output=True, text=True
            )

            output = ""
            if result.stdout:
                output += result.stdout
                print(result.stdout)
            if result.stderr:
                output += "\n" + result.stderr
                if result.returncode != 0:
                    print(f"[ERROR]\n{result.stderr}")

            print("-" * 40)

            if result.returncode == 0:
                print("[ProjectBuilder] Run successful!")
                return True, output
            else:
                print(f"[ProjectBuilder] Run failed (exit code: {result.returncode})")
                return False, output

        except subprocess.TimeoutExpired:
            msg = "Program timed out (30 sec limit for console apps)"
            print(f"[ProjectBuilder] {msg}")
            return True, msg
        except Exception as e:
            print(f"[ProjectBuilder] Run error: {e}")
            return False, str(e)

    def run_project_gui(self, project_dir, run_command):
        """
        GUI project ko background mein run karo (band nahi hoga).
        """
        if not run_command:
            return False

        print(f"\n[ProjectBuilder] Starting GUI app: {run_command}")

        try:
            subprocess.Popen(
                run_command, shell=True, cwd=project_dir,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            print("[ProjectBuilder] GUI app started!")
            return True
        except Exception as e:
            print(f"[ProjectBuilder] GUI launch error: {e}")
            return False

    def get_project_files(self, project_dir):
        """Project ke sab files read karo (improve ke liye)."""
        files = {}
        try:
            for root, dirs, filenames in os.walk(project_dir):
                # Skip hidden dirs and __pycache__
                dirs[:] = [d for d in dirs if not d.startswith((".", "__"))]
                for fname in filenames:
                    if fname.startswith("."):
                        continue
                    fpath = os.path.join(root, fname)
                    rel_path = os.path.relpath(fpath, project_dir)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            files[rel_path] = f.read()
                    except (UnicodeDecodeError, IOError):
                        pass
        except Exception as e:
            print(f"[ProjectBuilder] Read error: {e}")
        return files

    def open_in_explorer(self, project_dir):
        """Project folder Windows Explorer mein kholo."""
        try:
            os.startfile(project_dir)
            return True
        except Exception:
            try:
                subprocess.Popen(f'explorer "{project_dir}"', shell=True)
                return True
            except Exception:
                return False
