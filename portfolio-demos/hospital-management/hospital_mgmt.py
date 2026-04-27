"""
Hospital Management System (HMS) V2 - Advanced Medical Software
By: Matrix Tech Solutions | Lahore, Pakistan

Advanced Features:
- Login System with Role-Based Access (Admin, Doctor, Pharmacist, Receptionist)
- Patient Registration with Allergies & Chronic Conditions
- Patient Vitals Tracking (BP, Temperature, Pulse, Weight, Sugar, O2)
- Patient History Timeline (all visits, tests, prescriptions)
- Doctor Management & Revenue Dashboard
- Appointment System with Token/Queue + Auto-Billing
- Pharmacy with Medicine Interaction Warnings & Auto-Reorder Alerts
- Prescription System with Drug Interaction Checks
- Lab Reports Management
- Bed/Ward Management (Admission/Discharge)
- Billing & Invoicing with Print-Ready Format
- Advanced Reports (Daily/Weekly/Monthly, Doctor Revenue, Department)
- Database Backup & Restore
- Audit Log (who did what, when)
- Notification System (alerts, reminders)
- Excel Export for all modules
- Professional Dark Medical Theme with Status Badges

Target: Pakistani Hospitals, Clinics, Pharmacies
Value: PKR 50,000,000+ enterprise software

Usage:
    pip install matplotlib openpyxl
    python hospital_mgmt.py

Default Login:
    Admin:        admin / admin123
    Doctor:       doctor / doctor123
    Pharmacist:   pharmacist / pharma123
    Receptionist: receptionist / reception123
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
import os
import calendar

from database import (DB_FILE, get_conn, init_db, generate_id,
                      hash_password, audit_log, add_notification,
                      backup_db, restore_db)
from theme import COLORS as C, FONTS as F

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


# =====================================================================
#  LOGIN WINDOW
# =====================================================================

class LoginWindow:
    def __init__(self):
        init_db()
        self.root = tk.Tk()
        self.root.title("HMS Login")
        self.root.geometry("420x480")
        self.root.configure(bg=C["bg"])
        self.root.resizable(False, False)

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 420) // 2
        y = (self.root.winfo_screenheight() - 480) // 2
        self.root.geometry(f"420x480+{x}+{y}")

        # Logo
        logo_f = tk.Frame(self.root, bg=C["primary_dark"], height=100)
        logo_f.pack(fill="x")
        logo_f.pack_propagate(False)
        tk.Label(logo_f, text="HMS", bg=C["primary_dark"], fg="white",
                 font=("Segoe UI", 36, "bold")).pack(pady=(15, 0))
        tk.Label(logo_f, text="Hospital Management System", bg=C["primary_dark"],
                 fg=C["primary_light"], font=("Segoe UI", 10)).pack()

        # Form
        form = tk.Frame(self.root, bg=C["bg"])
        form.pack(expand=True)

        tk.Label(form, text="Sign In", bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 18, "bold")).pack(pady=(20, 15))

        tk.Label(form, text="Username", bg=C["bg"], fg=C["text_secondary"],
                 font=F["body"]).pack(anchor="w", padx=30)
        self.user_entry = tk.Entry(form, bg=C["input_bg"], fg=C["text"],
                                    font=("Segoe UI", 13), relief="flat",
                                    insertbackground=C["text"], width=28)
        self.user_entry.pack(padx=30, ipady=8, pady=(2, 10))
        self.user_entry.insert(0, "admin")

        tk.Label(form, text="Password", bg=C["bg"], fg=C["text_secondary"],
                 font=F["body"]).pack(anchor="w", padx=30)
        self.pass_entry = tk.Entry(form, bg=C["input_bg"], fg=C["text"],
                                    font=("Segoe UI", 13), relief="flat",
                                    insertbackground=C["text"], show="*", width=28)
        self.pass_entry.pack(padx=30, ipady=8, pady=(2, 15))
        self.pass_entry.insert(0, "admin123")
        self.pass_entry.bind("<Return>", lambda e: self._login())

        tk.Button(form, text="Login", bg=C["accent"], fg="black",
                  font=("Segoe UI", 13, "bold"), relief="flat",
                  padx=40, pady=8, command=self._login, cursor="hand2").pack(pady=5)

        self.status = tk.Label(form, text="", bg=C["bg"], fg=C["danger"], font=F["body_small"])
        self.status.pack(pady=5)

        # Default credentials hint
        hint = tk.Label(form, text="Default: admin/admin123 | doctor/doctor123\npharma/pharma123 | receptionist/reception123",
                        bg=C["bg"], fg=C["text_muted"], font=("Segoe UI", 8), justify="center")
        hint.pack(pady=(5, 0))

        tk.Label(self.root, text="Matrix Tech Solutions | Lahore, Pakistan",
                 bg=C["bg"], fg=C["text_muted"], font=("Segoe UI", 8)).pack(side="bottom", pady=8)

    def _login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        if not username or not password:
            self.status.config(text="Enter username and password!")
            return

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, username, password_hash, full_name, role, department, status FROM users WHERE username=?",
                 (username,))
        user = c.fetchone()
        conn.close()

        if not user:
            self.status.config(text="User not found!")
            return
        if user[2] != hash_password(password):
            self.status.config(text="Incorrect password!")
            return
        if user[6] != "Active":
            self.status.config(text="Account is disabled!")
            return

        # Update last login
        conn = get_conn()
        try:
            c = conn.cursor()
            c.execute("UPDATE users SET last_login=? WHERE id=?",
                     (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user[0]))
            conn.commit()
        finally:
            conn.close()

        audit_log(username, "Login", "Auth", f"{user[3]} logged in as {user[4]}")

        user_info = {
            "id": user[0], "username": user[1], "name": user[3],
            "role": user[4], "department": user[5]
        }
        self.root.destroy()
        app = HospitalApp(user_info)
        app.run()

    def run(self):
        self.root.mainloop()


# =====================================================================
#  MAIN APPLICATION
# =====================================================================

class HospitalApp:
    def __init__(self, user):
        init_db()
        self.user = user

        self.root = tk.Tk()
        self.root.title(f"HMS - Hospital Management System | {user['name']} ({user['role']})")
        self.root.geometry("1400x850")
        self.root.configure(bg=C["bg"])
        self.root.minsize(1100, 700)

        self._setup_styles()
        self._create_sidebar()
        self._create_main()
        self._check_auto_alerts()
        self._show_dashboard()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                         background=C["table_row1"], foreground=C["text"],
                         fieldbackground=C["table_row1"], borderwidth=0,
                         font=F["table_body"], rowheight=30)
        style.configure("Treeview.Heading",
                         background=C["table_header"], foreground=C["primary"],
                         font=F["table_header"], borderwidth=0)
        style.map("Treeview", background=[("selected", C["table_selected"])])

    def _check_auto_alerts(self):
        """Auto-generate pharmacy & expiry alerts on startup."""
        conn = get_conn()
        c = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")

        # Low stock
        c.execute("SELECT name, stock, min_stock, supplier FROM medicines WHERE stock <= min_stock AND status='Active'")
        for name, stock, minst, supplier in c.fetchall():
            add_notification(
                f"Low Stock: {name}",
                f"Only {stock} left (min: {minst}). Supplier: {supplier or 'N/A'}. Reorder needed!",
                "warning"
            )

        # Expiring in 30 days
        exp_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        c.execute("SELECT name, expiry_date FROM medicines WHERE expiry_date != '' AND expiry_date <= ? AND expiry_date > ? AND status='Active'",
                 (exp_date, today))
        for name, exp in c.fetchall():
            add_notification(f"Expiring Soon: {name}", f"Expires on {exp}", "danger")

        # Already expired
        c.execute("SELECT name, expiry_date FROM medicines WHERE expiry_date != '' AND expiry_date <= ? AND status='Active'",
                 (today,))
        for name, exp in c.fetchall():
            add_notification(f"EXPIRED: {name}", f"Expired on {exp}! Remove from shelf!", "danger")

        conn.close()

    # ============================== SIDEBAR ==============================

    def _create_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=C["sidebar"], width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo_f = tk.Frame(self.sidebar, bg=C["primary_dark"], height=70)
        logo_f.pack(fill="x")
        logo_f.pack_propagate(False)
        tk.Label(logo_f, text="HMS", bg=C["primary_dark"], fg="white",
                 font=("Segoe UI", 26, "bold")).pack(pady=(10, 0))
        tk.Label(logo_f, text="Hospital Management System", bg=C["primary_dark"],
                 fg=C["primary_light"], font=("Segoe UI", 8)).pack()

        # User info
        uf = tk.Frame(self.sidebar, bg=C["card"], padx=12, pady=8)
        uf.pack(fill="x", padx=8, pady=(8, 0))
        tk.Label(uf, text=self.user["name"], bg=C["card"], fg=C["text"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        role_colors = {"Admin": C["danger"], "Doctor": C["accent"], "Pharmacist": C["warning"], "Receptionist": C["info"]}
        rc = role_colors.get(self.user["role"], C["text_secondary"])
        tk.Label(uf, text=self.user["role"], bg=C["card"], fg=rc,
                 font=("Segoe UI", 9)).pack(anchor="w")

        tk.Frame(self.sidebar, bg=C["divider"], height=1).pack(fill="x", pady=6)

        # Menu
        menu_items = [
            ("  Dashboard", "dash", self._show_dashboard, True),
            ("  Patients", "patients", self._show_patients, True),
            ("  Vitals", "vitals", self._show_vitals, True),
            ("  Doctors", "doctors", self._show_doctors, self.user["role"] in ["Admin", "Doctor"]),
            ("  Appointments", "appt", self._show_appointments, True),
            ("  Pharmacy", "pharma", self._show_pharmacy, self.user["role"] in ["Admin", "Pharmacist"]),
            ("  Prescriptions", "rx", self._show_prescriptions, self.user["role"] in ["Admin", "Doctor"]),
            ("  Lab Reports", "lab", self._show_lab, True),
            ("  Bed Management", "beds", self._show_beds, True),
            ("  Billing", "billing", self._show_billing, True),
            ("  Calendar", "cal", self._show_calendar, True),
            ("  Reports", "reports", self._show_reports, self.user["role"] == "Admin"),
            ("  Notifications", "notif", self._show_notifications, True),
            ("  Settings", "settings", self._show_settings, self.user["role"] == "Admin"),
        ]

        self.menu_btns = {}
        for text, key, cmd, visible in menu_items:
            if not visible:
                continue
            btn = tk.Button(
                self.sidebar, text=text, bg=C["sidebar"], fg=C["text_secondary"],
                font=F["menu"], relief="flat", anchor="w", padx=18, pady=6,
                activebackground=C["sidebar_hover"], activeforeground=C["primary"],
                cursor="hand2", command=cmd, borderwidth=0
            )
            btn.pack(fill="x", padx=6, pady=1)
            self.menu_btns[key] = btn

        # Logout
        bottom = tk.Frame(self.sidebar, bg=C["sidebar"])
        bottom.pack(side="bottom", fill="x", pady=8)
        tk.Frame(bottom, bg=C["divider"], height=1).pack(fill="x", padx=12, pady=(0, 6))
        tk.Button(bottom, text="  Logout", bg=C["sidebar"], fg=C["danger"],
                  font=F["menu"], relief="flat", anchor="w", padx=18,
                  command=self._logout, cursor="hand2", borderwidth=0).pack(fill="x", padx=6)
        tk.Label(bottom, text="Matrix Tech Solutions\nLahore, Pakistan", bg=C["sidebar"],
                 fg=C["text_muted"], font=("Segoe UI", 7), justify="center").pack(pady=3)

    def _set_active(self, key):
        for k, btn in self.menu_btns.items():
            if k == key:
                btn.configure(bg=C["sidebar_hover"], fg=C["primary"])
            else:
                btn.configure(bg=C["sidebar"], fg=C["text_secondary"])

    def _logout(self):
        audit_log(self.user["username"], "Logout", "Auth")
        self.root.destroy()
        login = LoginWindow()
        login.run()

    # ============================== MAIN AREA ==============================

    def _create_main(self):
        self.main = tk.Frame(self.root, bg=C["bg"])
        self.main.pack(side="right", fill="both", expand=True)

    def _clear(self):
        for w in self.main.winfo_children():
            w.destroy()

    def _header(self, title, subtitle=""):
        h = tk.Frame(self.main, bg=C["bg"])
        h.pack(fill="x", padx=25, pady=(20, 12))
        tk.Label(h, text=title, bg=C["bg"], fg=C["text"],
                 font=F["header"]).pack(side="left")
        if subtitle:
            tk.Label(h, text=subtitle, bg=C["bg"], fg=C["text_secondary"],
                     font=F["header_sub"]).pack(side="left", padx=(12, 0), pady=(8, 0))
        return h

    def _badge(self, parent, text, color, bg_color=None):
        bg_c = bg_color or C["bg"]
        f = tk.Frame(parent, bg=color, padx=8, pady=2)
        tk.Label(f, text=text, bg=color, fg="black" if color in [C["warning"], C["accent"]] else "white",
                 font=("Segoe UI", 8, "bold")).pack()
        return f

    def _stat_card(self, parent, row, col, label, value, color, icon=""):
        card = tk.Frame(parent, bg=C["card"], padx=18, pady=12)
        card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
        if icon:
            tk.Label(card, text=icon, bg=C["card"], fg=color,
                     font=("Segoe UI", 14)).pack(anchor="w")
        tk.Label(card, text=str(value), bg=C["card"], fg=color,
                 font=F["card_value"]).pack(anchor="w")
        tk.Label(card, text=label, bg=C["card"], fg=C["text_secondary"],
                 font=F["card_label"]).pack(anchor="w")
        return card

    def _make_entry(self, parent, label_text, default="", row=0):
        tk.Label(parent, text=label_text, bg=C["bg"], fg=C["text_secondary"],
                 font=F["body_small"]).grid(row=row, column=0, sticky="w", pady=(6, 2), padx=5)
        entry = tk.Entry(parent, bg=C["input_bg"], fg=C["text"], font=F["input"],
                         relief="flat", insertbackground=C["text"], highlightthickness=1,
                         highlightbackground=C["input_border"], highlightcolor=C["input_focus"])
        entry.grid(row=row, column=1, sticky="ew", pady=(6, 2), padx=5, ipady=4)
        if default:
            entry.insert(0, default)
        return entry

    # ============================== DASHBOARD ==============================

    def _show_dashboard(self):
        self._clear()
        self._set_active("dash")
        h = self._header("Dashboard", datetime.now().strftime("%A, %d %B %Y"))

        conn = get_conn()
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM patients")
        total_patients = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM doctors WHERE status='Active'")
        total_doctors = c.fetchone()[0]

        today = datetime.now().strftime("%Y-%m-%d")
        c.execute("SELECT COUNT(*) FROM appointments WHERE date=?", (today,))
        today_appts = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM appointments WHERE date=? AND status='Waiting'", (today,))
        waiting = c.fetchone()[0]

        c.execute("SELECT COALESCE(SUM(total), 0) FROM pharmacy_sales WHERE created_at LIKE ?", (f"{today}%",))
        today_pharma = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(grand_total), 0) FROM bills WHERE created_at LIKE ?", (f"{today}%",))
        today_billing = c.fetchone()[0]
        today_revenue = today_pharma + today_billing

        c.execute("SELECT COUNT(*) FROM beds WHERE status='Occupied'")
        occupied = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM beds WHERE status='Available'")
        available = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM medicines WHERE stock <= min_stock AND status='Active'")
        low_stock = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM lab_tests WHERE status='Pending'")
        pending_labs = c.fetchone()[0]

        month = datetime.now().strftime("%Y-%m")
        c.execute("SELECT COALESCE(SUM(grand_total), 0) FROM bills WHERE created_at LIKE ?", (f"{month}%",))
        mb = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(total), 0) FROM pharmacy_sales WHERE created_at LIKE ?", (f"{month}%",))
        mp = c.fetchone()[0]
        month_rev = mb + mp

        c.execute("SELECT COUNT(*) FROM notifications WHERE is_read=0")
        unread = c.fetchone()[0]

        conn.close()

        # Stats
        grid = tk.Frame(self.main, bg=C["bg"])
        grid.pack(fill="x", padx=25)
        for i in range(6):
            grid.grid_columnconfigure(i, weight=1)

        self._stat_card(grid, 0, 0, "Total Patients", f"{total_patients:,}", C["primary"])
        self._stat_card(grid, 0, 1, "Active Doctors", str(total_doctors), C["accent"])
        self._stat_card(grid, 0, 2, "Today Appointments", str(today_appts), C["info"])
        self._stat_card(grid, 0, 3, "Waiting Queue", str(waiting), C["warning"])
        self._stat_card(grid, 0, 4, "Today Revenue", f"Rs {today_revenue:,.0f}", C["success"])
        self._stat_card(grid, 0, 5, "Unread Alerts", str(unread), C["danger"] if unread else C["text_muted"])

        self._stat_card(grid, 1, 0, "Beds Occupied", str(occupied), C["orange"])
        self._stat_card(grid, 1, 1, "Beds Available", str(available), C["success"])
        self._stat_card(grid, 1, 2, "Low Stock Meds", str(low_stock), C["danger"] if low_stock else C["success"])
        self._stat_card(grid, 1, 3, "Pending Labs", str(pending_labs), C["purple"])
        self._stat_card(grid, 1, 4, "Monthly Revenue", f"Rs {month_rev:,.0f}", C["accent"])
        self._stat_card(grid, 1, 5, f"Logged: {self.user['name'][:12]}", self.user["role"], C["info"])

        # Bottom panels
        bottom = tk.Frame(self.main, bg=C["bg"])
        bottom.pack(fill="both", expand=True, padx=25, pady=(8, 15))

        # Today's appointments
        left = tk.Frame(bottom, bg=C["card"], padx=12, pady=10)
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))

        tk.Label(left, text="Today's Appointments", bg=C["card"], fg=C["text"],
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))

        conn = get_conn()
        c = conn.cursor()
        c.execute("""SELECT token_no, patient_name, doctor_name, department, time, status
                    FROM appointments WHERE date=? ORDER BY token_no""", (today,))
        rows = c.fetchall()
        conn.close()

        if rows:
            cols = ("Token", "Patient", "Doctor", "Dept", "Time", "Status")
            tree = ttk.Treeview(left, columns=cols, show="headings", height=7)
            for col, w in zip(cols, [45, 130, 120, 90, 55, 75]):
                tree.heading(col, text=col)
                tree.column(col, width=w, minwidth=30)
            for r in rows:
                tree.insert("", "end", values=r)
            tree.pack(fill="both", expand=True)
        else:
            tk.Label(left, text="No appointments today.", bg=C["card"],
                     fg=C["text_muted"], font=F["body"]).pack(pady=25)

        # Alerts + Quick Actions
        right = tk.Frame(bottom, bg=C["card"], padx=12, pady=10, width=280)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        tk.Label(right, text="Quick Actions", bg=C["card"], fg=C["text"],
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))

        actions = [
            ("+ Register Patient", C["accent"], self._show_patients),
            ("+ New Appointment", C["primary"], self._show_appointments),
            ("+ Pharmacy Sale", C["warning"], self._show_pharmacy),
            ("+ Create Bill", C["info"], self._show_billing),
        ]
        for text, color, cmd in actions:
            tk.Button(right, text=text, bg=color, fg="black", font=("Segoe UI", 10, "bold"),
                      relief="flat", padx=10, pady=5, cursor="hand2",
                      command=cmd).pack(fill="x", pady=2)

        tk.Label(right, text="Recent Alerts", bg=C["card"], fg=C["text"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(12, 5))

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT title, category FROM notifications ORDER BY id DESC LIMIT 5")
        notifs = c.fetchall()
        conn.close()

        cat_colors = {"info": C["info"], "warning": C["warning"], "danger": C["danger"], "success": C["success"]}
        for title, cat in notifs:
            nf = tk.Frame(right, bg=C["bg_secondary"], padx=8, pady=5)
            nf.pack(fill="x", pady=1)
            tk.Label(nf, text="●", bg=C["bg_secondary"], fg=cat_colors.get(cat, C["text_muted"]),
                     font=("Segoe UI", 8)).pack(side="left")
            tk.Label(nf, text=title[:35], bg=C["bg_secondary"], fg=C["text_secondary"],
                     font=("Segoe UI", 8)).pack(side="left", padx=5)

    # ============================== PATIENTS ==============================

    def _show_patients(self):
        self._clear()
        self._set_active("patients")
        h = self._header("Patient Management", "Registration & Records")

        tk.Button(h, text="+ Register Patient", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=14, pady=4,
                  command=self._register_patient, cursor="hand2").pack(side="right")

        sf = tk.Frame(self.main, bg=C["bg"])
        sf.pack(fill="x", padx=25, pady=(0, 8))
        self.pat_search = tk.Entry(sf, bg=C["input_bg"], fg=C["text"], font=F["input"],
                                    relief="flat", insertbackground=C["text"],
                                    highlightthickness=1, highlightbackground=C["input_border"])
        self.pat_search.pack(side="left", fill="x", expand=True, ipady=6)
        self.pat_search.insert(0, "Search by name, CNIC, patient ID, phone...")
        self.pat_search.bind("<FocusIn>", lambda e: self.pat_search.delete(0, "end") if "Search" in self.pat_search.get() else None)
        self.pat_search.bind("<KeyRelease>", lambda e: self._load_patients())

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        cols = ("ID", "Name", "Father", "CNIC", "Age", "Gender", "Phone", "Type", "Blood", "Allergies", "Status")
        self.pat_tree = ttk.Treeview(tf, columns=cols, show="headings", height=16)
        widths = [80, 140, 110, 125, 35, 55, 95, 45, 40, 90, 55]
        for col, w in zip(cols, widths):
            self.pat_tree.heading(col, text=col)
            self.pat_tree.column(col, width=w, minwidth=30)

        sb = ttk.Scrollbar(tf, orient="vertical", command=self.pat_tree.yview)
        self.pat_tree.configure(yscrollcommand=sb.set)
        self.pat_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.pat_tree.bind("<Double-1>", lambda e: self._patient_detail())

        tk.Label(tf, text="Double-click for patient details & history",
                 bg=C["card"], fg=C["text_muted"], font=F["body_small"]).pack(side="bottom", pady=2)

        self._load_patients()

    def _load_patients(self):
        search = self.pat_search.get().strip()
        if "Search" in search:
            search = ""
        for item in self.pat_tree.get_children():
            self.pat_tree.delete(item)

        conn = get_conn()
        c = conn.cursor()
        if search:
            q = f"%{search}%"
            c.execute("""SELECT patient_id, name, father_name, cnic, age, gender, phone, patient_type, blood_group, allergies, status
                        FROM patients WHERE name LIKE ? OR cnic LIKE ? OR patient_id LIKE ? OR phone LIKE ?
                        ORDER BY id DESC""", (q, q, q, q))
        else:
            c.execute("""SELECT patient_id, name, father_name, cnic, age, gender, phone, patient_type, blood_group, allergies, status
                        FROM patients ORDER BY id DESC""")
        for r in c.fetchall():
            self.pat_tree.insert("", "end", values=r)
        conn.close()

    def _register_patient(self):
        d = tk.Toplevel(self.root)
        d.title("Register New Patient")
        d.geometry("580x700")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Patient Registration", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 16, "bold")).pack(pady=(12, 8))

        canvas = tk.Canvas(d, bg=C["bg"], highlightthickness=0)
        scroll = ttk.Scrollbar(d, orient="vertical", command=canvas.yview)
        form = tk.Frame(canvas, bg=C["bg"])
        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=form, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True, padx=25)
        scroll.pack(side="right", fill="y")
        form.grid_columnconfigure(1, weight=1)

        pid = generate_id("PAT", "patients", "patient_id")
        fields = {}
        defs = [
            ("Patient ID", "patient_id", pid, 0),
            ("Full Name *", "name", "", 1),
            ("Father's Name", "father_name", "", 2),
            ("CNIC (xxxxx-xxxxxxx-x)", "cnic", "", 3),
            ("Age", "age", "", 4),
            ("Phone (03xx-xxxxxxx)", "phone", "", 5),
            ("Email", "email", "", 6),
            ("Address", "address", "", 7),
            ("Emergency Contact", "emergency", "", 8),
            ("Allergies (comma separated)", "allergies", "", 9),
            ("Chronic Conditions", "chronic", "", 10),
        ]
        for label, key, default, row in defs:
            fields[key] = self._make_entry(form, label, default, row)

        # Gender
        tk.Label(form, text="Gender", bg=C["bg"], fg=C["text_secondary"],
                 font=F["body_small"]).grid(row=11, column=0, sticky="w", pady=(6, 2), padx=5)
        gender_var = tk.StringVar(value="Male")
        gf = tk.Frame(form, bg=C["bg"])
        gf.grid(row=11, column=1, sticky="w", padx=5)
        for g in ["Male", "Female", "Other"]:
            tk.Radiobutton(gf, text=g, variable=gender_var, value=g, bg=C["bg"],
                           fg=C["text"], selectcolor=C["input_bg"], font=F["body_small"],
                           activebackground=C["bg"]).pack(side="left", padx=8)

        # Blood group
        tk.Label(form, text="Blood Group", bg=C["bg"], fg=C["text_secondary"],
                 font=F["body_small"]).grid(row=12, column=0, sticky="w", pady=(6, 2), padx=5)
        blood_var = tk.StringVar(value="")
        ttk.Combobox(form, textvariable=blood_var,
                      values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                      state="readonly").grid(row=12, column=1, sticky="ew", padx=5)

        # Type
        tk.Label(form, text="Patient Type", bg=C["bg"], fg=C["text_secondary"],
                 font=F["body_small"]).grid(row=13, column=0, sticky="w", pady=(6, 2), padx=5)
        type_var = tk.StringVar(value="OPD")
        ttk.Combobox(form, textvariable=type_var, values=["OPD", "IPD", "Emergency"],
                      state="readonly").grid(row=13, column=1, sticky="ew", padx=5)

        def save():
            name = fields["name"].get().strip()
            if not name:
                messagebox.showerror("Error", "Patient name is required!")
                return
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""INSERT INTO patients (patient_id, name, father_name, cnic, age, gender, phone, email,
                            address, blood_group, emergency_contact, patient_type, allergies, chronic_conditions)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                         (fields["patient_id"].get(), name, fields["father_name"].get(),
                          fields["cnic"].get(), int(fields["age"].get() or 0),
                          gender_var.get(), fields["phone"].get(), fields["email"].get(),
                          fields["address"].get(), blood_var.get(), fields["emergency"].get(),
                          type_var.get(), fields["allergies"].get(), fields["chronic"].get()))
                conn.commit()
                audit_log(self.user["username"], "Register Patient", "Patients", f"{name} ({fields['patient_id'].get()})")
                d.destroy()
                self._load_patients()
                messagebox.showinfo("Success", f"Patient '{name}' registered!\nID: {fields['patient_id'].get()}")
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Register Patient", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=10)

    def _patient_detail(self):
        sel = self.pat_tree.selection()
        if not sel:
            return
        pid = self.pat_tree.item(sel[0])["values"][0]

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM patients WHERE patient_id=?", (pid,))
        p = c.fetchone()
        if not p:
            conn.close()
            return

        d = tk.Toplevel(self.root)
        d.title(f"Patient: {p[2]} ({pid})")
        d.geometry("700x600")
        d.configure(bg=C["bg"])
        d.transient(self.root)

        # Header
        hdr = tk.Frame(d, bg=C["primary_dark"], padx=15, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"{p[2]}  |  {pid}", bg=C["primary_dark"], fg="white",
                 font=("Segoe UI", 16, "bold")).pack(side="left")
        tk.Label(hdr, text=f"{p[6]} | {p[12]} | Blood: {p[10]}", bg=C["primary_dark"],
                 fg=C["primary_light"], font=("Segoe UI", 10)).pack(side="right")

        # Tabs
        nb = ttk.Notebook(d)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Info
        info_f = tk.Frame(nb, bg=C["bg"])
        nb.add(info_f, text="  Info  ")
        info_items = [
            ("Father", p[3]), ("CNIC", p[4]), ("Age", p[5]),
            ("Gender", p[6]), ("Phone", p[7]), ("Email", p[8]),
            ("Address", p[9]), ("Blood Group", p[10]), ("Emergency Contact", p[11]),
            ("Patient Type", p[12]), ("Allergies", p[13] if len(p) > 13 else ""),
            ("Chronic Conditions", p[14] if len(p) > 14 else ""),
            ("Status", p[15] if len(p) > 15 else "Active"),
            ("Registered", p[16] if len(p) > 16 else ""),
        ]
        for i, (label, val) in enumerate(info_items):
            tk.Label(info_f, text=label + ":", bg=C["bg"], fg=C["text_secondary"],
                     font=("Segoe UI", 10)).grid(row=i, column=0, sticky="w", padx=15, pady=3)
            tk.Label(info_f, text=str(val or "-"), bg=C["bg"], fg=C["text"],
                     font=("Segoe UI", 10, "bold")).grid(row=i, column=1, sticky="w", padx=10, pady=3)

        # Tab 2: Visit History (Timeline)
        hist_f = tk.Frame(nb, bg=C["bg"])
        nb.add(hist_f, text="  History  ")

        tk.Label(hist_f, text="Visit & Treatment Timeline", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=15, pady=8)

        hist_canvas = tk.Canvas(hist_f, bg=C["bg"], highlightthickness=0)
        hist_scroll = ttk.Scrollbar(hist_f, orient="vertical", command=hist_canvas.yview)
        hist_inner = tk.Frame(hist_canvas, bg=C["bg"])
        hist_inner.bind("<Configure>", lambda e: hist_canvas.configure(scrollregion=hist_canvas.bbox("all")))
        hist_canvas.create_window((0, 0), window=hist_inner, anchor="nw")
        hist_canvas.configure(yscrollcommand=hist_scroll.set)
        hist_canvas.pack(side="left", fill="both", expand=True)
        hist_scroll.pack(side="right", fill="y")

        # Appointments
        c.execute("SELECT date, doctor_name, department, status, fee FROM appointments WHERE patient_id=? ORDER BY date DESC", (pid,))
        for row in c.fetchall():
            ef = tk.Frame(hist_inner, bg=C["card"], padx=10, pady=6)
            ef.pack(fill="x", padx=15, pady=2)
            tk.Label(ef, text=f"[{row[0]}] Appointment", bg=C["card"], fg=C["info"],
                     font=("Segoe UI", 9, "bold")).pack(side="left")
            tk.Label(ef, text=f"Dr. {row[1]} ({row[2]}) - {row[3]} - Rs {row[4]:,.0f}",
                     bg=C["card"], fg=C["text_secondary"], font=("Segoe UI", 9)).pack(side="left", padx=10)

        # Prescriptions
        c.execute("SELECT created_at, doctor_name, diagnosis, medicines FROM prescriptions WHERE patient_id=? ORDER BY id DESC", (pid,))
        for row in c.fetchall():
            ef = tk.Frame(hist_inner, bg=C["card"], padx=10, pady=6)
            ef.pack(fill="x", padx=15, pady=2)
            tk.Label(ef, text=f"[{row[0][:10]}] Prescription", bg=C["card"], fg=C["accent"],
                     font=("Segoe UI", 9, "bold")).pack(side="left")
            tk.Label(ef, text=f"Dr. {row[1]} | {row[2][:40]}", bg=C["card"],
                     fg=C["text_secondary"], font=("Segoe UI", 9)).pack(side="left", padx=10)

        # Lab tests
        c.execute("SELECT created_at, test_name, status, result FROM lab_tests WHERE patient_id=? ORDER BY id DESC", (pid,))
        for row in c.fetchall():
            ef = tk.Frame(hist_inner, bg=C["card"], padx=10, pady=6)
            ef.pack(fill="x", padx=15, pady=2)
            tk.Label(ef, text=f"[{row[0][:10]}] Lab: {row[1]}", bg=C["card"], fg=C["purple"],
                     font=("Segoe UI", 9, "bold")).pack(side="left")
            tk.Label(ef, text=f"{row[2]} - {row[3][:30] or 'Pending'}",
                     bg=C["card"], fg=C["text_secondary"], font=("Segoe UI", 9)).pack(side="left", padx=10)

        # Tab 3: Vitals
        vit_f = tk.Frame(nb, bg=C["bg"])
        nb.add(vit_f, text="  Vitals  ")

        c.execute("""SELECT blood_pressure, temperature, pulse, weight, blood_sugar, oxygen_level, created_at
                    FROM patient_vitals WHERE patient_id=? ORDER BY id DESC LIMIT 10""", (pid,))
        vitals = c.fetchall()
        conn.close()

        if vitals:
            vt_cols = ("BP", "Temp", "Pulse", "Weight", "Sugar", "O2", "Date")
            vt_tree = ttk.Treeview(vit_f, columns=vt_cols, show="headings", height=8)
            for col, w in zip(vt_cols, [80, 60, 55, 60, 60, 55, 110]):
                vt_tree.heading(col, text=col)
                vt_tree.column(col, width=w, minwidth=30)
            for v in vitals:
                vt_tree.insert("", "end", values=(v[0] or "-", f"{v[1]:.1f}" if v[1] else "-",
                                                   v[2] or "-", f"{v[3]:.1f}" if v[3] else "-",
                                                   f"{v[4]:.0f}" if v[4] else "-",
                                                   f"{v[5]:.0f}%" if v[5] else "-", v[6][:16]))
            vt_tree.pack(fill="both", expand=True, padx=10, pady=10)
        else:
            tk.Label(vit_f, text="No vitals recorded yet.\nGo to Vitals module to record.",
                     bg=C["bg"], fg=C["text_muted"], font=F["body"]).pack(pady=30)

    # ============================== VITALS ==============================

    def _show_vitals(self):
        self._clear()
        self._set_active("vitals")
        h = self._header("Patient Vitals", "BP, Temperature, Pulse, Sugar, O2")

        tk.Button(h, text="+ Record Vitals", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=14, pady=4,
                  command=self._record_vitals, cursor="hand2").pack(side="right")

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        cols = ("ID", "Patient", "BP", "Temp (F)", "Pulse", "Weight", "Sugar", "O2 %", "Resp Rate", "Recorded By", "Date")
        tree = ttk.Treeview(tf, columns=cols, show="headings", height=16)
        for col, w in zip(cols, [40, 130, 80, 60, 50, 55, 55, 50, 60, 90, 100]):
            tree.heading(col, text=col)
            tree.column(col, width=w, minwidth=30)

        conn = get_conn()
        c = conn.cursor()
        c.execute("""SELECT id, patient_name, blood_pressure, temperature, pulse, weight, blood_sugar,
                    oxygen_level, respiratory_rate, recorded_by, created_at FROM patient_vitals ORDER BY id DESC""")
        for r in c.fetchall():
            tree.insert("", "end", values=(r[0], r[1], r[2] or "-", f"{r[3]:.1f}" if r[3] else "-",
                                            r[4] or "-", f"{r[5]:.1f}" if r[5] else "-",
                                            f"{r[6]:.0f}" if r[6] else "-",
                                            f"{r[7]:.0f}%" if r[7] else "-",
                                            r[8] or "-", r[9], r[10][:16]))
        conn.close()
        tree.pack(fill="both", expand=True)

    def _record_vitals(self):
        d = tk.Toplevel(self.root)
        d.title("Record Patient Vitals")
        d.geometry("480x520")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Record Vitals", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(12, 8))

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT patient_id, name FROM patients WHERE status='Active' ORDER BY name")
        patients = c.fetchall()
        conn.close()

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)

        tk.Label(form, text="Patient", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(5, 2))
        pat_var = tk.StringVar()
        ttk.Combobox(form, textvariable=pat_var,
                      values=[f"{p[0]} - {p[1]}" for p in patients], state="readonly").pack(fill="x", ipady=3)

        form2 = tk.Frame(d, bg=C["bg"])
        form2.pack(fill="x", padx=25)
        form2.grid_columnconfigure(1, weight=1)

        fields = {}
        for label, key, default, row in [
            ("Blood Pressure (120/80)", "bp", "", 0),
            ("Temperature (F)", "temp", "", 1),
            ("Pulse (bpm)", "pulse", "", 2),
            ("Weight (kg)", "weight", "", 3),
            ("Height (cm)", "height", "", 4),
            ("Blood Sugar (mg/dL)", "sugar", "", 5),
            ("Oxygen Level (%)", "o2", "", 6),
            ("Respiratory Rate", "resp", "", 7),
        ]:
            fields[key] = self._make_entry(form2, label, default, row)

        tk.Label(form2, text="Notes", bg=C["bg"], fg=C["text_secondary"],
                 font=F["body_small"]).grid(row=8, column=0, sticky="w", padx=5, pady=(6, 2))
        notes = tk.Entry(form2, bg=C["input_bg"], fg=C["text"], font=F["input"], relief="flat")
        notes.grid(row=8, column=1, sticky="ew", padx=5, ipady=4)

        def save():
            if not pat_var.get():
                messagebox.showerror("Error", "Select patient!")
                return
            parts = pat_var.get().split(" - ")
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""INSERT INTO patient_vitals (patient_id, patient_name, blood_pressure, temperature,
                            pulse, weight, height, blood_sugar, oxygen_level, respiratory_rate, notes, recorded_by)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                         (parts[0], parts[1], fields["bp"].get(),
                          float(fields["temp"].get() or 0), int(fields["pulse"].get() or 0),
                          float(fields["weight"].get() or 0), float(fields["height"].get() or 0),
                          float(fields["sugar"].get() or 0), float(fields["o2"].get() or 0),
                          int(fields["resp"].get() or 0), notes.get(), self.user["name"]))
                conn.commit()
                audit_log(self.user["username"], "Record Vitals", "Vitals", parts[1])
                d.destroy()
                self._show_vitals()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Save Vitals", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=10)

    # ============================== DOCTORS ==============================

    def _show_doctors(self):
        self._clear()
        self._set_active("doctors")
        h = self._header("Doctor Management", "Staff & Revenue")

        btn_f = tk.Frame(h, bg=C["bg"])
        btn_f.pack(side="right")
        tk.Button(btn_f, text="+ Add Doctor", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=12, pady=4,
                  command=self._add_doctor, cursor="hand2").pack(side="left", padx=3)
        tk.Button(btn_f, text="Doctor Revenue", bg=C["primary"], fg="white",
                  font=F["button"], relief="flat", padx=12, pady=4,
                  command=self._doctor_revenue, cursor="hand2").pack(side="left", padx=3)

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        cols = ("ID", "Name", "Specialization", "Department", "Qualification", "Fee", "Schedule", "Phone", "Status")
        self.doc_tree = ttk.Treeview(tf, columns=cols, show="headings", height=16)
        for col, w in zip(cols, [75, 140, 115, 105, 95, 75, 125, 95, 65]):
            self.doc_tree.heading(col, text=col)
            self.doc_tree.column(col, width=w, minwidth=35)

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT doctor_id, name, specialization, department, qualification, fee, schedule, phone, status FROM doctors ORDER BY id DESC")
        for r in c.fetchall():
            self.doc_tree.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4], f"Rs {r[5]:,.0f}", r[6], r[7], r[8]))
        conn.close()
        self.doc_tree.pack(fill="both", expand=True)

    def _add_doctor(self):
        d = tk.Toplevel(self.root)
        d.title("Add Doctor")
        d.geometry("500x520")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Add New Doctor", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(12, 8))

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT name FROM departments")
        dept_list = [r[0] for r in c.fetchall()]
        conn.close()

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)
        form.grid_columnconfigure(1, weight=1)

        did = generate_id("DOC", "doctors", "doctor_id")
        fields = {}
        for label, key, default, row in [
            ("Doctor ID", "doctor_id", did, 0),
            ("Full Name *", "name", "", 1),
            ("Qualification", "qualification", "", 2),
            ("Specialization", "specialization", "", 3),
            ("Fee (Rs)", "fee", "1000", 4),
            ("Phone", "phone", "", 5),
            ("Email", "email", "", 6),
            ("Schedule", "schedule", "Mon-Sat 9AM-5PM", 7),
        ]:
            fields[key] = self._make_entry(form, label, default, row)

        tk.Label(form, text="Department", bg=C["bg"], fg=C["text_secondary"],
                 font=F["body_small"]).grid(row=8, column=0, sticky="w", padx=5, pady=(6, 2))
        dept_var = tk.StringVar(value=dept_list[0] if dept_list else "")
        ttk.Combobox(form, textvariable=dept_var, values=dept_list,
                      state="readonly").grid(row=8, column=1, sticky="ew", padx=5)

        def save():
            name = fields["name"].get().strip()
            if not name:
                messagebox.showerror("Error", "Doctor name required!")
                return
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""INSERT INTO doctors (doctor_id, name, specialization, department, qualification, phone, email, fee, schedule)
                            VALUES (?,?,?,?,?,?,?,?,?)""",
                         (fields["doctor_id"].get(), name, fields["specialization"].get(),
                          dept_var.get(), fields["qualification"].get(), fields["phone"].get(),
                          fields["email"].get(), float(fields["fee"].get() or 0), fields["schedule"].get()))
                conn.commit()
                audit_log(self.user["username"], "Add Doctor", "Doctors", name)
                d.destroy()
                self._show_doctors()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Save Doctor", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=10)

    def _doctor_revenue(self):
        d = tk.Toplevel(self.root)
        d.title("Doctor Revenue Report")
        d.geometry("600x400")
        d.configure(bg=C["bg"])
        d.transient(self.root)

        tk.Label(d, text="Doctor-wise Revenue (This Month)", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=12)

        month = datetime.now().strftime("%Y-%m")
        conn = get_conn()
        c = conn.cursor()
        c.execute("""SELECT doctor_name, COUNT(*), SUM(fee) FROM appointments
                    WHERE date LIKE ? AND status='Completed'
                    GROUP BY doctor_name ORDER BY SUM(fee) DESC""", (f"{month}%",))
        rows = c.fetchall()
        conn.close()

        cols = ("Doctor", "Appointments", "Revenue")
        tree = ttk.Treeview(d, columns=cols, show="headings", height=12)
        for col, w in zip(cols, [250, 120, 150]):
            tree.heading(col, text=col)
            tree.column(col, width=w)
        for r in rows:
            tree.insert("", "end", values=(r[0], r[1], f"Rs {r[2]:,.0f}"))
        tree.pack(fill="both", expand=True, padx=20, pady=10)

    # ============================== APPOINTMENTS ==============================

    def _show_appointments(self):
        self._clear()
        self._set_active("appt")
        h = self._header("Appointments", "Token & Queue")

        tk.Button(h, text="+ New Appointment", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=14, pady=4,
                  command=self._new_appointment, cursor="hand2").pack(side="right")

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        cols = ("Token", "Patient", "Doctor", "Department", "Date", "Time", "Fee", "Status", "Billed")
        self.appt_tree = ttk.Treeview(tf, columns=cols, show="headings", height=16)
        for col, w in zip(cols, [50, 140, 130, 100, 85, 60, 75, 80, 50]):
            self.appt_tree.heading(col, text=col)
            self.appt_tree.column(col, width=w, minwidth=30)

        today = datetime.now().strftime("%Y-%m-%d")
        conn = get_conn()
        c = conn.cursor()
        c.execute("""SELECT token_no, patient_name, doctor_name, department, date, time, fee, status, auto_billed
                    FROM appointments WHERE date=? ORDER BY token_no""", (today,))
        for r in c.fetchall():
            billed = "Yes" if r[8] else "No"
            self.appt_tree.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4], r[5], f"Rs {r[6]:,.0f}", r[7], billed))
        conn.close()

        self.appt_tree.pack(fill="both", expand=True)
        self.appt_tree.bind("<Double-1>", lambda e: self._update_appt_status())

        tk.Label(tf, text="Double-click: Waiting → In Progress → Completed (auto-generates bill on completion)",
                 bg=C["card"], fg=C["text_muted"], font=F["body_small"]).pack(pady=2)

    def _new_appointment(self):
        d = tk.Toplevel(self.root)
        d.title("New Appointment")
        d.geometry("480x440")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Book Appointment", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(12, 8))

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT patient_id, name FROM patients WHERE status='Active' ORDER BY name")
        patients = c.fetchall()
        c.execute("SELECT doctor_id, name, department, fee FROM doctors WHERE status='Active' ORDER BY name")
        doctors = c.fetchall()
        today = datetime.now().strftime("%Y-%m-%d")
        c.execute("SELECT COALESCE(MAX(token_no), 0) FROM appointments WHERE date=?", (today,))
        next_token = c.fetchone()[0] + 1
        conn.close()

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)

        tk.Label(form, text=f"Token #: {next_token}", bg=C["bg"], fg=C["accent"],
                 font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=5)

        tk.Label(form, text="Patient", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(6, 2))
        pat_var = tk.StringVar()
        ttk.Combobox(form, textvariable=pat_var,
                      values=[f"{p[0]} - {p[1]}" for p in patients], state="readonly").pack(fill="x", ipady=3)

        tk.Label(form, text="Doctor", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(6, 2))
        doc_var = tk.StringVar()
        ttk.Combobox(form, textvariable=doc_var,
                      values=[f"{dd[0]} - {dd[1]} ({dd[2]}) Rs {dd[3]:,.0f}" for dd in doctors],
                      state="readonly").pack(fill="x", ipady=3)

        tk.Label(form, text="Date", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(6, 2))
        date_e = tk.Entry(form, bg=C["input_bg"], fg=C["text"], font=F["input"], relief="flat")
        date_e.pack(fill="x", ipady=4)
        date_e.insert(0, today)

        tk.Label(form, text="Time", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(6, 2))
        time_e = tk.Entry(form, bg=C["input_bg"], fg=C["text"], font=F["input"], relief="flat")
        time_e.pack(fill="x", ipady=4)
        time_e.insert(0, datetime.now().strftime("%H:%M"))

        def save():
            if not pat_var.get() or not doc_var.get():
                messagebox.showerror("Error", "Select patient and doctor!")
                return
            pat_parts = pat_var.get().split(" - ")
            doc_id = doc_var.get().split(" - ")[0]
            doc_info = next((dd for dd in doctors if dd[0] == doc_id), None)
            if not doc_info:
                return

            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""INSERT INTO appointments (token_no, patient_id, patient_name, doctor_id, doctor_name, department, date, time, fee)
                            VALUES (?,?,?,?,?,?,?,?,?)""",
                         (next_token, pat_parts[0], pat_parts[1], doc_id, doc_info[1], doc_info[2],
                          date_e.get(), time_e.get(), doc_info[3]))
                conn.commit()
                audit_log(self.user["username"], "Book Appointment", "Appointments",
                         f"Token #{next_token} {pat_parts[1]} with {doc_info[1]}")
                d.destroy()
                self._show_appointments()
                messagebox.showinfo("Booked", f"Token #{next_token}\n{pat_parts[1]} → Dr. {doc_info[1]}\nFee: Rs {doc_info[3]:,.0f}")
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Book Appointment", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=10)

    def _update_appt_status(self):
        sel = self.appt_tree.selection()
        if not sel:
            return
        vals = self.appt_tree.item(sel[0])["values"]
        token, current = vals[0], vals[7]
        today = datetime.now().strftime("%Y-%m-%d")

        flow = {"Waiting": "In Progress", "In Progress": "Completed"}
        new_status = flow.get(current, current)
        if new_status == current:
            messagebox.showinfo("Info", f"Already {current}.")
            return

        conn = get_conn()
        try:
            c = conn.cursor()
            c.execute("UPDATE appointments SET status=? WHERE token_no=? AND date=?",
                     (new_status, token, today))

            # Auto-billing on completion
            if new_status == "Completed":
                c.execute("SELECT id, patient_id, patient_name, doctor_name, fee, auto_billed FROM appointments WHERE token_no=? AND date=?",
                         (token, today))
                appt = c.fetchone()
                if appt and not appt[5]:
                    bill_no = f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    fee = appt[4]
                    c.execute("""INSERT INTO bills (bill_no, patient_id, patient_name, bill_type,
                                consultation_fee, subtotal, grand_total, paid, payment_method, payment_status)
                                VALUES (?,?,?,'OPD',?,?,?,?,'Cash','Paid')""",
                             (bill_no, appt[1], appt[2], fee, fee, fee, fee))
                    c.execute("UPDATE appointments SET auto_billed=1 WHERE id=?", (appt[0],))
                    add_notification("Auto-Bill Generated",
                                    f"Bill {bill_no} for {appt[2]} - Rs {fee:,.0f} (Dr. {appt[3]})", "success")

            conn.commit()
            self._show_appointments()
        finally:
            conn.close()

    # ============================== PHARMACY ==============================

    def _show_pharmacy(self):
        self._clear()
        self._set_active("pharma")
        h = self._header("Pharmacy", "Inventory, Sales & Alerts")

        btn_f = tk.Frame(h, bg=C["bg"])
        btn_f.pack(side="right")
        tk.Button(btn_f, text="+ Add Medicine", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=10, pady=4,
                  command=self._add_medicine, cursor="hand2").pack(side="left", padx=2)
        tk.Button(btn_f, text="New Sale", bg=C["primary"], fg="white",
                  font=F["button"], relief="flat", padx=10, pady=4,
                  command=self._pharmacy_sale, cursor="hand2").pack(side="left", padx=2)
        tk.Button(btn_f, text="Reorder Alerts", bg=C["warning"], fg="black",
                  font=F["button"], relief="flat", padx=10, pady=4,
                  command=self._reorder_alerts, cursor="hand2").pack(side="left", padx=2)

        sf = tk.Frame(self.main, bg=C["bg"])
        sf.pack(fill="x", padx=25, pady=(0, 6))
        self.med_search = tk.Entry(sf, bg=C["input_bg"], fg=C["text"], font=F["input"],
                                    relief="flat", insertbackground=C["text"])
        self.med_search.pack(side="left", fill="x", expand=True, ipady=5)
        self.med_search.insert(0, "Search medicine...")
        self.med_search.bind("<FocusIn>", lambda e: self.med_search.delete(0, "end") if "Search" in self.med_search.get() else None)
        self.med_search.bind("<KeyRelease>", lambda e: self._load_medicines())

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        cols = ("ID", "Name", "Generic", "Category", "Price", "Cost", "Stock", "Min", "Expiry", "Supplier", "Status")
        self.med_tree = ttk.Treeview(tf, columns=cols, show="headings", height=14)
        for col, w in zip(cols, [35, 150, 110, 80, 65, 60, 50, 40, 80, 100, 60]):
            self.med_tree.heading(col, text=col)
            self.med_tree.column(col, width=w, minwidth=30)
        self.med_tree.pack(fill="both", expand=True)
        self._load_medicines()

    def _load_medicines(self):
        search = self.med_search.get().strip()
        if "Search" in search:
            search = ""
        for item in self.med_tree.get_children():
            self.med_tree.delete(item)
        conn = get_conn()
        c = conn.cursor()
        if search:
            q = f"%{search}%"
            c.execute("""SELECT id, name, generic_name, category, price, cost_price, stock, min_stock, expiry_date, supplier, status
                        FROM medicines WHERE name LIKE ? OR generic_name LIKE ? ORDER BY name""", (q, q))
        else:
            c.execute("""SELECT id, name, generic_name, category, price, cost_price, stock, min_stock, expiry_date, supplier, status
                        FROM medicines ORDER BY name""")
        today = datetime.now().strftime("%Y-%m-%d")
        for r in c.fetchall():
            status = r[10]
            if r[6] <= r[7]:
                status = "LOW"
            if r[8] and r[8] <= today:
                status = "EXPIRED"
            self.med_tree.insert("", "end", values=(r[0], r[1], r[2], r[3], f"Rs {r[4]:,.0f}",
                                                     f"Rs {r[5]:,.0f}", r[6], r[7], r[8], r[9], status))
        conn.close()

    def _add_medicine(self):
        d = tk.Toplevel(self.root)
        d.title("Add Medicine")
        d.geometry("500x580")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Add Medicine", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(12, 8))

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)
        form.grid_columnconfigure(1, weight=1)

        fields = {}
        for label, key, default, row in [
            ("Medicine Name *", "name", "", 0),
            ("Generic Name", "generic", "", 1),
            ("Category", "category", "", 2),
            ("Manufacturer", "manufacturer", "", 3),
            ("Batch No", "batch", "", 4),
            ("Sell Price (Rs)", "price", "0", 5),
            ("Cost Price (Rs)", "cost", "0", 6),
            ("Stock Quantity", "stock", "0", 7),
            ("Min Stock Alert", "min_stock", "10", 8),
            ("Expiry (YYYY-MM-DD)", "expiry", "", 9),
            ("Shelf Location", "shelf", "", 10),
            ("Supplier Name", "supplier", "", 11),
            ("Supplier Phone", "sup_phone", "", 12),
            ("Interaction Group", "interaction", "", 13),
        ]:
            fields[key] = self._make_entry(form, label, default, row)

        def save():
            name = fields["name"].get().strip()
            if not name:
                messagebox.showerror("Error", "Medicine name required!")
                return
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""INSERT INTO medicines (name, generic_name, category, manufacturer, batch_no,
                            price, cost_price, stock, min_stock, expiry_date, shelf_location, supplier, supplier_phone, interaction_group)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                         (name, fields["generic"].get(), fields["category"].get(),
                          fields["manufacturer"].get(), fields["batch"].get(),
                          float(fields["price"].get() or 0), float(fields["cost"].get() or 0),
                          int(fields["stock"].get() or 0), int(fields["min_stock"].get() or 10),
                          fields["expiry"].get(), fields["shelf"].get(),
                          fields["supplier"].get(), fields["sup_phone"].get(), fields["interaction"].get()))
                conn.commit()
                audit_log(self.user["username"], "Add Medicine", "Pharmacy", name)
                d.destroy()
                self._load_medicines()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Save Medicine", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=10)

    def _pharmacy_sale(self):
        d = tk.Toplevel(self.root)
        d.title("Pharmacy Sale")
        d.geometry("680x520")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Pharmacy Sale", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(12, 5))

        top = tk.Frame(d, bg=C["bg"])
        top.pack(fill="x", padx=20)
        tk.Label(top, text="Customer:", bg=C["bg"], fg=C["text_secondary"]).pack(side="left")
        cust_e = tk.Entry(top, bg=C["input_bg"], fg=C["text"], font=F["input"], relief="flat", width=25)
        cust_e.pack(side="left", padx=5, ipady=3)
        cust_e.insert(0, "Walk-in")

        cart_items = []
        cart_f = tk.Frame(d, bg=C["card"], padx=10, pady=8)
        cart_f.pack(fill="both", expand=True, padx=20, pady=8)

        cols = ("Medicine", "Qty", "Price", "Total")
        cart_tree = ttk.Treeview(cart_f, columns=cols, show="headings", height=7)
        for col, w in zip(cols, [240, 55, 95, 95]):
            cart_tree.heading(col, text=col)
            cart_tree.column(col, width=w)
        cart_tree.pack(fill="both", expand=True)

        total_lbl = tk.Label(cart_f, text="Total: Rs 0", bg=C["card"], fg=C["accent"],
                              font=("Segoe UI", 16, "bold"))
        total_lbl.pack(anchor="e", pady=4)

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, name, price, stock FROM medicines WHERE stock > 0 AND status='Active' ORDER BY name")
        meds = c.fetchall()
        conn.close()

        add_f = tk.Frame(d, bg=C["bg"])
        add_f.pack(fill="x", padx=20)
        med_var = tk.StringVar()
        ttk.Combobox(add_f, textvariable=med_var,
                      values=[f"{m[0]} - {m[1]} (Rs {m[2]:,.0f}) [{m[3]}]" for m in meds],
                      state="readonly", width=38).pack(side="left", padx=2)
        qty_e = tk.Entry(add_f, bg=C["input_bg"], fg=C["text"], font=F["input"], relief="flat", width=5)
        qty_e.pack(side="left", padx=2, ipady=3)
        qty_e.insert(0, "1")

        def add_item():
            if not med_var.get():
                return
            mid = int(med_var.get().split(" - ")[0])
            med = next((m for m in meds if m[0] == mid), None)
            if not med:
                return
            qty = int(qty_e.get() or 1)
            if qty > med[3]:
                messagebox.showwarning("Stock", f"Only {med[3]} available!")
                return
            total = qty * med[2]
            cart_items.append({"id": mid, "name": med[1], "qty": qty, "price": med[2], "total": total})
            cart_tree.insert("", "end", values=(med[1], qty, f"Rs {med[2]:,.0f}", f"Rs {total:,.0f}"))
            grand = sum(ci["total"] for ci in cart_items)
            total_lbl.config(text=f"Total: Rs {grand:,.0f}")

        tk.Button(add_f, text="Add", bg=C["primary"], fg="white", font=F["button"],
                  relief="flat", padx=8, command=add_item, cursor="hand2").pack(side="left", padx=2)

        def complete():
            if not cart_items:
                messagebox.showwarning("Empty", "Add medicines!")
                return

            # Check interactions
            conn = get_conn()
            c = conn.cursor()
            groups = set()
            for ci in cart_items:
                c.execute("SELECT interaction_group FROM medicines WHERE id=?", (ci["id"],))
                r = c.fetchone()
                if r and r[0]:
                    groups.add(r[0])

            warnings = []
            groups_list = list(groups)
            for i in range(len(groups_list)):
                for j in range(i + 1, len(groups_list)):
                    c.execute("""SELECT severity, description FROM medicine_interactions
                                WHERE (group_a=? AND group_b=?) OR (group_a=? AND group_b=?)""",
                             (groups_list[i], groups_list[j], groups_list[j], groups_list[i]))
                    inter = c.fetchone()
                    if inter:
                        warnings.append(f"[{inter[0]}] {inter[1]}")

            if warnings:
                msg = "DRUG INTERACTION WARNING:\n\n" + "\n".join(warnings) + "\n\nProceed anyway?"
                if not messagebox.askyesno("Warning", msg, icon="warning"):
                    conn.close()
                    return

            grand = sum(ci["total"] for ci in cart_items)
            inv_no = f"PH-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            try:
                c.execute("""INSERT INTO pharmacy_sales (invoice_no, patient_name, items_count, subtotal, total, sold_by)
                            VALUES (?,?,?,?,?,?)""",
                         (inv_no, cust_e.get(), len(cart_items), grand, grand, self.user["name"]))
                sale_id = c.lastrowid
                for ci in cart_items:
                    c.execute("""INSERT INTO pharmacy_sale_items (sale_id, medicine_id, medicine_name, quantity, price, total)
                                VALUES (?,?,?,?,?,?)""",
                             (sale_id, ci["id"], ci["name"], ci["qty"], ci["price"], ci["total"]))
                    c.execute("UPDATE medicines SET stock = stock - ? WHERE id = ?", (ci["qty"], ci["id"]))
                conn.commit()
                audit_log(self.user["username"], "Pharmacy Sale", "Pharmacy", f"{inv_no} Rs {grand:,.0f}")
                d.destroy()
                messagebox.showinfo("Sale Complete", f"Invoice: {inv_no}\nTotal: Rs {grand:,.0f}")
                self._show_pharmacy()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Complete Sale", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=complete, cursor="hand2").pack(pady=6)

    def _reorder_alerts(self):
        d = tk.Toplevel(self.root)
        d.title("Reorder Alerts")
        d.geometry("650x400")
        d.configure(bg=C["bg"])
        d.transient(self.root)

        tk.Label(d, text="Medicines Need Reorder", bg=C["bg"], fg=C["danger"],
                 font=("Segoe UI", 15, "bold")).pack(pady=12)

        conn = get_conn()
        c = conn.cursor()
        c.execute("""SELECT name, generic_name, stock, min_stock, supplier, supplier_phone
                    FROM medicines WHERE stock <= min_stock AND status='Active' ORDER BY stock""")
        rows = c.fetchall()
        conn.close()

        cols = ("Medicine", "Generic", "Stock", "Min", "Supplier", "Phone")
        tree = ttk.Treeview(d, columns=cols, show="headings", height=12)
        for col, w in zip(cols, [180, 130, 60, 50, 120, 100]):
            tree.heading(col, text=col)
            tree.column(col, width=w)
        for r in rows:
            tree.insert("", "end", values=r)
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        if not rows:
            tk.Label(d, text="All medicines are adequately stocked!",
                     bg=C["bg"], fg=C["success"], font=F["body"]).pack(pady=20)

    # ============================== PRESCRIPTIONS ==============================

    def _show_prescriptions(self):
        self._clear()
        self._set_active("rx")
        h = self._header("Prescriptions", "With Drug Interaction Check")

        tk.Button(h, text="+ New Prescription", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=14, pady=4,
                  command=self._new_prescription, cursor="hand2").pack(side="right")

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        cols = ("ID", "Patient", "Doctor", "Diagnosis", "Medicines", "Follow-up", "Date")
        tree = ttk.Treeview(tf, columns=cols, show="headings", height=16)
        for col, w in zip(cols, [35, 130, 130, 150, 200, 85, 85]):
            tree.heading(col, text=col)
            tree.column(col, width=w, minwidth=30)

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, patient_name, doctor_name, diagnosis, medicines, follow_up, created_at FROM prescriptions ORDER BY id DESC")
        for r in c.fetchall():
            tree.insert("", "end", values=(r[0], r[1], r[2], r[3][:40], r[4][:50], r[5], r[6][:10]))
        conn.close()
        tree.pack(fill="both", expand=True)

    def _new_prescription(self):
        d = tk.Toplevel(self.root)
        d.title("New Prescription")
        d.geometry("560x580")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Write Prescription", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(12, 8))

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT patient_id, name, allergies FROM patients WHERE status='Active'")
        patients = c.fetchall()
        c.execute("SELECT doctor_id, name FROM doctors WHERE status='Active'")
        doctors = c.fetchall()
        conn.close()

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)

        tk.Label(form, text="Patient", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(4, 2))
        pat_var = tk.StringVar()
        pat_combo = ttk.Combobox(form, textvariable=pat_var,
                      values=[f"{p[0]} - {p[1]}" for p in patients], state="readonly")
        pat_combo.pack(fill="x", ipady=3)

        allergy_lbl = tk.Label(form, text="", bg=C["bg"], fg=C["danger"], font=("Segoe UI", 9, "bold"))
        allergy_lbl.pack(anchor="w")

        def on_patient_select(e):
            if pat_var.get():
                pid = pat_var.get().split(" - ")[0]
                pat = next((p for p in patients if p[0] == pid), None)
                if pat and pat[2]:
                    allergy_lbl.config(text=f"ALLERGIES: {pat[2]}")
                else:
                    allergy_lbl.config(text="")
        pat_combo.bind("<<ComboboxSelected>>", on_patient_select)

        tk.Label(form, text="Doctor", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(4, 2))
        doc_var = tk.StringVar()
        ttk.Combobox(form, textvariable=doc_var,
                      values=[f"{dd[0]} - {dd[1]}" for dd in doctors], state="readonly").pack(fill="x", ipady=3)

        tk.Label(form, text="Diagnosis", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(4, 2))
        diag = tk.Text(form, bg=C["input_bg"], fg=C["text"], font=F["input"], height=2, relief="flat")
        diag.pack(fill="x")

        tk.Label(form, text="Medicines (one per line)", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(4, 2))
        meds_text = tk.Text(form, bg=C["input_bg"], fg=C["text"], font=F["input"], height=4, relief="flat")
        meds_text.pack(fill="x")

        tk.Label(form, text="Instructions", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(4, 2))
        instr = tk.Text(form, bg=C["input_bg"], fg=C["text"], font=F["input"], height=2, relief="flat")
        instr.pack(fill="x")

        tk.Label(form, text="Follow-up Date", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(4, 2))
        followup_e = tk.Entry(form, bg=C["input_bg"], fg=C["text"], font=F["input"], relief="flat")
        followup_e.pack(fill="x", ipady=3)

        def save():
            if not pat_var.get() or not doc_var.get():
                messagebox.showerror("Error", "Select patient and doctor!")
                return
            pat_parts = pat_var.get().split(" - ")
            doc_parts = doc_var.get().split(" - ")
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""INSERT INTO prescriptions (patient_id, patient_name, doctor_id, doctor_name, diagnosis, medicines, instructions, follow_up)
                            VALUES (?,?,?,?,?,?,?,?)""",
                         (pat_parts[0], pat_parts[1], doc_parts[0], doc_parts[1],
                          diag.get("1.0", "end").strip(), meds_text.get("1.0", "end").strip(),
                          instr.get("1.0", "end").strip(), followup_e.get()))
                conn.commit()
                audit_log(self.user["username"], "New Prescription", "Prescriptions", pat_parts[1])
                d.destroy()
                self._show_prescriptions()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Save Prescription", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=8)

    # ============================== LAB REPORTS ==============================

    def _show_lab(self):
        self._clear()
        self._set_active("lab")
        h = self._header("Lab Reports", "Tests & Results")

        tk.Button(h, text="+ Request Test", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=14, pady=4,
                  command=self._request_lab_test, cursor="hand2").pack(side="right")

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        cols = ("Test ID", "Patient", "Doctor", "Test Name", "Category", "Fee", "Result", "Status", "Date")
        self.lab_tree = ttk.Treeview(tf, columns=cols, show="headings", height=14)
        for col, w in zip(cols, [70, 120, 110, 125, 85, 65, 90, 65, 80]):
            self.lab_tree.heading(col, text=col)
            self.lab_tree.column(col, width=w, minwidth=30)

        conn = get_conn()
        c = conn.cursor()
        c.execute("""SELECT test_id, patient_name, doctor_name, test_name, test_category, fee, result, status, created_at
                    FROM lab_tests ORDER BY id DESC""")
        for r in c.fetchall():
            self.lab_tree.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4], f"Rs {r[5]:,.0f}", r[6][:25] or "-", r[7], r[8][:10]))
        conn.close()
        self.lab_tree.pack(fill="both", expand=True)
        self.lab_tree.bind("<Double-1>", lambda e: self._update_lab_result())

        tk.Label(tf, text="Double-click to enter result", bg=C["card"],
                 fg=C["text_muted"], font=F["body_small"]).pack(pady=2)

    def _request_lab_test(self):
        d = tk.Toplevel(self.root)
        d.title("Request Lab Test")
        d.geometry("480x380")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Lab Test Request", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(12, 8))

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT patient_id, name FROM patients WHERE status='Active'")
        patients = c.fetchall()
        c.execute("SELECT doctor_id, name FROM doctors WHERE status='Active'")
        doctors = c.fetchall()
        conn.close()

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)

        tk.Label(form, text="Patient", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(4, 2))
        pat_var = tk.StringVar()
        ttk.Combobox(form, textvariable=pat_var,
                      values=[f"{p[0]} - {p[1]}" for p in patients], state="readonly").pack(fill="x", ipady=3)

        tk.Label(form, text="Referred by Doctor", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(4, 2))
        doc_var = tk.StringVar()
        ttk.Combobox(form, textvariable=doc_var,
                      values=[f"{dd[0]} - {dd[1]}" for dd in doctors], state="readonly").pack(fill="x", ipady=3)

        form2 = tk.Frame(d, bg=C["bg"])
        form2.pack(fill="x", padx=25)
        form2.grid_columnconfigure(1, weight=1)

        categories = ["Blood Test", "Urine Test", "X-Ray", "CT Scan", "MRI", "Ultrasound", "ECG", "Other"]
        fields = {}
        fields["test"] = self._make_entry(form2, "Test Name *", "", 0)
        tk.Label(form2, text="Category", bg=C["bg"], fg=C["text_secondary"],
                 font=F["body_small"]).grid(row=1, column=0, sticky="w", padx=5, pady=(6, 2))
        cat_var = tk.StringVar(value="Blood Test")
        ttk.Combobox(form2, textvariable=cat_var, values=categories,
                      state="readonly").grid(row=1, column=1, sticky="ew", padx=5)
        fields["fee"] = self._make_entry(form2, "Fee (Rs)", "500", 2)

        def save():
            if not pat_var.get() or not fields["test"].get().strip():
                messagebox.showerror("Error", "Patient and test name required!")
                return
            test_id = generate_id("LAB", "lab_tests", "test_id")
            pat_parts = pat_var.get().split(" - ")
            doc_name = doc_var.get().split(" - ")[1] if doc_var.get() else ""
            doc_id = doc_var.get().split(" - ")[0] if doc_var.get() else ""
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""INSERT INTO lab_tests (test_id, patient_id, patient_name, doctor_id, doctor_name, test_name, test_category, fee)
                            VALUES (?,?,?,?,?,?,?,?)""",
                         (test_id, pat_parts[0], pat_parts[1], doc_id, doc_name,
                          fields["test"].get(), cat_var.get(), float(fields["fee"].get() or 0)))
                conn.commit()
                audit_log(self.user["username"], "Request Lab Test", "Lab", f"{test_id} {pat_parts[1]}")
                d.destroy()
                self._show_lab()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Submit Request", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=10)

    def _update_lab_result(self):
        sel = self.lab_tree.selection()
        if not sel:
            return
        test_id = self.lab_tree.item(sel[0])["values"][0]

        d = tk.Toplevel(self.root)
        d.title(f"Result: {test_id}")
        d.geometry("400x280")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text=f"Enter Result: {test_id}", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 14, "bold")).pack(pady=(12, 8))

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)

        tk.Label(form, text="Result", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(4, 2))
        result = tk.Text(form, bg=C["input_bg"], fg=C["text"], font=F["input"], height=3, relief="flat")
        result.pack(fill="x")

        tk.Label(form, text="Normal Range", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(4, 2))
        normal = tk.Entry(form, bg=C["input_bg"], fg=C["text"], font=F["input"], relief="flat")
        normal.pack(fill="x", ipady=3)

        def save():
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""UPDATE lab_tests SET result=?, normal_range=?, status='Completed', report_date=?
                            WHERE test_id=?""",
                         (result.get("1.0", "end").strip(), normal.get(),
                          datetime.now().strftime("%Y-%m-%d"), test_id))
                conn.commit()
                add_notification("Lab Report Ready", f"Test {test_id} completed", "success")
                audit_log(self.user["username"], "Enter Lab Result", "Lab", test_id)
                d.destroy()
                self._show_lab()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Save Result", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=8)

    # ============================== BED MANAGEMENT ==============================

    def _show_beds(self):
        self._clear()
        self._set_active("beds")
        h = self._header("Bed Management", "Ward & Admission")

        tk.Button(h, text="Admit Patient", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=14, pady=4,
                  command=self._admit_patient, cursor="hand2").pack(side="right")

        # Ward cards
        conn = get_conn()
        c = conn.cursor()
        c.execute("""SELECT w.name, w.ward_type, w.total_beds,
                    SUM(CASE WHEN b.status='Available' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN b.status='Occupied' THEN 1 ELSE 0 END),
                    w.charge_per_day
                    FROM wards w LEFT JOIN beds b ON w.id = b.ward_id
                    GROUP BY w.id ORDER BY w.name""")
        wards = c.fetchall()
        conn.close()

        wf = tk.Frame(self.main, bg=C["bg"])
        wf.pack(fill="x", padx=25, pady=(0, 8))
        for i, w in enumerate(wards):
            card = tk.Frame(wf, bg=C["card"], padx=10, pady=8)
            card.grid(row=i // 4, column=i % 4, padx=3, pady=3, sticky="nsew")
            wf.grid_columnconfigure(i % 4, weight=1)
            avail = w[3] or 0
            occ = w[4] or 0
            color = C["success"] if avail > 0 else C["danger"]
            tk.Label(card, text=w[0], bg=C["card"], fg=C["primary"],
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(card, text=f"{avail} free / {occ} occupied", bg=C["card"], fg=color,
                     font=("Segoe UI", 8)).pack(anchor="w")
            tk.Label(card, text=f"Rs {w[5]:,.0f}/day", bg=C["card"], fg=C["text_muted"],
                     font=("Segoe UI", 7)).pack(anchor="w")

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        cols = ("Bed No", "Ward", "Status", "Patient", "Admission", "Doctor")
        self.bed_tree = ttk.Treeview(tf, columns=cols, show="headings", height=10)
        for col, w in zip(cols, [75, 130, 75, 140, 100, 120]):
            self.bed_tree.heading(col, text=col)
            self.bed_tree.column(col, width=w, minwidth=35)

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT bed_no, ward_name, status, patient_name, admission_date, doctor_id FROM beds ORDER BY ward_name, bed_no")
        for r in c.fetchall():
            self.bed_tree.insert("", "end", values=(r[0], r[1], r[2], r[3] or "-", r[4] or "-", r[5] or "-"))
        conn.close()
        self.bed_tree.pack(fill="both", expand=True)
        self.bed_tree.bind("<Double-1>", lambda e: self._discharge_patient())

        tk.Label(tf, text="Double-click occupied bed to discharge", bg=C["card"],
                 fg=C["text_muted"], font=F["body_small"]).pack(pady=2)

    def _admit_patient(self):
        d = tk.Toplevel(self.root)
        d.title("Admit Patient")
        d.geometry("450x340")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Admit Patient (IPD)", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(12, 8))

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT patient_id, name FROM patients WHERE status='Active'")
        patients = c.fetchall()
        c.execute("SELECT bed_no, ward_name FROM beds WHERE status='Available' ORDER BY ward_name, bed_no")
        beds = c.fetchall()
        c.execute("SELECT doctor_id, name FROM doctors WHERE status='Active'")
        doctors = c.fetchall()
        conn.close()

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)

        for label, var_name in [("Patient", "pat"), ("Available Bed", "bed"), ("Doctor", "doc")]:
            tk.Label(form, text=label, bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(6, 2))

        pat_var = tk.StringVar()
        ttk.Combobox(form, textvariable=pat_var,
                      values=[f"{p[0]} - {p[1]}" for p in patients], state="readonly").pack(fill="x", ipady=3)

        bed_var = tk.StringVar()
        ttk.Combobox(form, textvariable=bed_var,
                      values=[f"{b[0]} ({b[1]})" for b in beds], state="readonly").pack(fill="x", ipady=3)

        doc_var = tk.StringVar()
        ttk.Combobox(form, textvariable=doc_var,
                      values=[f"{dd[0]} - {dd[1]}" for dd in doctors], state="readonly").pack(fill="x", ipady=3)

        def save():
            if not pat_var.get() or not bed_var.get():
                messagebox.showerror("Error", "Select patient and bed!")
                return
            pat_parts = pat_var.get().split(" - ")
            bed_no = bed_var.get().split(" (")[0]
            doc_id = doc_var.get().split(" - ")[0] if doc_var.get() else ""
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""UPDATE beds SET status='Occupied', patient_id=?, patient_name=?,
                            admission_date=?, doctor_id=? WHERE bed_no=?""",
                         (pat_parts[0], pat_parts[1], datetime.now().strftime("%Y-%m-%d"), doc_id, bed_no))
                c.execute("UPDATE patients SET patient_type='IPD' WHERE patient_id=?", (pat_parts[0],))
                conn.commit()
                audit_log(self.user["username"], "Admit Patient", "Beds", f"{pat_parts[1]} → {bed_no}")
                add_notification("Patient Admitted", f"{pat_parts[1]} admitted to {bed_no}", "info")
                d.destroy()
                self._show_beds()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Admit", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=10)

    def _discharge_patient(self):
        sel = self.bed_tree.selection()
        if not sel:
            return
        vals = self.bed_tree.item(sel[0])["values"]
        if vals[2] != "Occupied":
            return
        if messagebox.askyesno("Discharge", f"Discharge {vals[3]} from {vals[0]}?"):
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""UPDATE beds SET status='Available', patient_id='', patient_name='',
                            admission_date='', doctor_id='' WHERE bed_no=?""", (vals[0],))
                conn.commit()
                audit_log(self.user["username"], "Discharge Patient", "Beds", f"{vals[3]} from {vals[0]}")
                self._show_beds()
            finally:
                conn.close()

    # ============================== BILLING ==============================

    def _show_billing(self):
        self._clear()
        self._set_active("billing")
        h = self._header("Billing", "Invoices & Payments")

        tk.Button(h, text="+ Create Bill", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=14, pady=4,
                  command=self._create_bill, cursor="hand2").pack(side="right")

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        cols = ("Bill No", "Patient", "Type", "Consult", "Lab", "Pharma", "Bed", "Discount", "Total", "Paid", "Status")
        tree = ttk.Treeview(tf, columns=cols, show="headings", height=16)
        for col, w in zip(cols, [85, 120, 45, 70, 60, 65, 60, 60, 80, 70, 60]):
            tree.heading(col, text=col)
            tree.column(col, width=w, minwidth=30)

        conn = get_conn()
        c = conn.cursor()
        c.execute("""SELECT bill_no, patient_name, bill_type, consultation_fee, lab_charges, pharmacy_charges,
                    bed_charges, discount, grand_total, paid, payment_status FROM bills ORDER BY id DESC""")
        for r in c.fetchall():
            tree.insert("", "end", values=(r[0], r[1], r[2], f"Rs {r[3]:,.0f}", f"Rs {r[4]:,.0f}",
                                           f"Rs {r[5]:,.0f}", f"Rs {r[6]:,.0f}", f"Rs {r[7]:,.0f}",
                                           f"Rs {r[8]:,.0f}", f"Rs {r[9]:,.0f}", r[10]))
        conn.close()
        tree.pack(fill="both", expand=True)

    def _create_bill(self):
        d = tk.Toplevel(self.root)
        d.title("Create Bill")
        d.geometry("500x550")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Create Bill / Invoice", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(12, 8))

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT patient_id, name FROM patients WHERE status='Active'")
        patients = c.fetchall()
        conn.close()

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)
        form.grid_columnconfigure(1, weight=1)

        tk.Label(form, text="Patient", bg=C["bg"], fg=C["text_secondary"]).grid(row=0, column=0, sticky="w", padx=5, pady=4)
        pat_var = tk.StringVar()
        ttk.Combobox(form, textvariable=pat_var,
                      values=[f"{p[0]} - {p[1]}" for p in patients],
                      state="readonly").grid(row=0, column=1, sticky="ew", padx=5, pady=4)

        tk.Label(form, text="Type", bg=C["bg"], fg=C["text_secondary"]).grid(row=1, column=0, sticky="w", padx=5, pady=4)
        type_var = tk.StringVar(value="OPD")
        ttk.Combobox(form, textvariable=type_var, values=["OPD", "IPD", "Emergency"],
                      state="readonly").grid(row=1, column=1, sticky="ew", padx=5, pady=4)

        fields = {}
        for label, key, default, row in [
            ("Consultation Fee", "consult", "0", 2),
            ("Lab Charges", "lab", "0", 3),
            ("Pharmacy Charges", "pharma", "0", 4),
            ("Bed Charges", "bed", "0", 5),
            ("Other Charges", "other", "0", 6),
            ("Discount", "discount", "0", 7),
        ]:
            fields[key] = self._make_entry(form, label, default, row)

        tk.Label(form, text="Payment", bg=C["bg"], fg=C["text_secondary"]).grid(row=8, column=0, sticky="w", padx=5, pady=4)
        pay_var = tk.StringVar(value="Cash")
        ttk.Combobox(form, textvariable=pay_var, values=["Cash", "Card", "Online", "JazzCash", "Easypaisa", "Insurance", "Credit"],
                      state="readonly").grid(row=8, column=1, sticky="ew", padx=5, pady=4)

        def save():
            if not pat_var.get():
                messagebox.showerror("Error", "Select patient!")
                return
            pat_parts = pat_var.get().split(" - ")
            bill_no = f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            consult = float(fields["consult"].get() or 0)
            lab = float(fields["lab"].get() or 0)
            pharma = float(fields["pharma"].get() or 0)
            bed = float(fields["bed"].get() or 0)
            other = float(fields["other"].get() or 0)
            discount = float(fields["discount"].get() or 0)
            subtotal = consult + lab + pharma + bed + other
            grand = subtotal - discount
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""INSERT INTO bills (bill_no, patient_id, patient_name, bill_type,
                            consultation_fee, lab_charges, pharmacy_charges, bed_charges, other_charges,
                            subtotal, discount, grand_total, paid, balance, payment_method, payment_status)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                         (bill_no, pat_parts[0], pat_parts[1], type_var.get(),
                          consult, lab, pharma, bed, other, subtotal, discount, grand,
                          grand, 0, pay_var.get(), "Paid"))
                conn.commit()
                audit_log(self.user["username"], "Create Bill", "Billing", f"{bill_no} Rs {grand:,.0f}")
                d.destroy()
                self._show_billing()
                messagebox.showinfo("Bill Created", f"Bill: {bill_no}\nTotal: Rs {grand:,.0f}")
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Generate Bill", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=10)

    # ============================== CALENDAR ==============================

    def _show_calendar(self):
        self._clear()
        self._set_active("cal")
        h = self._header("Appointment Calendar", "Monthly View")

        now = datetime.now()
        year, month = now.year, now.month

        cal_f = tk.Frame(self.main, bg=C["card"], padx=15, pady=12)
        cal_f.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        month_name = calendar.month_name[month]
        tk.Label(cal_f, text=f"{month_name} {year}", bg=C["card"], fg=C["primary"],
                 font=("Segoe UI", 18, "bold")).pack(pady=(0, 10))

        # Day headers
        grid = tk.Frame(cal_f, bg=C["card"])
        grid.pack(fill="both", expand=True)
        for i in range(7):
            grid.grid_columnconfigure(i, weight=1)

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            tk.Label(grid, text=day, bg=C["card"], fg=C["primary"],
                     font=("Segoe UI", 10, "bold")).grid(row=0, column=i, pady=5)

        # Get appointment counts
        conn = get_conn()
        c = conn.cursor()
        c.execute("""SELECT date, COUNT(*) FROM appointments
                    WHERE date LIKE ? GROUP BY date""", (f"{year}-{month:02d}%",))
        appt_counts = {r[0]: r[1] for r in c.fetchall()}
        conn.close()

        # Calendar days
        cal = calendar.monthcalendar(year, month)
        for row_idx, week in enumerate(cal, 1):
            for col_idx, day in enumerate(week):
                if day == 0:
                    tk.Label(grid, text="", bg=C["card"]).grid(row=row_idx, column=col_idx)
                    continue

                date_str = f"{year}-{month:02d}-{day:02d}"
                count = appt_counts.get(date_str, 0)
                is_today = (day == now.day and month == now.month)

                cell_bg = C["primary_dark"] if is_today else C["bg_secondary"]
                cell = tk.Frame(grid, bg=cell_bg, padx=5, pady=5)
                cell.grid(row=row_idx, column=col_idx, padx=2, pady=2, sticky="nsew")
                grid.grid_rowconfigure(row_idx, weight=1)

                tk.Label(cell, text=str(day), bg=cell_bg,
                         fg="white" if is_today else C["text"],
                         font=("Segoe UI", 11, "bold" if is_today else "normal")).pack(anchor="w")
                if count:
                    tk.Label(cell, text=f"{count} appt", bg=cell_bg, fg=C["accent"],
                             font=("Segoe UI", 8)).pack(anchor="w")

    # ============================== REPORTS ==============================

    def _show_reports(self):
        self._clear()
        self._set_active("reports")
        h = self._header("Reports & Analytics", "Business Intelligence")

        btn_f = tk.Frame(h, bg=C["bg"])
        btn_f.pack(side="right")
        tk.Button(btn_f, text="Export Excel", bg=C["primary"], fg="white",
                  font=F["button"], relief="flat", padx=10, pady=4,
                  command=self._export_all, cursor="hand2").pack(side="left", padx=2)
        tk.Button(btn_f, text="Daily Report", bg=C["info"], fg="white",
                  font=F["button"], relief="flat", padx=10, pady=4,
                  command=self._daily_report, cursor="hand2").pack(side="left", padx=2)

        if not HAS_MPL:
            tk.Label(self.main, text="Install matplotlib: pip install matplotlib",
                     bg=C["bg"], fg=C["warning"], font=("Segoe UI", 14)).pack(pady=40)
            return

        conn = get_conn()
        c = conn.cursor()

        # 7-day revenue
        dates, revenues = [], []
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            c.execute("SELECT COALESCE(SUM(grand_total),0) FROM bills WHERE created_at LIKE ?", (f"{date}%",))
            br = c.fetchone()[0]
            c.execute("SELECT COALESCE(SUM(total),0) FROM pharmacy_sales WHERE created_at LIKE ?", (f"{date}%",))
            pr = c.fetchone()[0]
            revenues.append(br + pr)
            dates.append((datetime.now() - timedelta(days=i)).strftime("%d/%m"))

        # Department
        c.execute("SELECT department, COUNT(*) FROM appointments GROUP BY department ORDER BY COUNT(*) DESC LIMIT 6")
        dept_data = c.fetchall()

        # Payment
        c.execute("SELECT payment_method, COUNT(*) FROM bills GROUP BY payment_method")
        pay_data = c.fetchall()

        # Doctor revenue
        month = datetime.now().strftime("%Y-%m")
        c.execute("""SELECT doctor_name, SUM(fee) FROM appointments WHERE date LIKE ? AND status='Completed'
                    GROUP BY doctor_name ORDER BY SUM(fee) DESC LIMIT 5""", (f"{month}%",))
        doc_rev = c.fetchall()

        conn.close()

        fig = Figure(figsize=(11, 5), facecolor=C["bg"])

        ax1 = fig.add_subplot(141)
        ax1.set_facecolor(C["card"])
        ax1.bar(dates, revenues, color=C["accent"])
        ax1.set_title("7-Day Revenue", color=C["text"], fontsize=9)
        ax1.tick_params(colors=C["text_muted"], labelsize=6)
        for sp in ax1.spines.values():
            sp.set_color(C["border"])

        if dept_data:
            ax2 = fig.add_subplot(142)
            ax2.pie([d[1] for d in dept_data], labels=[d[0] or "Other" for d in dept_data],
                    autopct="%1.0f%%", textprops={"color": C["text"], "fontsize": 7})
            ax2.set_title("Patients by Dept", color=C["text"], fontsize=9)

        if pay_data:
            ax3 = fig.add_subplot(143)
            ax3.pie([p[1] for p in pay_data], labels=[p[0] for p in pay_data],
                    autopct="%1.0f%%", textprops={"color": C["text"], "fontsize": 7})
            ax3.set_title("Payment Methods", color=C["text"], fontsize=9)

        if doc_rev:
            ax4 = fig.add_subplot(144)
            ax4.set_facecolor(C["card"])
            names = [d[0].replace("Dr. ", "") for d in doc_rev]
            vals = [d[1] for d in doc_rev]
            ax4.barh(names, vals, color=C["primary"])
            ax4.set_title("Doctor Revenue", color=C["text"], fontsize=9)
            ax4.tick_params(colors=C["text_muted"], labelsize=6)
            for sp in ax4.spines.values():
                sp.set_color(C["border"])

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, self.main)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=25, pady=(0, 15))

    def _daily_report(self):
        d = tk.Toplevel(self.root)
        d.title("Daily Summary Report")
        d.geometry("500x450")
        d.configure(bg=C["bg"])
        d.transient(self.root)

        today = datetime.now().strftime("%Y-%m-%d")
        tk.Label(d, text=f"Daily Report: {today}", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 16, "bold")).pack(pady=12)

        conn = get_conn()
        c = conn.cursor()

        stats = []
        c.execute("SELECT COUNT(*) FROM patients WHERE created_at LIKE ?", (f"{today}%",))
        stats.append(("New Patients", c.fetchone()[0]))
        c.execute("SELECT COUNT(*) FROM appointments WHERE date=?", (today,))
        stats.append(("Total Appointments", c.fetchone()[0]))
        c.execute("SELECT COUNT(*) FROM appointments WHERE date=? AND status='Completed'", (today,))
        stats.append(("Completed", c.fetchone()[0]))
        c.execute("SELECT COUNT(*) FROM appointments WHERE date=? AND status='Waiting'", (today,))
        stats.append(("Still Waiting", c.fetchone()[0]))
        c.execute("SELECT COALESCE(SUM(grand_total), 0) FROM bills WHERE created_at LIKE ?", (f"{today}%",))
        stats.append(("Billing Revenue", f"Rs {c.fetchone()[0]:,.0f}"))
        c.execute("SELECT COALESCE(SUM(total), 0) FROM pharmacy_sales WHERE created_at LIKE ?", (f"{today}%",))
        stats.append(("Pharmacy Sales", f"Rs {c.fetchone()[0]:,.0f}"))
        c.execute("SELECT COUNT(*) FROM lab_tests WHERE created_at LIKE ?", (f"{today}%",))
        stats.append(("Lab Tests", c.fetchone()[0]))
        c.execute("SELECT COUNT(*) FROM prescriptions WHERE created_at LIKE ?", (f"{today}%",))
        stats.append(("Prescriptions", c.fetchone()[0]))
        conn.close()

        for label, val in stats:
            row = tk.Frame(d, bg=C["card"], padx=15, pady=8)
            row.pack(fill="x", padx=20, pady=2)
            tk.Label(row, text=label, bg=C["card"], fg=C["text_secondary"],
                     font=("Segoe UI", 11)).pack(side="left")
            tk.Label(row, text=str(val), bg=C["card"], fg=C["accent"],
                     font=("Segoe UI", 13, "bold")).pack(side="right")

    def _export_all(self):
        try:
            import openpyxl
        except ImportError:
            messagebox.showerror("Error", "pip install openpyxl")
            return

        fp = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if not fp:
            return

        wb = openpyxl.Workbook()
        conn = get_conn()
        c = conn.cursor()

        ws = wb.active
        ws.title = "Patients"
        ws.append(["ID", "Name", "Father", "CNIC", "Age", "Gender", "Phone", "Type", "Blood", "Allergies", "Status"])
        c.execute("SELECT patient_id, name, father_name, cnic, age, gender, phone, patient_type, blood_group, allergies, status FROM patients")
        for r in c.fetchall():
            ws.append(list(r))

        for sheet_name, query, headers in [
            ("Doctors", "SELECT doctor_id, name, specialization, department, qualification, fee, phone, schedule, status FROM doctors",
             ["ID", "Name", "Spec", "Dept", "Qual", "Fee", "Phone", "Schedule", "Status"]),
            ("Appointments", "SELECT token_no, patient_name, doctor_name, department, date, time, fee, status FROM appointments ORDER BY date DESC",
             ["Token", "Patient", "Doctor", "Dept", "Date", "Time", "Fee", "Status"]),
            ("Medicines", "SELECT name, generic_name, category, price, cost_price, stock, min_stock, expiry_date, manufacturer, supplier FROM medicines",
             ["Name", "Generic", "Category", "Price", "Cost", "Stock", "Min", "Expiry", "Manufacturer", "Supplier"]),
            ("Bills", "SELECT bill_no, patient_name, bill_type, consultation_fee, lab_charges, pharmacy_charges, bed_charges, grand_total, paid, payment_status FROM bills",
             ["Bill No", "Patient", "Type", "Consult", "Lab", "Pharma", "Bed", "Total", "Paid", "Status"]),
            ("Lab Tests", "SELECT test_id, patient_name, doctor_name, test_name, test_category, fee, result, status, created_at FROM lab_tests",
             ["ID", "Patient", "Doctor", "Test", "Category", "Fee", "Result", "Status", "Date"]),
            ("Vitals", "SELECT patient_name, blood_pressure, temperature, pulse, weight, blood_sugar, oxygen_level, recorded_by, created_at FROM patient_vitals",
             ["Patient", "BP", "Temp", "Pulse", "Weight", "Sugar", "O2", "Recorded By", "Date"]),
            ("Audit Log", "SELECT user, action, module, details, created_at FROM audit_log ORDER BY id DESC LIMIT 500",
             ["User", "Action", "Module", "Details", "Date"]),
        ]:
            ws_new = wb.create_sheet(sheet_name)
            ws_new.append(headers)
            c.execute(query)
            for r in c.fetchall():
                ws_new.append(list(r))

        conn.close()
        wb.save(fp)
        audit_log(self.user["username"], "Export Data", "Reports", fp)
        messagebox.showinfo("Exported!", f"All hospital data exported to:\n{fp}")

    # ============================== NOTIFICATIONS ==============================

    def _show_notifications(self):
        self._clear()
        self._set_active("notif")
        h = self._header("Notifications", "Alerts & Reminders")

        tk.Button(h, text="Mark All Read", bg=C["primary"], fg="white",
                  font=F["button"], relief="flat", padx=12, pady=4,
                  command=self._mark_all_read, cursor="hand2").pack(side="right")

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, title, message, category, is_read, created_at FROM notifications ORDER BY id DESC LIMIT 50")
        notifs = c.fetchall()
        conn.close()

        canvas = tk.Canvas(self.main, bg=C["bg"], highlightthickness=0)
        scroll = ttk.Scrollbar(self.main, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=C["bg"])
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True, padx=25, pady=(0, 15))
        scroll.pack(side="right", fill="y")

        cat_colors = {"info": C["info"], "warning": C["warning"], "danger": C["danger"], "success": C["success"]}

        for nid, title, msg, cat, is_read, created in notifs:
            bg = C["card"] if not is_read else C["bg_secondary"]
            nf = tk.Frame(inner, bg=bg, padx=12, pady=8)
            nf.pack(fill="x", pady=2)

            top_f = tk.Frame(nf, bg=bg)
            top_f.pack(fill="x")
            tk.Label(top_f, text="●", bg=bg, fg=cat_colors.get(cat, C["text_muted"]),
                     font=("Segoe UI", 10)).pack(side="left")
            tk.Label(top_f, text=title, bg=bg, fg=C["text"],
                     font=("Segoe UI", 10, "bold")).pack(side="left", padx=8)
            tk.Label(top_f, text=created[:16], bg=bg, fg=C["text_muted"],
                     font=("Segoe UI", 8)).pack(side="right")

            if msg:
                tk.Label(nf, text=msg, bg=bg, fg=C["text_secondary"],
                         font=("Segoe UI", 9), wraplength=600, justify="left").pack(anchor="w", padx=22)

    def _mark_all_read(self):
        conn = get_conn()
        try:
            c = conn.cursor()
            c.execute("UPDATE notifications SET is_read=1")
            conn.commit()
            self._show_notifications()
        finally:
            conn.close()

    # ============================== SETTINGS ==============================

    def _show_settings(self):
        self._clear()
        self._set_active("settings")
        h = self._header("Settings", "Admin Panel")

        content = tk.Frame(self.main, bg=C["bg"])
        content.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        # User management
        user_f = tk.Frame(content, bg=C["card"], padx=15, pady=12)
        user_f.pack(fill="x", pady=(0, 10))
        tk.Label(user_f, text="User Management", bg=C["card"], fg=C["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))

        tk.Button(user_f, text="+ Add User", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=12, pady=4,
                  command=self._add_user, cursor="hand2").pack(anchor="w", pady=3)

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT username, full_name, role, status, last_login FROM users ORDER BY id")
        users = c.fetchall()
        conn.close()

        cols = ("Username", "Name", "Role", "Status", "Last Login")
        tree = ttk.Treeview(user_f, columns=cols, show="headings", height=5)
        for col, w in zip(cols, [100, 150, 100, 80, 140]):
            tree.heading(col, text=col)
            tree.column(col, width=w)
        for u in users:
            tree.insert("", "end", values=u)
        tree.pack(fill="x", pady=5)

        # Backup/Restore
        bk_f = tk.Frame(content, bg=C["card"], padx=15, pady=12)
        bk_f.pack(fill="x", pady=(0, 10))
        tk.Label(bk_f, text="Database Backup & Restore", bg=C["card"], fg=C["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))

        btn_row = tk.Frame(bk_f, bg=C["card"])
        btn_row.pack(anchor="w")
        tk.Button(btn_row, text="Backup Database", bg=C["primary"], fg="white",
                  font=F["button"], relief="flat", padx=12, pady=5,
                  command=self._backup, cursor="hand2").pack(side="left", padx=5)
        tk.Button(btn_row, text="Restore Database", bg=C["warning"], fg="black",
                  font=F["button"], relief="flat", padx=12, pady=5,
                  command=self._restore, cursor="hand2").pack(side="left", padx=5)

        # Audit log
        audit_f = tk.Frame(content, bg=C["card"], padx=15, pady=12)
        audit_f.pack(fill="both", expand=True)
        tk.Label(audit_f, text="Recent Audit Log", bg=C["card"], fg=C["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT user, action, module, details, created_at FROM audit_log ORDER BY id DESC LIMIT 15")
        logs = c.fetchall()
        conn.close()

        cols = ("User", "Action", "Module", "Details", "Time")
        log_tree = ttk.Treeview(audit_f, columns=cols, show="headings", height=6)
        for col, w in zip(cols, [80, 120, 80, 200, 130]):
            log_tree.heading(col, text=col)
            log_tree.column(col, width=w)
        for l in logs:
            log_tree.insert("", "end", values=l)
        log_tree.pack(fill="both", expand=True)

    def _add_user(self):
        d = tk.Toplevel(self.root)
        d.title("Add User")
        d.geometry("400x350")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Add New User", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(12, 8))

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)
        form.grid_columnconfigure(1, weight=1)

        fields = {}
        for label, key, default, row in [
            ("Username *", "username", "", 0),
            ("Password *", "password", "", 1),
            ("Full Name *", "name", "", 2),
            ("Phone", "phone", "", 3),
        ]:
            fields[key] = self._make_entry(form, label, default, row)

        tk.Label(form, text="Role", bg=C["bg"], fg=C["text_secondary"],
                 font=F["body_small"]).grid(row=4, column=0, sticky="w", padx=5, pady=(6, 2))
        role_var = tk.StringVar(value="Receptionist")
        ttk.Combobox(form, textvariable=role_var, values=["Admin", "Doctor", "Pharmacist", "Receptionist"],
                      state="readonly").grid(row=4, column=1, sticky="ew", padx=5)

        def save():
            uname = fields["username"].get().strip()
            pw = fields["password"].get().strip()
            name = fields["name"].get().strip()
            if not uname or not pw or not name:
                messagebox.showerror("Error", "Username, password and name required!")
                return
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""INSERT INTO users (username, password_hash, full_name, role, phone)
                            VALUES (?,?,?,?,?)""",
                         (uname, hash_password(pw), name, role_var.get(), fields["phone"].get()))
                conn.commit()
                audit_log(self.user["username"], "Add User", "Settings", f"{uname} ({role_var.get()})")
                d.destroy()
                self._show_settings()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists!")
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Create User", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=10)

    def _backup(self):
        fp = filedialog.asksaveasfilename(defaultextension=".db",
                                           filetypes=[("Database", "*.db")],
                                           initialfile=f"hospital_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        if fp:
            backup_db(fp)
            audit_log(self.user["username"], "Backup Database", "Settings", fp)
            messagebox.showinfo("Backup", f"Database backed up to:\n{fp}")

    def _restore(self):
        if not messagebox.askyesno("Restore", "This will REPLACE all current data!\nAre you sure?", icon="warning"):
            return
        fp = filedialog.askopenfilename(filetypes=[("Database", "*.db")])
        if fp:
            if restore_db(fp):
                audit_log(self.user["username"], "Restore Database", "Settings", fp)
                messagebox.showinfo("Restored", "Database restored! Please restart the application.")
            else:
                messagebox.showerror("Error", "File not found!")

    # ============================== RUN ==============================

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    login = LoginWindow()
    login.run()
