# Voice Controller Bot

**Apni awaz se apna computer chalao!** - Control your computer with your voice!

Ye bot tumhari awaz sun ke mouse, keyboard, media player, aur apps control karta hai.
**AI Mode** mein kuch bhi bolo — kisi bhi zuban mein — bot samajh ke kaam karega!

---

## AI Mode (Groq AI)

AI mode ON karne se tumhe koi specific command yaad rakhne ki zaroorat NAHI.
Kuch bhi bolo, jaise:

- "zara mouse thoda upar le jao" → mouse upar
- "ye band karo" → window close
- "awaaz barha do" → volume up
- "chrome khol do" → Chrome open
- "kuch likh do hello world" → type karega
- "youtube khol do" → YouTube open
- "agla gaana laga do" → next track
- "kya tum mujhe sun sakte ho?" → bot jawab de ga!

**English, Urdu, Hindi, Roman Urdu — kuch bhi bolo!**

---

## Setup / Install Kaise Karo (Step by Step)

### Step 1: Python Install Karo
1. Jao: **https://www.python.org/downloads/**
2. Download karo **Python 3.10+** (latest version)
3. Install karte waqt **"Add Python to PATH"** checkbox **zaroor check karo!**

### Step 2: Voice Controller Files Copy Karo
1. GitHub se poora `voice-controller` folder download karo
2. Apne laptop mein kisi jagah paste karo
   - Example: `C:\Users\TumharaName\Desktop\voice-controller\`

### Step 3: Setup Run Karo
1. `voice-controller` folder mein jao
2. **`setup.bat`** double-click karo
3. Sab packages automatically install ho jayein ge
4. Agar PyAudio mein error aaye to CMD mein ye likho:
   ```
   pip install pipwin
   pipwin install pyaudio
   ```

### Step 4: Groq AI Key Lagao (FREE hai!)
1. Jao: **https://console.groq.com/keys**
2. Sign up karo (Google account se bhi ho jata hai)
3. **"Create API Key"** button click karo
4. Jo key mile wo copy karo
5. `config.py` file Notepad mein kholo
6. Line 10 mein `GROQ_API_KEY = ""` ke andar key paste karo:
   ```python
   GROQ_API_KEY = "gsk_tumhari_key_yahan_paste_karo"
   ```
7. File save karo (Ctrl+S)

### Step 5: Bot Chalao
1. **`run.bat`** double-click karo
2. Bolo kuch bhi — bot samjhe ga aur kaam karega!

---

## Kya Bol Sakte Ho (Examples)

### Mouse
| Bolo (kuch bhi) | Kya Hoga |
|------|----------|
| "mouse upar" / "upar le jao" | Mouse upar jaye ga |
| "neeche" / "mouse down" | Mouse neeche |
| "click karo" / "click" | Left click |
| "double click" | Double click |
| "right click" | Right click |
| "scroll upar" / "scroll up" | Page upar scroll |
| "scroll neeche" | Page neeche scroll |

### Keyboard / Typing
| Bolo | Kya Hoga |
|------|----------|
| "likh do hello world" / "type hello" | Text type karega |
| "enter dabao" / "press enter" | Enter key |
| "backspace" | Backspace key |
| "escape" | Escape key |

### Shortcuts
| Bolo | Kya Hoga |
|------|----------|
| "copy karo" | Ctrl+C |
| "paste karo" | Ctrl+V |
| "undo" | Ctrl+Z |
| "save karo" | Ctrl+S |
| "select all" | Ctrl+A |
| "find karo" | Ctrl+F |
| "tab band karo" / "close tab" | Ctrl+W |
| "window band karo" | Alt+F4 |
| "screenshot lo" | Win+Shift+S |

### Media
| Bolo | Kya Hoga |
|------|----------|
| "gaana chalao" / "play" | Play/Pause |
| "awaaz barha do" / "volume up" | Volume up |
| "awaaz kam karo" | Volume down |
| "agla gaana" / "next" | Next track |
| "mute karo" | Mute |

### Apps Kholna
| Bolo | Kya Hoga |
|------|----------|
| "notepad kholo" / "open notepad" | Notepad |
| "chrome kholo" | Chrome browser |
| "calculator kholo" | Calculator |
| "paint kholo" | MS Paint |
| "file manager kholo" | File Explorer |

### Websites
| Bolo | Kya Hoga |
|------|----------|
| "youtube khol do" | YouTube open |
| "google kholo" | Google open |

### System
| Bolo | Kya Hoga |
|------|----------|
| "help" | Commands dikhao |
| "exit" / "band karo" | Bot band karo |

### Baat Cheet (Chat)
AI mode mein tum bot se baat bhi kar sakte ho:
- "kya tum mujhe sun sakte ho?" → "Haan! Main sun raha hoon!"
- "tum kya kar sakte ho?" → Bot bataye ga

---

## Settings Badlna

`config.py` file Notepad mein kholo. Important settings:

| Setting | Kya hai | Default |
|---------|---------|---------|
| `GROQ_API_KEY` | Tumhari Groq API key | `""` (khali) |
| `USE_AI` | AI mode on/off | `True` |
| `LANGUAGE` | Zuban | `"en-US"` |
| `MOUSE_STEP` | Mouse kitna move kare | `30` |
| `SPEECH_RATE` | Bot kitni tezi se bole | `170` |
| `SPEECH_VOLUME` | Bot ki awaz | `0.9` |

---

## File Structure

```
voice-controller/
├── main.py                  # Main program - ye chalao
├── ai_brain.py              # Groq AI - kuch bhi samjhe
├── voice_engine.py          # Awaz sun ne ka module
├── command_parser.py        # Commands parse kare (backup)
├── mouse_controller.py      # Mouse control
├── keyboard_controller.py   # Keyboard control
├── media_controller.py      # Media playback control
├── app_launcher.py          # Apps open/close
├── speaker.py               # Bot bolta hai (TTS)
├── config.py                # Settings - GROQ KEY YAHAN LAGAO
├── commands.json            # Custom commands
├── requirements.txt         # Python packages list
├── setup.bat                # Setup (double-click)
├── run.bat                  # Run (double-click)
└── README.md                # Ye file
```

---

## Masla Aaye To (Troubleshooting)

### "Python nahi mila"
- Python install karo: https://www.python.org/downloads/
- **"Add Python to PATH"** zaroor check karo

### "PyAudio install nahi ho raha"
```
pip install pipwin
pipwin install pyaudio
```

### "AI kaam nahi kar raha"
- `config.py` mein `GROQ_API_KEY` set karo
- Internet connection check karo
- Key free hai: https://console.groq.com/keys

### "Awaz samajh nahi aa rahi"
- Internet connection check karo
- Microphone connected hai check karo
- Windows Settings > Privacy > Microphone > Apps ko allow karo

---

## Requirements

- **Windows 10/11**
- **Python 3.10+**
- **Microphone** (laptop ka built-in bhi chal jaye ga)
- **Internet connection**
- **Groq API key** (FREE — https://console.groq.com/keys)

---

Made with care for accessibility.
