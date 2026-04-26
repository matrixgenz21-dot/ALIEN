# Voice Controller Bot

**Apni awaz se apna computer chalao!** - Control your computer with your voice!

Ye bot tumhari awaz sun ke mouse, keyboard, media player, aur apps control karta hai. Un logon ke liye jo keyboard/mouse use nahi kar sakte ya voice se kaam karna chahte hain.

---

## Features / Kya kar sakta hai

| Feature | Commands |
|---------|----------|
| **Mouse Control** | move up/down/left/right, click, double click, right click, scroll, drag & drop |
| **Keyboard** | type any text, press any key (enter, escape, tab, etc.) |
| **Shortcuts** | copy, paste, cut, undo, redo, save, select all, find, etc. |
| **Media** | play, pause, stop, next track, previous track, volume up/down, mute |
| **Apps** | open notepad, chrome, calculator, or any app by name |
| **Websites** | "go to youtube.com" - browser mein open ho jaye ga |
| **Window Control** | minimize, maximize, close window, switch window |
| **Repeat** | "scroll down 5 times" - koi bhi command repeat karo |

---

## Setup / Install Kaise Karo

### Step 1: Python Install Karo
1. Jao: **https://www.python.org/downloads/**
2. Download karo **Python 3.10+** (latest version)
3. Install karte waqt **"Add Python to PATH"** checkbox **zaroor check karo!**

### Step 2: Voice Controller Files Copy Karo
1. Ye poora `voice-controller` folder apne laptop mein kisi jagah copy karo
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

### Step 4: Bot Chalao
1. **`run.bat`** double-click karo
2. Ya CMD kholo, folder mein jao, aur type karo:
   ```
   python main.py
   ```

---

## Commands / Kya Bol Sakte Ho

### Mouse Commands
| Bolo | Kya Hoga |
|------|----------|
| "mouse up" | Mouse upar jaye ga |
| "mouse down" | Mouse neeche jaye ga |
| "mouse left" | Mouse baayein jaye ga |
| "mouse right" | Mouse daayein jaye ga |
| "move fast up" | Mouse tezi se upar |
| "click" | Left click |
| "double click" | Double click |
| "right click" | Right click |
| "scroll up" | Page upar scroll |
| "scroll down" | Page neeche scroll |
| "center mouse" | Mouse screen ke beech mein |
| "drag" | Drag start (hold) |
| "drop" | Drag end (release) |

### Keyboard Commands
| Bolo | Kya Hoga |
|------|----------|
| "type hello world" | "hello world" type ho jaye ga |
| "press enter" | Enter key |
| "press escape" | Escape key |
| "press tab" | Tab key |
| "press space" | Space bar |
| "press backspace" | Backspace |
| "press delete" | Delete key |
| "press up/down/left/right" | Arrow keys |

### Shortcuts
| Bolo | Kya Hoga |
|------|----------|
| "copy" | Ctrl+C |
| "paste" | Ctrl+V |
| "cut" | Ctrl+X |
| "undo" | Ctrl+Z |
| "redo" | Ctrl+Y |
| "select all" | Ctrl+A |
| "save" | Ctrl+S |
| "find" | Ctrl+F |
| "new tab" | Ctrl+T |
| "close tab" | Ctrl+W |
| "close window" | Alt+F4 |
| "switch window" | Alt+Tab |
| "screenshot" | Win+Shift+S |
| "zoom in" | Ctrl++ |
| "zoom out" | Ctrl+- |

### Media Controls
| Bolo | Kya Hoga |
|------|----------|
| "play" / "pause" | Play/Pause toggle |
| "stop" | Stop media |
| "next track" | Agla gaana |
| "previous track" | Pichla gaana |
| "volume up" | Awaz barha |
| "volume down" | Awaz kam kar |
| "mute" | Mute toggle |

### App Commands
| Bolo | Kya Hoga |
|------|----------|
| "open notepad" | Notepad khul jaye ga |
| "open chrome" | Chrome browser khule ga |
| "open calculator" | Calculator khule ga |
| "open paint" | MS Paint khule ga |
| "open file manager" | File Explorer khule ga |
| "open cmd" | Command Prompt khule ga |

### Website Commands
| Bolo | Kya Hoga |
|------|----------|
| "go to youtube.com" | YouTube open hoga |
| "go to google.com" | Google open hoga |

### System Commands
| Bolo | Kya Hoga |
|------|----------|
| "help" | Sab commands dikhao |
| "status" | Mouse position aur screen info |
| "stop listening" | Sunna band karo |
| "start listening" | Dubara sunna shuru karo |
| "exit" / "quit" / "goodbye" | Bot band karo |

### Repeat Commands
| Bolo | Kya Hoga |
|------|----------|
| "scroll down 5 times" | 5 baar scroll down |
| "mouse up 10 times" | 10 baar mouse up |
| "click 3 times" | 3 baar click |

---

## Settings / Settings Badlo

`config.py` file mein ye cheezein change kar sakte ho:

| Setting | Default | Description |
|---------|---------|-------------|
| `LANGUAGE` | `"en-US"` | `"en-US"` English, `"ur-PK"` Urdu |
| `WAKE_WORD` | `"hello"` | Bot tab active ho jab ye bolo. `None` = always active |
| `MOUSE_STEP` | `30` | Mouse kitna move kare (pixels) |
| `MOUSE_FAST_STEP` | `100` | Fast move mein kitna move kare |
| `SPEECH_RATE` | `170` | Bot kitni tezi se bole |
| `SPEECH_VOLUME` | `0.9` | Bot ki awaz (0.0 to 1.0) |
| `ENERGY_THRESHOLD` | `300` | Mic sensitivity (kam = zyada sensitive) |

---

## Custom Commands / Apne Commands Banao

`commands.json` file mein apne commands add kar sakte ho:

```json
{
    "commands": {
        "open youtube": "start chrome https://www.youtube.com",
        "open google": "start chrome https://www.google.com",
        "play music": "start wmplayer"
    }
}
```

Bot restart karo changes apply karne ke liye.

---

## Troubleshooting / Masla Aaye To

### "Python nahi mila"
- Python install karo: https://www.python.org/downloads/
- **"Add Python to PATH"** zaroor check karo

### "PyAudio install nahi ho raha"
```
pip install pipwin
pipwin install pyaudio
```

### "Microphone kaam nahi kar raha"
- Windows Settings > Privacy > Microphone > Apps ko allow karo
- Microphone connected hai ya nahi check karo

### "Awaz samajh nahi aa rahi"
- Internet connection check karo (Google Speech API online kaam karta hai)
- Shor wali jagah se door jao
- `config.py` mein `ENERGY_THRESHOLD` kam karo (e.g., 200)

### "Commands kaam nahi kar rahe"
- Admin mode mein run karo (right click > Run as Administrator)
- Antivirus mein exception add karo

---

## File Structure

```
voice-controller/
├── main.py                  # Main program - ye chalao
├── voice_engine.py          # Awaz sun ne ka module
├── command_parser.py        # Awaz ko command mein badle
├── mouse_controller.py      # Mouse control
├── keyboard_controller.py   # Keyboard control
├── media_controller.py      # Media playback control
├── app_launcher.py          # Apps open/close
├── speaker.py               # Bot bolta hai (TTS)
├── config.py                # Settings aur command mappings
├── commands.json            # Custom commands (user-editable)
├── requirements.txt         # Python packages list
├── setup.bat                # One-click setup (double-click)
├── run.bat                  # One-click run (double-click)
└── README.md                # Ye file - instructions
```

---

## Requirements

- **Windows 10/11**
- **Python 3.10+**
- **Microphone** (laptop ka built-in bhi chal jaye ga)
- **Internet connection** (Google Speech Recognition ke liye)

---

Made with care for accessibility.
