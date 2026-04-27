"""
AI Chatbot - Intelligent chatbot for businesses
By: Matrix (Fiverr Portfolio Demo)

Features:
- GUI interface with modern dark theme
- AI-powered responses (Groq/OpenAI compatible)
- Customizable personality and business info
- Chat history saved
- Works offline with fallback responses
- Easy to customize for any business

Usage:
    python chatbot.py
"""

import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import json
import os
import re
import threading

# Try to import AI library
try:
    from groq import Groq
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


# ============= CUSTOMIZE YOUR CHATBOT HERE =============
BOT_NAME = "Matrix AI Assistant"
BOT_PERSONALITY = """You are a friendly and helpful AI assistant for a Pakistani software development business. 
You speak in a mix of English and Roman Urdu. You help customers with:
- Software development inquiries
- Price quotes for projects
- Technical support
- General questions

Business Info:
- Name: Matrix Tech Solutions
- Location: Lahore, Pakistan
- Services: Web Development, Mobile Apps, Desktop Software, AI/Automation, Web Scraping
- Pricing: Starting from Rs 5,000 for simple projects
- Contact: WhatsApp available
- Working Hours: Mon-Sat, 10 AM - 8 PM

Be friendly, professional, and helpful. If you don't know something, ask for more details."""

GROQ_API_KEY = ""  # Optional: Paste your Groq API key for AI responses
# ========================================================


# Fallback responses when AI is not available
FALLBACK_RESPONSES = {
    "hello": "Hello! Welcome to Matrix Tech Solutions. How can I help you today?",
    "hi": "Hi there! Main Matrix AI Assistant hoon. Kaise help kar sakta hoon?",
    "price": "Hamari services Rs 5,000 se start hoti hain. Aapko kaunsi service chahiye?\n\n1. Web Development (Rs 10,000+)\n2. Mobile App (Rs 25,000+)\n3. Desktop Software (Rs 15,000+)\n4. Web Scraping (Rs 5,000+)\n5. AI Chatbot (Rs 8,000+)",
    "service": "Hum ye services offer karte hain:\n- Web Development\n- Mobile Apps\n- Desktop Software\n- AI & Automation\n- Web Scraping\n- Custom Chatbots\n\nKaunsi service mein interest hai?",
    "contact": "Aap hamse WhatsApp pe contact kar sakte hain!\nWorking hours: Mon-Sat, 10 AM - 8 PM",
    "time": "Hamari working hours: Monday to Saturday, 10 AM - 8 PM (Pakistan Time)",
    "thanks": "Shukriya! Agar aur koi sawal ho to zaroor poochiye. Happy to help!",
    "bye": "Allah Hafiz! Phir milein ge. Have a great day!",
    "default": "Main samajh nahi paaya. Kya aap thoda detail mein bata sakte hain? Ya in topics ke baare mein poochein:\n- Services\n- Pricing\n- Contact Info",
}


class ChatbotGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(BOT_NAME)
        self.root.geometry("500x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f0f23")

        self.ai_client = None
        self.chat_history = []
        self._init_ai()
        self._create_ui()

    def _init_ai(self):
        if AI_AVAILABLE and GROQ_API_KEY:
            try:
                self.ai_client = Groq(api_key=GROQ_API_KEY)
                print(f"[{BOT_NAME}] AI mode enabled!")
            except Exception as e:
                print(f"[{BOT_NAME}] AI init failed: {e}")
        else:
            print(f"[{BOT_NAME}] Running in fallback mode (no AI)")

    def _create_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#1a1a3e", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text=BOT_NAME, bg="#1a1a3e", fg="#00d4ff",
            font=("Segoe UI", 16, "bold")
        ).pack(side="left", padx=20, pady=15)

        status_text = "AI Online" if self.ai_client else "Basic Mode"
        status_color = "#00ff88" if self.ai_client else "#ffaa00"
        tk.Label(
            header, text=f"● {status_text}", bg="#1a1a3e", fg=status_color,
            font=("Segoe UI", 10)
        ).pack(side="right", padx=20)

        # Chat area
        chat_frame = tk.Frame(self.root, bg="#0f0f23")
        chat_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.chat_area = scrolledtext.ScrolledText(
            chat_frame, bg="#0f0f23", fg="white",
            font=("Segoe UI", 11), wrap=tk.WORD,
            relief="flat", borderwidth=0, state="disabled",
            selectbackground="#1a1a3e"
        )
        self.chat_area.pack(fill="both", expand=True)

        # Configure tags for different message styles
        self.chat_area.tag_configure("bot", foreground="#00d4ff")
        self.chat_area.tag_configure("user", foreground="#ff6b9d")
        self.chat_area.tag_configure("system", foreground="#666688")
        self.chat_area.tag_configure("time", foreground="#444466")

        # Input frame
        input_frame = tk.Frame(self.root, bg="#1a1a3e", height=60)
        input_frame.pack(fill="x", padx=10, pady=10)
        input_frame.pack_propagate(False)

        self.input_field = tk.Entry(
            input_frame, bg="#2a2a4e", fg="white",
            font=("Segoe UI", 13), relief="flat",
            insertbackground="white", borderwidth=0
        )
        self.input_field.pack(side="left", fill="both", expand=True, padx=(15, 10), pady=12)
        self.input_field.bind("<Return>", self._on_send)
        self.input_field.focus()

        send_btn = tk.Button(
            input_frame, text="Send", bg="#00d4ff", fg="black",
            font=("Segoe UI", 12, "bold"), relief="flat",
            command=self._on_send, cursor="hand2",
            activebackground="#00b8e6"
        )
        send_btn.pack(side="right", padx=(0, 15), pady=12)

        # Welcome message
        self._add_message("bot", f"Assalam o Alaikum! Main {BOT_NAME} hoon.\nKaise help kar sakta hoon? 😊")

    def _add_message(self, sender, text):
        self.chat_area.config(state="normal")

        timestamp = datetime.now().strftime("%H:%M")

        if sender == "bot":
            self.chat_area.insert("end", f"\n🤖 {BOT_NAME}", "bot")
            self.chat_area.insert("end", f"  {timestamp}\n", "time")
            self.chat_area.insert("end", f"{text}\n", "bot")
        elif sender == "user":
            self.chat_area.insert("end", f"\n👤 You", "user")
            self.chat_area.insert("end", f"  {timestamp}\n", "time")
            self.chat_area.insert("end", f"{text}\n", "user")
        else:
            self.chat_area.insert("end", f"\n{text}\n", "system")

        self.chat_area.config(state="disabled")
        self.chat_area.see("end")

        self.chat_history.append({
            "sender": sender,
            "text": text,
            "time": timestamp
        })

    def _on_send(self, event=None):
        text = self.input_field.get().strip()
        if not text:
            return

        self.input_field.delete(0, "end")
        self._add_message("user", text)

        history_snapshot = list(self.chat_history)
        threading.Thread(target=self._get_response, args=(text, history_snapshot), daemon=True).start()

    def _get_response(self, user_text, history_snapshot=None):
        if self.ai_client:
            response = self._get_ai_response(user_text, history_snapshot)
        else:
            response = self._get_fallback_response(user_text)

        self.root.after(0, self._add_message, "bot", response)

    def _get_ai_response(self, text, history_snapshot=None):
        try:
            messages = [{"role": "system", "content": BOT_PERSONALITY}]

            history = history_snapshot if history_snapshot is not None else list(self.chat_history)
            for msg in history[-11:-1]:
                role = "assistant" if msg["sender"] == "bot" else "user"
                messages.append({"role": role, "content": msg["text"]})

            messages.append({"role": "user", "content": text})

            response = self.ai_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[AI Error] {e}")
            return self._get_fallback_response(text)

    def _get_fallback_response(self, text):
        text_lower = text.lower()
        for keyword, response in FALLBACK_RESPONSES.items():
            if keyword != "default" and re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                return response
        return FALLBACK_RESPONSES["default"]

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ChatbotGUI()
    app.run()
