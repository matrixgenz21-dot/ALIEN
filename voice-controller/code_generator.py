"""
Mini Devin - Code Generator (Groq AI)
Bolo kya banana hai, AI poora code generate karega.
Files banayega, folder structure banayega, run karega.
"""

import json
import os

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

from config import GROQ_API_KEY, GROQ_MODEL, PROJECTS_DIR

CODE_SYSTEM_PROMPT = """You are Mini Devin — an AI coding assistant. The user will describe a project they want to build. You must generate the COMPLETE project with all files.

Return a JSON object with this structure:
{
    "project_name": "my-project",
    "description": "Short description of the project",
    "language": "python",
    "files": [
        {
            "path": "main.py",
            "content": "# full code here..."
        },
        {
            "path": "utils/helpers.py",
            "content": "# full code here..."
        }
    ],
    "run_command": "python main.py",
    "setup_commands": ["pip install requests"],
    "explanation": "Short explanation in the same language as user (Urdu/Hindi/English)"
}

RULES:
1. ALWAYS return valid JSON. No extra text.
2. Generate COMPLETE, WORKING code — not pseudocode or placeholders.
3. Include ALL necessary files — main code, helpers, config, etc.
4. The "run_command" should be the command to run the project.
5. "setup_commands" should list any pip install or other setup needed.
6. File paths should be relative to the project folder.
7. For Python projects: include proper imports, error handling, and main() function.
8. For HTML/CSS/JS projects: include index.html, style.css, script.js as needed.
9. For C/C++ projects: include the source files and compilation command.
10. Understand commands in ANY language — English, Urdu, Hindi, Roman Urdu, mixed.
11. The "explanation" should be in the same language as the user's request.
12. Make the code PROFESSIONAL quality — proper structure, comments, error handling.
13. If the user asks for a GUI app, use tkinter (Python) or HTML/CSS/JS.
14. Keep projects reasonable in size — max 10 files for simple requests.
15. Add helpful comments in the code.
16. The speech-to-text may mishear words. Understand the intent even if text is garbled.

EXAMPLES:
User: "Python mein calculator banao"
→ Generate a calculator with GUI (tkinter), all operations, nice UI

User: "HTML mein portfolio website banao"
→ Generate index.html, style.css with responsive design, sections for about/skills/contact

User: "todo app banao"
→ Generate a todo app with add/delete/complete functionality

User: "snake game banao"
→ Generate a snake game using pygame or tkinter

User: "API banao jo weather data de"
→ Generate a Flask/FastAPI server with weather endpoint
"""

IMPROVE_SYSTEM_PROMPT = """You are Mini Devin — an AI coding assistant. The user has a project and wants to improve/fix it. You will receive the current code and the user's request.

Return a JSON object with this structure:
{
    "files": [
        {
            "path": "main.py",
            "content": "# complete updated code..."
        }
    ],
    "run_command": "python main.py",
    "setup_commands": [],
    "explanation": "What was changed and why (in user's language)"
}

RULES:
1. Return COMPLETE file contents, not diffs or patches.
2. Only include files that need to change.
3. Fix errors, add features, improve code as requested.
4. Keep the explanation short and in the user's language.
"""


class CodeGenerator:
    """Groq AI se code generate karo — poora project banao."""

    def __init__(self):
        self._client = None
        self.enabled = False
        self.current_project = None

        if not GROQ_API_KEY:
            print("[CodeGen] Groq API key not set")
            return

        if not GROQ_AVAILABLE:
            print("[CodeGen] groq package not installed")
            return

        try:
            self._client = Groq(api_key=GROQ_API_KEY)
            self.enabled = True
            os.makedirs(PROJECTS_DIR, exist_ok=True)
            print(f"[CodeGen] Ready! Projects folder: {PROJECTS_DIR}")
        except Exception as e:
            print(f"[CodeGen] Init error: {e}")

    def generate_project(self, description):
        """
        User ki description se poora project generate karo.
        Returns: dict with project info, or None on failure.
        """
        if not self.enabled:
            return None

        print(f"[CodeGen] Generating project: {description}")

        try:
            response = self._client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": CODE_SYSTEM_PROMPT},
                    {"role": "user", "content": description},
                ],
                temperature=0.2,
                max_tokens=8192,
                response_format={"type": "json_object"},
            )

            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)

            project_name = result.get("project_name", "my-project")
            files = result.get("files", [])
            print(f"[CodeGen] Generated: {project_name} ({len(files)} files)")

            return result

        except json.JSONDecodeError as e:
            print(f"[CodeGen] JSON parse error: {e}")
            return None
        except Exception as e:
            print(f"[CodeGen] API error: {e}")
            return None

    def improve_project(self, description, project_files):
        """
        Existing project ko improve/fix karo.
        """
        if not self.enabled:
            return None

        context = "Current project files:\n\n"
        for fpath, content in project_files.items():
            context += f"--- {fpath} ---\n{content}\n\n"

        context += f"\nUser request: {description}"

        try:
            response = self._client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": IMPROVE_SYSTEM_PROMPT},
                    {"role": "user", "content": context},
                ],
                temperature=0.2,
                max_tokens=8192,
                response_format={"type": "json_object"},
            )

            result_text = response.choices[0].message.content.strip()
            return json.loads(result_text)

        except Exception as e:
            print(f"[CodeGen] Improve error: {e}")
            return None
