"""
Professional GUI Calculator
By: Matrix (Fiverr Portfolio Demo)

Features:
- Modern dark theme design
- All basic operations (+, -, *, /)
- Percentage, square root, power
- Keyboard support
- History of calculations
- Clear and backspace buttons
"""

import tkinter as tk
from tkinter import font as tkfont
import math


class Calculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Matrix Calculator Pro")
        self.root.geometry("380x620")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")

        self.current = ""
        self.result = ""
        self.history = []

        self._create_ui()
        self._bind_keys()

    def _create_ui(self):
        # Title bar
        title_frame = tk.Frame(self.root, bg="#16213e", height=40)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame, text="Calculator Pro",
            bg="#16213e", fg="#e94560", font=("Segoe UI", 12, "bold")
        ).pack(side="left", padx=15, pady=8)

        # Display frame
        display_frame = tk.Frame(self.root, bg="#1a1a2e", height=140)
        display_frame.pack(fill="x", padx=15, pady=(10, 5))
        display_frame.pack_propagate(False)

        # Expression label
        self.expr_label = tk.Label(
            display_frame, text="", bg="#1a1a2e", fg="#8a8a9a",
            font=("Segoe UI", 14), anchor="e"
        )
        self.expr_label.pack(fill="x", pady=(10, 0))

        # Result label
        self.result_label = tk.Label(
            display_frame, text="0", bg="#1a1a2e", fg="#ffffff",
            font=("Segoe UI", 36, "bold"), anchor="e"
        )
        self.result_label.pack(fill="x", pady=(5, 10))

        # Buttons
        btn_frame = tk.Frame(self.root, bg="#1a1a2e")
        btn_frame.pack(fill="both", expand=True, padx=15, pady=10)

        buttons = [
            [("C", "#e94560"), ("()", "#0f3460"), ("%", "#0f3460"), ("/", "#e94560")],
            [("7", "#16213e"), ("8", "#16213e"), ("9", "#16213e"), ("*", "#e94560")],
            [("4", "#16213e"), ("5", "#16213e"), ("6", "#16213e"), ("-", "#e94560")],
            [("1", "#16213e"), ("2", "#16213e"), ("3", "#16213e"), ("+", "#e94560")],
            [("+-", "#0f3460"), ("0", "#16213e"), (".", "#16213e"), ("=", "#e94560")],
        ]

        for i, row in enumerate(buttons):
            btn_frame.grid_rowconfigure(i, weight=1)
            for j, (text, color) in enumerate(row):
                btn_frame.grid_columnconfigure(j, weight=1)
                btn = tk.Button(
                    btn_frame, text=text, bg=color, fg="white",
                    font=("Segoe UI", 18, "bold"),
                    relief="flat", borderwidth=0,
                    activebackground="#533483", activeforeground="white",
                    command=lambda t=text: self._on_click(t)
                )
                btn.grid(row=i, column=j, padx=3, pady=3, sticky="nsew")

        # Extra buttons row
        extra_frame = tk.Frame(self.root, bg="#1a1a2e")
        extra_frame.pack(fill="x", padx=15, pady=(0, 15))

        extras = [("sqrt", "#0f3460"), ("x^2", "#0f3460"), ("1/x", "#0f3460"), ("DEL", "#0f3460")]
        for i, (text, color) in enumerate(extras):
            extra_frame.grid_columnconfigure(i, weight=1)
            btn = tk.Button(
                extra_frame, text=text, bg=color, fg="white",
                font=("Segoe UI", 12), relief="flat",
                activebackground="#533483",
                command=lambda t=text: self._on_click(t)
            )
            btn.grid(row=0, column=i, padx=3, pady=3, sticky="ew")

    def _bind_keys(self):
        self.root.bind("<Key>", self._on_key)
        self.root.bind("<Return>", lambda e: self._on_click("="))
        self.root.bind("<BackSpace>", lambda e: self._on_click("DEL"))
        self.root.bind("<Escape>", lambda e: self._on_click("C"))

    def _on_key(self, event):
        char = event.char
        if char in "0123456789.+-*/()%":
            self._on_click(char)

    def _on_click(self, text):
        if text == "C":
            self.current = ""
            self.result = ""
            self._update_display("", "0")

        elif text == "DEL":
            self.current = self.current[:-1]
            self._update_display(self.current, self.current or "0")

        elif text == "=":
            if self.current:
                try:
                    expr = self.current.replace("^", "**")
                    res = eval(expr)
                    res_str = str(res)
                    if "." in res_str:
                        res = round(res, 10)
                        res_str = str(res)
                        if res_str.endswith(".0"):
                            res_str = res_str[:-2]
                    self.history.append(f"{self.current} = {res_str}")
                    self._update_display(f"{self.current} =", res_str)
                    self.current = res_str
                except ZeroDivisionError:
                    self._update_display(self.current, "Cannot divide by zero")
                    self.current = ""
                except Exception:
                    self._update_display(self.current, "Error")
                    self.current = ""

        elif text == "+-":
            if self.current and self.current[0] == "-":
                self.current = self.current[1:]
            elif self.current:
                self.current = "-" + self.current
            self._update_display("", self.current or "0")

        elif text == "%":
            if self.current:
                try:
                    res = eval(self.current) / 100
                    self.current = str(res)
                    self._update_display("", self.current)
                except Exception:
                    pass

        elif text == "sqrt":
            if self.current:
                try:
                    val = eval(self.current)
                    if val >= 0:
                        res = math.sqrt(val)
                        self._update_display(f"sqrt({self.current})", str(round(res, 10)))
                        self.current = str(round(res, 10))
                    else:
                        self._update_display("", "Invalid input")
                except Exception:
                    pass

        elif text == "x^2":
            if self.current:
                try:
                    val = eval(self.current)
                    res = val ** 2
                    self._update_display(f"({self.current})^2", str(res))
                    self.current = str(res)
                except Exception:
                    pass

        elif text == "1/x":
            if self.current:
                try:
                    val = eval(self.current)
                    if val != 0:
                        res = 1 / val
                        self._update_display(f"1/({self.current})", str(round(res, 10)))
                        self.current = str(round(res, 10))
                    else:
                        self._update_display("", "Cannot divide by zero")
                except Exception:
                    pass

        elif text == "()":
            open_count = self.current.count("(")
            close_count = self.current.count(")")
            if open_count == close_count or (self.current and self.current[-1] in "+-*/("):
                self.current += "("
            else:
                self.current += ")"
            self._update_display("", self.current)

        else:
            self.current += text
            self._update_display("", self.current)

    def _update_display(self, expr, result):
        self.expr_label.config(text=expr)
        display_text = result
        if len(display_text) > 15:
            try:
                num = float(display_text)
                display_text = f"{num:.6e}"
            except (ValueError, OverflowError):
                display_text = display_text[:15] + "..."
        self.result_label.config(text=display_text)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = Calculator()
    app.run()
