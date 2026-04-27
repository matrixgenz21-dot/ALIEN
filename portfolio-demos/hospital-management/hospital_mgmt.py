"""
Hospital Management System (HMS) - Complete Medical Software
By: Matrix Tech Solutions | Lahore, Pakistan

Features:
- Patient Registration (OPD/IPD) with CNIC & History
- Doctor Management & Scheduling
- Appointment System with Token/Queue
- Pharmacy Module (Inventory, Sales, Expiry Alerts)
- Billing & Invoicing (OPD/IPD)
- Lab Reports Management
- Bed/Ward Management (Admission/Discharge)
- Prescription System
- Dashboard with Revenue Analytics
- Excel Export for all modules
- Professional Dark Medical Theme

Target: Pakistani Hospitals, Clinics, Pharmacies
Value: PKR 50,000,000+ software

Usage:
    pip install matplotlib openpyxl
    python hospital_mgmt.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta

from database import DB_FILE, get_conn, init_db, generate_id
from theme import COLORS as C, FONTS as F

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class HospitalApp:
    def __init__(self):
        init_db()

        self.root = tk.Tk()
        self.root.title("HMS - Hospital Management System | Matrix Tech Solutions")
        self.root.geometry("1350x800")
        self.root.configure(bg=C["bg"])
        self.root.minsize(1100, 700)

        self._setup_styles()
        self._create_sidebar()
        self._create_main()
        self._show_dashboard()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                         background=C["table_row1"], foreground=C["text"],
                         fieldbackground=C["table_row1"], borderwidth=0,
                         font=F["table_body"], rowheight=28)
        style.configure("Treeview.Heading",
                         background=C["table_header"], foreground=C["primary"],
                         font=F["table_header"], borderwidth=0)
        style.map("Treeview", background=[("selected", C["table_selected"])])

    # ============================== SIDEBAR ==============================

    def _create_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=C["sidebar"], width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo area
        logo_frame = tk.Frame(self.sidebar, bg=C["primary_dark"], height=80)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        tk.Label(logo_frame, text="HMS", bg=C["primary_dark"], fg="white",
                 font=("Segoe UI", 28, "bold")).pack(pady=(12, 0))
        tk.Label(logo_frame, text="Hospital Management System", bg=C["primary_dark"],
                 fg=C["primary_light"], font=("Segoe UI", 8)).pack()

        # Menu
        menu_items = [
            ("  Dashboard", "dash", self._show_dashboard),
            ("  Patients", "patients", self._show_patients),
            ("  Doctors", "doctors", self._show_doctors),
            ("  Appointments", "appt", self._show_appointments),
            ("  Pharmacy", "pharma", self._show_pharmacy),
            ("  Prescriptions", "rx", self._show_prescriptions),
            ("  Lab Reports", "lab", self._show_lab),
            ("  Bed Management", "beds", self._show_beds),
            ("  Billing", "billing", self._show_billing),
            ("  Reports", "reports", self._show_reports),
        ]

        tk.Frame(self.sidebar, bg=C["divider"], height=1).pack(fill="x")
        tk.Label(self.sidebar, text="MAIN MENU", bg=C["sidebar"], fg=C["text_muted"],
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=20, pady=(15, 5))

        self.menu_btns = {}
        for text, key, cmd in menu_items:
            btn = tk.Button(
                self.sidebar, text=text, bg=C["sidebar"], fg=C["text_secondary"],
                font=F["menu"], relief="flat", anchor="w", padx=20, pady=8,
                activebackground=C["sidebar_hover"], activeforeground=C["primary"],
                cursor="hand2", command=cmd, borderwidth=0
            )
            btn.pack(fill="x", padx=8, pady=1)
            self.menu_btns[key] = btn

        # Bottom branding
        bottom = tk.Frame(self.sidebar, bg=C["sidebar"])
        bottom.pack(side="bottom", fill="x", pady=10)
        tk.Frame(bottom, bg=C["divider"], height=1).pack(fill="x", padx=15, pady=(0, 8))
        tk.Label(bottom, text="Matrix Tech Solutions", bg=C["sidebar"],
                 fg=C["text_muted"], font=("Segoe UI", 8)).pack()
        tk.Label(bottom, text="Lahore, Pakistan", bg=C["sidebar"],
                 fg=C["text_muted"], font=("Segoe UI", 7)).pack()

    def _set_active(self, key):
        for k, btn in self.menu_btns.items():
            if k == key:
                btn.configure(bg=C["sidebar_hover"], fg=C["primary"])
            else:
                btn.configure(bg=C["sidebar"], fg=C["text_secondary"])

    # ============================== MAIN AREA ==============================

    def _create_main(self):
        self.main = tk.Frame(self.root, bg=C["bg"])
        self.main.pack(side="right", fill="both", expand=True)

    def _clear(self):
        for w in self.main.winfo_children():
            w.destroy()

    def _header(self, title, subtitle=""):
        h = tk.Frame(self.main, bg=C["bg"])
        h.pack(fill="x", padx=30, pady=(25, 15))
        tk.Label(h, text=title, bg=C["bg"], fg=C["text"],
                 font=F["header"]).pack(side="left")
        if subtitle:
            tk.Label(h, text=subtitle, bg=C["bg"], fg=C["text_secondary"],
                     font=F["header_sub"]).pack(side="left", padx=(15, 0), pady=(8, 0))
        return h

    def _stat_card(self, parent, row, col, label, value, color, colspan=1):
        card = tk.Frame(parent, bg=C["card"], padx=20, pady=14)
        card.grid(row=row, column=col, columnspan=colspan, padx=5, pady=5, sticky="nsew")
        tk.Label(card, text=str(value), bg=C["card"], fg=color,
                 font=F["card_value"]).pack(anchor="w")
        tk.Label(card, text=label, bg=C["card"], fg=C["text_secondary"],
                 font=F["card_label"]).pack(anchor="w")
        return card

    def _make_entry(self, parent, label_text, default="", row=0):
        tk.Label(parent, text=label_text, bg=C["bg"], fg=C["text_secondary"],
                 font=F["body_small"]).grid(row=row, column=0, sticky="w", pady=(8, 2), padx=5)
        entry = tk.Entry(parent, bg=C["input_bg"], fg=C["text"], font=F["input"],
                         relief="flat", insertbackground=C["text"], highlightthickness=1,
                         highlightbackground=C["input_border"], highlightcolor=C["input_focus"])
        entry.grid(row=row, column=1, sticky="ew", pady=(8, 2), padx=5, ipady=5)
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
        occupied_beds = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM beds WHERE status='Available'")
        available_beds = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM medicines WHERE stock <= min_stock AND status='Active'")
        low_stock_meds = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM medicines WHERE expiry_date != '' AND expiry_date <= ? AND status='Active'",
                   (datetime.now().strftime("%Y-%m-%d"),))
        expired_meds = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM lab_tests WHERE status='Pending'")
        pending_labs = c.fetchone()[0]

        month = datetime.now().strftime("%Y-%m")
        c.execute("SELECT COALESCE(SUM(grand_total), 0) FROM bills WHERE created_at LIKE ?", (f"{month}%",))
        month_billing = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(total), 0) FROM pharmacy_sales WHERE created_at LIKE ?", (f"{month}%",))
        month_pharma = c.fetchone()[0]
        month_revenue = month_billing + month_pharma

        conn.close()

        # Stats grid
        grid = tk.Frame(self.main, bg=C["bg"])
        grid.pack(fill="x", padx=30)
        for i in range(5):
            grid.grid_columnconfigure(i, weight=1)

        self._stat_card(grid, 0, 0, "Total Patients", f"{total_patients:,}", C["primary"])
        self._stat_card(grid, 0, 1, "Active Doctors", str(total_doctors), C["accent"])
        self._stat_card(grid, 0, 2, "Today's Appointments", str(today_appts), C["info"])
        self._stat_card(grid, 0, 3, "Waiting Queue", str(waiting), C["warning"])
        self._stat_card(grid, 0, 4, "Today's Revenue", f"Rs {today_revenue:,.0f}", C["success"])

        self._stat_card(grid, 1, 0, "Beds Occupied", str(occupied_beds), C["orange"])
        self._stat_card(grid, 1, 1, "Beds Available", str(available_beds), C["success"])
        self._stat_card(grid, 1, 2, "Low Stock Medicines", str(low_stock_meds), C["danger"] if low_stock_meds else C["success"])
        self._stat_card(grid, 1, 3, "Pending Lab Tests", str(pending_labs), C["purple"])
        self._stat_card(grid, 1, 4, "Monthly Revenue", f"Rs {month_revenue:,.0f}", C["accent"])

        # Bottom section: Recent + Chart
        bottom = tk.Frame(self.main, bg=C["bg"])
        bottom.pack(fill="both", expand=True, padx=30, pady=(10, 20))

        # Recent appointments
        recent_frame = tk.Frame(bottom, bg=C["card"], padx=15, pady=12)
        recent_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(recent_frame, text="Today's Appointments", bg=C["card"], fg=C["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))

        conn = get_conn()
        c = conn.cursor()
        c.execute("""SELECT token_no, patient_name, doctor_name, department, time, status
                    FROM appointments WHERE date=? ORDER BY token_no""", (today,))
        rows = c.fetchall()
        conn.close()

        if rows:
            cols = ("Token", "Patient", "Doctor", "Department", "Time", "Status")
            tree = ttk.Treeview(recent_frame, columns=cols, show="headings", height=8)
            for col, w in zip(cols, [50, 150, 130, 110, 70, 80]):
                tree.heading(col, text=col)
                tree.column(col, width=w, minwidth=40)
            for r in rows:
                tree.insert("", "end", values=r)
            tree.pack(fill="both", expand=True)
        else:
            tk.Label(recent_frame, text="No appointments today.\nGo to 'Appointments' to create one.",
                     bg=C["card"], fg=C["text_muted"], font=F["body"]).pack(pady=30)

        # Alerts panel
        alerts_frame = tk.Frame(bottom, bg=C["card"], padx=15, pady=12, width=280)
        alerts_frame.pack(side="right", fill="y")
        alerts_frame.pack_propagate(False)

        tk.Label(alerts_frame, text="Alerts & Notifications", bg=C["card"], fg=C["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 10))

        alerts = []
        if waiting > 0:
            alerts.append((f"{waiting} patients waiting in queue", C["warning"]))
        if low_stock_meds > 0:
            alerts.append((f"{low_stock_meds} medicines low on stock", C["danger"]))
        if expired_meds > 0:
            alerts.append((f"{expired_meds} medicines expired!", C["danger"]))
        if pending_labs > 0:
            alerts.append((f"{pending_labs} lab reports pending", C["purple"]))
        if occupied_beds > 0:
            alerts.append((f"{occupied_beds} beds occupied / {available_beds} available", C["info"]))

        if not alerts:
            alerts.append(("All systems normal", C["success"]))

        for msg, color in alerts:
            af = tk.Frame(alerts_frame, bg=C["bg_secondary"], padx=10, pady=8)
            af.pack(fill="x", pady=3)
            tk.Label(af, text="●", bg=C["bg_secondary"], fg=color, font=("Segoe UI", 10)).pack(side="left")
            tk.Label(af, text=msg, bg=C["bg_secondary"], fg=C["text_secondary"],
                     font=("Segoe UI", 9)).pack(side="left", padx=8)

    # ============================== PATIENTS ==============================

    def _show_patients(self):
        self._clear()
        self._set_active("patients")
        h = self._header("Patient Management", "Registration & Records")

        btn_frame = tk.Frame(h, bg=C["bg"])
        btn_frame.pack(side="right")
        tk.Button(btn_frame, text="+ Register Patient", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=15, pady=5,
                  command=self._register_patient, cursor="hand2").pack(side="left", padx=5)

        # Search
        sf = tk.Frame(self.main, bg=C["bg"])
        sf.pack(fill="x", padx=30, pady=(0, 10))
        self.pat_search = tk.Entry(sf, bg=C["input_bg"], fg=C["text"], font=F["input"],
                                    relief="flat", insertbackground=C["text"],
                                    highlightthickness=1, highlightbackground=C["input_border"])
        self.pat_search.pack(side="left", fill="x", expand=True, ipady=7)
        self.pat_search.insert(0, "Search by name, CNIC, patient ID...")
        self.pat_search.bind("<FocusIn>", lambda e: self.pat_search.delete(0, "end") if "Search" in self.pat_search.get() else None)
        self.pat_search.bind("<KeyRelease>", lambda e: self._load_patients())

        # Table
        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        cols = ("Patient ID", "Name", "Father", "CNIC", "Age", "Gender", "Phone", "Type", "Blood", "Status")
        self.pat_tree = ttk.Treeview(tf, columns=cols, show="headings", height=18)
        widths = [85, 150, 120, 130, 40, 60, 100, 50, 50, 60]
        for col, w in zip(cols, widths):
            self.pat_tree.heading(col, text=col)
            self.pat_tree.column(col, width=w, minwidth=35)

        sb = ttk.Scrollbar(tf, orient="vertical", command=self.pat_tree.yview)
        self.pat_tree.configure(yscrollcommand=sb.set)
        self.pat_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.pat_tree.bind("<Double-1>", lambda e: self._edit_patient())

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
            c.execute("""SELECT patient_id, name, father_name, cnic, age, gender, phone, patient_type, blood_group, status
                        FROM patients WHERE name LIKE ? OR cnic LIKE ? OR patient_id LIKE ? OR phone LIKE ?
                        ORDER BY id DESC""", (q, q, q, q))
        else:
            c.execute("""SELECT patient_id, name, father_name, cnic, age, gender, phone, patient_type, blood_group, status
                        FROM patients ORDER BY id DESC""")

        for r in c.fetchall():
            self.pat_tree.insert("", "end", values=r)
        conn.close()

    def _register_patient(self):
        d = tk.Toplevel(self.root)
        d.title("Register New Patient")
        d.geometry("550x620")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Patient Registration", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 16, "bold")).pack(pady=(15, 10))

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)
        form.grid_columnconfigure(1, weight=1)

        pid = generate_id("PAT", "patients", "patient_id")
        fields = {}
        defs = [
            ("Patient ID", "patient_id", pid, 0),
            ("Full Name *", "name", "", 1),
            ("Father's Name", "father_name", "", 2),
            ("CNIC", "cnic", "", 3),
            ("Age", "age", "", 4),
            ("Phone", "phone", "", 5),
            ("Email", "email", "", 6),
            ("Address", "address", "", 7),
            ("Emergency Contact", "emergency", "", 8),
        ]
        for label, key, default, row in defs:
            fields[key] = self._make_entry(form, label, default, row)

        # Gender
        tk.Label(form, text="Gender", bg=C["bg"], fg=C["text_secondary"],
                 font=F["body_small"]).grid(row=9, column=0, sticky="w", pady=(8, 2), padx=5)
        gender_var = tk.StringVar(value="Male")
        gf = tk.Frame(form, bg=C["bg"])
        gf.grid(row=9, column=1, sticky="w", pady=(8, 2), padx=5)
        for g in ["Male", "Female", "Other"]:
            tk.Radiobutton(gf, text=g, variable=gender_var, value=g, bg=C["bg"],
                           fg=C["text"], selectcolor=C["input_bg"], font=F["body_small"],
                           activebackground=C["bg"]).pack(side="left", padx=8)

        # Blood group
        tk.Label(form, text="Blood Group", bg=C["bg"], fg=C["text_secondary"],
                 font=F["body_small"]).grid(row=10, column=0, sticky="w", pady=(8, 2), padx=5)
        blood_var = tk.StringVar(value="")
        ttk.Combobox(form, textvariable=blood_var,
                      values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                      state="readonly").grid(row=10, column=1, sticky="ew", pady=(8, 2), padx=5)

        # Type
        tk.Label(form, text="Patient Type", bg=C["bg"], fg=C["text_secondary"],
                 font=F["body_small"]).grid(row=11, column=0, sticky="w", pady=(8, 2), padx=5)
        type_var = tk.StringVar(value="OPD")
        ttk.Combobox(form, textvariable=type_var, values=["OPD", "IPD", "Emergency"],
                      state="readonly").grid(row=11, column=1, sticky="ew", pady=(8, 2), padx=5)

        def save():
            name = fields["name"].get().strip()
            if not name:
                messagebox.showerror("Error", "Patient name is required!")
                return
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""INSERT INTO patients (patient_id, name, father_name, cnic, age, gender, phone, email, address, blood_group, emergency_contact, patient_type)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (fields["patient_id"].get(), name, fields["father_name"].get(),
                          fields["cnic"].get(), int(fields["age"].get() or 0),
                          gender_var.get(), fields["phone"].get(), fields["email"].get(),
                          fields["address"].get(), blood_var.get(), fields["emergency"].get(),
                          type_var.get()))
                conn.commit()
                d.destroy()
                self._load_patients()
                messagebox.showinfo("Success", f"Patient '{name}' registered!\nID: {fields['patient_id'].get()}")
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Register Patient", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=8,
                  command=save, cursor="hand2").pack(pady=15)

    def _edit_patient(self):
        sel = self.pat_tree.selection()
        if not sel:
            return
        pid = self.pat_tree.item(sel[0])["values"][0]

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM patients WHERE patient_id=?", (pid,))
        p = c.fetchone()
        conn.close()
        if not p:
            return

        d = tk.Toplevel(self.root)
        d.title(f"Patient: {p[2]}")
        d.geometry("550x550")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text=f"Edit Patient: {p[1]}", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(15, 10))

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)
        form.grid_columnconfigure(1, weight=1)

        fields = {}
        defs = [
            ("Name", "name", p[2], 0),
            ("Father", "father", p[3] or "", 1),
            ("CNIC", "cnic", p[4] or "", 2),
            ("Age", "age", str(p[5]), 3),
            ("Phone", "phone", p[7] or "", 4),
            ("Address", "address", p[9] or "", 5),
        ]
        for label, key, val, row in defs:
            fields[key] = self._make_entry(form, label, val, row)

        tk.Label(form, text="Status", bg=C["bg"], fg=C["text_secondary"],
                 font=F["body_small"]).grid(row=6, column=0, sticky="w", pady=(8, 2), padx=5)
        stat_var = tk.StringVar(value=p[13] or "Active")
        ttk.Combobox(form, textvariable=stat_var, values=["Active", "Discharged", "Deceased"],
                      state="readonly").grid(row=6, column=1, sticky="ew", pady=(8, 2), padx=5)

        def save():
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""UPDATE patients SET name=?, father_name=?, cnic=?, age=?, phone=?, address=?, status=?
                            WHERE patient_id=?""",
                         (fields["name"].get(), fields["father"].get(), fields["cnic"].get(),
                          int(fields["age"].get() or 0), fields["phone"].get(),
                          fields["address"].get(), stat_var.get(), pid))
                conn.commit()
                d.destroy()
                self._load_patients()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Save Changes", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=12)

    # ============================== DOCTORS ==============================

    def _show_doctors(self):
        self._clear()
        self._set_active("doctors")
        h = self._header("Doctor Management", "Staff & Scheduling")

        tk.Button(h, text="+ Add Doctor", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=15, pady=5,
                  command=self._add_doctor, cursor="hand2").pack(side="right")

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        cols = ("Doctor ID", "Name", "Specialization", "Department", "Qualification", "Fee", "Schedule", "Phone", "Status")
        self.doc_tree = ttk.Treeview(tf, columns=cols, show="headings", height=18)
        widths = [80, 150, 120, 110, 100, 80, 130, 100, 70]
        for col, w in zip(cols, widths):
            self.doc_tree.heading(col, text=col)
            self.doc_tree.column(col, width=w, minwidth=40)

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT doctor_id, name, specialization, department, qualification, fee, schedule, phone, status FROM doctors ORDER BY id DESC")
        for r in c.fetchall():
            self.doc_tree.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4], f"Rs {r[5]:,.0f}", r[6], r[7], r[8]))
        conn.close()

        self.doc_tree.pack(fill="both", expand=True)
        self.doc_tree.bind("<Double-1>", lambda e: self._edit_doctor())

    def _add_doctor(self):
        d = tk.Toplevel(self.root)
        d.title("Add Doctor")
        d.geometry("500x520")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Add New Doctor", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(15, 10))

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
                 font=F["body_small"]).grid(row=8, column=0, sticky="w", pady=(8, 2), padx=5)
        dept_var = tk.StringVar(value=dept_list[0] if dept_list else "")
        ttk.Combobox(form, textvariable=dept_var, values=dept_list,
                      state="readonly").grid(row=8, column=1, sticky="ew", pady=(8, 2), padx=5)

        def save():
            name = fields["name"].get().strip()
            if not name:
                messagebox.showerror("Error", "Doctor name required!")
                return
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""INSERT INTO doctors (doctor_id, name, specialization, department, qualification, phone, email, fee, schedule)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (fields["doctor_id"].get(), name, fields["specialization"].get(),
                          dept_var.get(), fields["qualification"].get(), fields["phone"].get(),
                          fields["email"].get(), float(fields["fee"].get() or 0),
                          fields["schedule"].get()))
                conn.commit()
                d.destroy()
                self._show_doctors()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Save Doctor", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=12)

    def _edit_doctor(self):
        sel = self.doc_tree.selection()
        if not sel:
            return
        did = self.doc_tree.item(sel[0])["values"][0]
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM doctors WHERE doctor_id=?", (did,))
        doc = c.fetchone()
        conn.close()
        if not doc:
            return

        d = tk.Toplevel(self.root)
        d.title(f"Dr. {doc[2]}")
        d.geometry("500x480")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text=f"Edit: Dr. {doc[2]}", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(15, 10))

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)
        form.grid_columnconfigure(1, weight=1)

        fields = {}
        for label, key, val, row in [
            ("Name", "name", doc[2], 0),
            ("Specialization", "spec", doc[3] or "", 1),
            ("Qualification", "qual", doc[5] or "", 2),
            ("Fee", "fee", str(doc[8]), 3),
            ("Phone", "phone", doc[6] or "", 4),
            ("Schedule", "schedule", doc[9] or "", 5),
        ]:
            fields[key] = self._make_entry(form, label, val, row)

        tk.Label(form, text="Status", bg=C["bg"], fg=C["text_secondary"],
                 font=F["body_small"]).grid(row=6, column=0, sticky="w", pady=(8, 2), padx=5)
        stat_var = tk.StringVar(value=doc[10] or "Active")
        ttk.Combobox(form, textvariable=stat_var, values=["Active", "On Leave", "Inactive"],
                      state="readonly").grid(row=6, column=1, sticky="ew", pady=(8, 2), padx=5)

        def save():
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""UPDATE doctors SET name=?, specialization=?, qualification=?, fee=?, phone=?, schedule=?, status=?
                            WHERE doctor_id=?""",
                         (fields["name"].get(), fields["spec"].get(), fields["qual"].get(),
                          float(fields["fee"].get() or 0), fields["phone"].get(),
                          fields["schedule"].get(), stat_var.get(), did))
                conn.commit()
                d.destroy()
                self._show_doctors()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Save", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=12)

    # ============================== APPOINTMENTS ==============================

    def _show_appointments(self):
        self._clear()
        self._set_active("appt")
        h = self._header("Appointments", "Token & Queue Management")

        tk.Button(h, text="+ New Appointment", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=15, pady=5,
                  command=self._new_appointment, cursor="hand2").pack(side="right")

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        cols = ("Token", "Patient", "Doctor", "Department", "Date", "Time", "Fee", "Status")
        self.appt_tree = ttk.Treeview(tf, columns=cols, show="headings", height=18)
        for col, w in zip(cols, [55, 150, 140, 110, 90, 70, 80, 80]):
            self.appt_tree.heading(col, text=col)
            self.appt_tree.column(col, width=w, minwidth=40)

        today = datetime.now().strftime("%Y-%m-%d")
        conn = get_conn()
        c = conn.cursor()
        c.execute("""SELECT token_no, patient_name, doctor_name, department, date, time, fee, status
                    FROM appointments WHERE date=? ORDER BY token_no""", (today,))
        for r in c.fetchall():
            self.appt_tree.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4], r[5], f"Rs {r[6]:,.0f}", r[7]))
        conn.close()

        self.appt_tree.pack(fill="both", expand=True)
        self.appt_tree.bind("<Double-1>", lambda e: self._update_appt_status())

        tk.Label(tf, text="Double-click to update status (Waiting → In Progress → Completed)",
                 bg=C["card"], fg=C["text_muted"], font=F["body_small"]).pack(pady=3)

    def _new_appointment(self):
        d = tk.Toplevel(self.root)
        d.title("New Appointment")
        d.geometry("480x420")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Book Appointment", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(15, 10))

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
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=5)

        tk.Label(form, text="Patient", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(8, 2))
        pat_var = tk.StringVar()
        ttk.Combobox(form, textvariable=pat_var,
                      values=[f"{p[0]} - {p[1]}" for p in patients],
                      state="readonly").pack(fill="x", ipady=3)

        tk.Label(form, text="Doctor", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(8, 2))
        doc_var = tk.StringVar()
        doc_combo = ttk.Combobox(form, textvariable=doc_var,
                                  values=[f"{d[0]} - {d[1]} ({d[2]}) - Rs {d[3]:,.0f}" for d in doctors],
                                  state="readonly")
        doc_combo.pack(fill="x", ipady=3)

        tk.Label(form, text="Date", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(8, 2))
        date_entry = tk.Entry(form, bg=C["input_bg"], fg=C["text"], font=F["input"], relief="flat")
        date_entry.pack(fill="x", ipady=5)
        date_entry.insert(0, today)

        tk.Label(form, text="Time", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(8, 2))
        time_entry = tk.Entry(form, bg=C["input_bg"], fg=C["text"], font=F["input"], relief="flat")
        time_entry.pack(fill="x", ipady=5)
        time_entry.insert(0, datetime.now().strftime("%H:%M"))

        def save():
            if not pat_var.get() or not doc_var.get():
                messagebox.showerror("Error", "Select patient and doctor!")
                return

            pat_parts = pat_var.get().split(" - ")
            doc_parts = doc_var.get().split(" - ")
            pat_id, pat_name = pat_parts[0], pat_parts[1]
            doc_id = doc_parts[0]

            # Find doctor details
            doc_info = next((dd for dd in doctors if dd[0] == doc_id), None)
            if not doc_info:
                return

            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""INSERT INTO appointments (token_no, patient_id, patient_name, doctor_id, doctor_name, department, date, time, fee)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (next_token, pat_id, pat_name, doc_id, doc_info[1], doc_info[2],
                          date_entry.get(), time_entry.get(), doc_info[3]))
                conn.commit()
                d.destroy()
                self._show_appointments()
                messagebox.showinfo("Appointment Booked",
                                     f"Token #{next_token}\nPatient: {pat_name}\nDoctor: {doc_info[1]}\nFee: Rs {doc_info[3]:,.0f}")
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Book Appointment", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=12)

    def _update_appt_status(self):
        sel = self.appt_tree.selection()
        if not sel:
            return
        vals = self.appt_tree.item(sel[0])["values"]
        token = vals[0]
        current = vals[7]
        today = datetime.now().strftime("%Y-%m-%d")

        flow = {"Waiting": "In Progress", "In Progress": "Completed", "Completed": "Completed"}
        new_status = flow.get(current, current)

        if new_status == current and current == "Completed":
            messagebox.showinfo("Info", "Appointment already completed.")
            return

        conn = get_conn()
        try:
            c = conn.cursor()
            c.execute("UPDATE appointments SET status=? WHERE token_no=? AND date=?",
                     (new_status, token, today))
            conn.commit()
            self._show_appointments()
        finally:
            conn.close()

    # ============================== PHARMACY ==============================

    def _show_pharmacy(self):
        self._clear()
        self._set_active("pharma")
        h = self._header("Pharmacy", "Medicine Inventory & Sales")

        btn_f = tk.Frame(h, bg=C["bg"])
        btn_f.pack(side="right")
        tk.Button(btn_f, text="+ Add Medicine", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=12, pady=5,
                  command=self._add_medicine, cursor="hand2").pack(side="left", padx=3)
        tk.Button(btn_f, text="New Sale", bg=C["primary"], fg="white",
                  font=F["button"], relief="flat", padx=12, pady=5,
                  command=self._pharmacy_sale, cursor="hand2").pack(side="left", padx=3)

        # Search
        sf = tk.Frame(self.main, bg=C["bg"])
        sf.pack(fill="x", padx=30, pady=(0, 8))
        self.med_search = tk.Entry(sf, bg=C["input_bg"], fg=C["text"], font=F["input"],
                                    relief="flat", insertbackground=C["text"])
        self.med_search.pack(side="left", fill="x", expand=True, ipady=6)
        self.med_search.insert(0, "Search medicine...")
        self.med_search.bind("<FocusIn>", lambda e: self.med_search.delete(0, "end") if "Search" in self.med_search.get() else None)
        self.med_search.bind("<KeyRelease>", lambda e: self._load_medicines())

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        cols = ("ID", "Name", "Generic", "Category", "Price", "Stock", "Min", "Expiry", "Manufacturer", "Status")
        self.med_tree = ttk.Treeview(tf, columns=cols, show="headings", height=16)
        for col, w in zip(cols, [40, 160, 120, 90, 70, 55, 45, 85, 110, 60]):
            self.med_tree.heading(col, text=col)
            self.med_tree.column(col, width=w, minwidth=35)

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
            c.execute("""SELECT id, name, generic_name, category, price, stock, min_stock, expiry_date, manufacturer, status
                        FROM medicines WHERE name LIKE ? OR generic_name LIKE ? ORDER BY name""", (q, q))
        else:
            c.execute("""SELECT id, name, generic_name, category, price, stock, min_stock, expiry_date, manufacturer, status
                        FROM medicines ORDER BY name""")

        for r in c.fetchall():
            status = r[9]
            if r[5] <= r[6]:
                status = "LOW"
            if r[7] and r[7] <= datetime.now().strftime("%Y-%m-%d"):
                status = "EXPIRED"
            self.med_tree.insert("", "end", values=(r[0], r[1], r[2], r[3], f"Rs {r[4]:,.0f}", r[5], r[6], r[7], r[8], status))
        conn.close()

    def _add_medicine(self):
        d = tk.Toplevel(self.root)
        d.title("Add Medicine")
        d.geometry("480x520")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Add Medicine", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(15, 10))

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
            ("Expiry Date (YYYY-MM-DD)", "expiry", "", 9),
            ("Shelf Location", "shelf", "", 10),
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
                c.execute("""INSERT INTO medicines (name, generic_name, category, manufacturer, batch_no, price, cost_price, stock, min_stock, expiry_date, shelf_location)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (name, fields["generic"].get(), fields["category"].get(),
                          fields["manufacturer"].get(), fields["batch"].get(),
                          float(fields["price"].get() or 0), float(fields["cost"].get() or 0),
                          int(fields["stock"].get() or 0), int(fields["min_stock"].get() or 10),
                          fields["expiry"].get(), fields["shelf"].get()))
                conn.commit()
                d.destroy()
                self._load_medicines()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Save Medicine", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=12)

    def _pharmacy_sale(self):
        d = tk.Toplevel(self.root)
        d.title("Pharmacy Sale")
        d.geometry("650x500")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Pharmacy Sale", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(15, 5))

        top = tk.Frame(d, bg=C["bg"])
        top.pack(fill="x", padx=20)

        tk.Label(top, text="Customer:", bg=C["bg"], fg=C["text_secondary"]).pack(side="left")
        cust_entry = tk.Entry(top, bg=C["input_bg"], fg=C["text"], font=F["input"], relief="flat", width=25)
        cust_entry.pack(side="left", padx=5, ipady=3)
        cust_entry.insert(0, "Walk-in")

        # Cart
        cart_items = []
        cart_frame = tk.Frame(d, bg=C["card"], padx=10, pady=10)
        cart_frame.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("Medicine", "Qty", "Price", "Total")
        cart_tree = ttk.Treeview(cart_frame, columns=cols, show="headings", height=8)
        for col, w in zip(cols, [250, 60, 100, 100]):
            cart_tree.heading(col, text=col)
            cart_tree.column(col, width=w)
        cart_tree.pack(fill="both", expand=True)

        total_label = tk.Label(cart_frame, text="Total: Rs 0", bg=C["card"], fg=C["accent"],
                               font=("Segoe UI", 16, "bold"))
        total_label.pack(anchor="e", pady=5)

        # Add medicine row
        add_frame = tk.Frame(d, bg=C["bg"])
        add_frame.pack(fill="x", padx=20)

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, name, price, stock FROM medicines WHERE stock > 0 AND status='Active' ORDER BY name")
        meds = c.fetchall()
        conn.close()

        med_var = tk.StringVar()
        ttk.Combobox(add_frame, textvariable=med_var,
                      values=[f"{m[0]} - {m[1]} (Rs {m[2]:,.0f}) [{m[3]} left]" for m in meds],
                      state="readonly", width=40).pack(side="left", padx=3)

        qty_entry = tk.Entry(add_frame, bg=C["input_bg"], fg=C["text"], font=F["input"],
                              relief="flat", width=6)
        qty_entry.pack(side="left", padx=3, ipady=3)
        qty_entry.insert(0, "1")

        def add_to_cart():
            if not med_var.get():
                return
            mid = int(med_var.get().split(" - ")[0])
            med = next((m for m in meds if m[0] == mid), None)
            if not med:
                return
            qty = int(qty_entry.get() or 1)
            if qty > med[3]:
                messagebox.showwarning("Low Stock", f"Only {med[3]} available!")
                return
            total = qty * med[2]
            cart_items.append({"id": mid, "name": med[1], "qty": qty, "price": med[2], "total": total})
            cart_tree.insert("", "end", values=(med[1], qty, f"Rs {med[2]:,.0f}", f"Rs {total:,.0f}"))
            grand = sum(ci["total"] for ci in cart_items)
            total_label.config(text=f"Total: Rs {grand:,.0f}")

        tk.Button(add_frame, text="Add", bg=C["primary"], fg="white", font=F["button"],
                  relief="flat", padx=10, command=add_to_cart, cursor="hand2").pack(side="left", padx=3)

        def complete_sale():
            if not cart_items:
                messagebox.showwarning("Empty", "Add medicines first!")
                return
            grand = sum(ci["total"] for ci in cart_items)
            inv_no = f"PH-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""INSERT INTO pharmacy_sales (invoice_no, patient_name, items_count, subtotal, total)
                            VALUES (?, ?, ?, ?, ?)""",
                         (inv_no, cust_entry.get(), len(cart_items), grand, grand))
                sale_id = c.lastrowid
                for ci in cart_items:
                    c.execute("""INSERT INTO pharmacy_sale_items (sale_id, medicine_id, medicine_name, quantity, price, total)
                                VALUES (?, ?, ?, ?, ?, ?)""",
                             (sale_id, ci["id"], ci["name"], ci["qty"], ci["price"], ci["total"]))
                    c.execute("UPDATE medicines SET stock = stock - ? WHERE id = ?", (ci["qty"], ci["id"]))
                conn.commit()
                d.destroy()
                messagebox.showinfo("Sale Complete", f"Invoice: {inv_no}\nTotal: Rs {grand:,.0f}")
                self._show_pharmacy()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Complete Sale", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=complete_sale, cursor="hand2").pack(pady=8)

    # ============================== PRESCRIPTIONS ==============================

    def _show_prescriptions(self):
        self._clear()
        self._set_active("rx")
        h = self._header("Prescriptions", "Doctor Prescriptions")

        tk.Button(h, text="+ New Prescription", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=15, pady=5,
                  command=self._new_prescription, cursor="hand2").pack(side="right")

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        cols = ("ID", "Patient", "Doctor", "Diagnosis", "Medicines", "Follow-up", "Date")
        tree = ttk.Treeview(tf, columns=cols, show="headings", height=18)
        for col, w in zip(cols, [40, 140, 140, 160, 200, 90, 90]):
            tree.heading(col, text=col)
            tree.column(col, width=w, minwidth=40)

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
        d.geometry("550x550")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Write Prescription", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(15, 10))

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT patient_id, name FROM patients WHERE status='Active'")
        patients = c.fetchall()
        c.execute("SELECT doctor_id, name FROM doctors WHERE status='Active'")
        doctors = c.fetchall()
        conn.close()

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)

        tk.Label(form, text="Patient", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(5, 2))
        pat_var = tk.StringVar()
        ttk.Combobox(form, textvariable=pat_var,
                      values=[f"{p[0]} - {p[1]}" for p in patients], state="readonly").pack(fill="x", ipady=3)

        tk.Label(form, text="Doctor", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(5, 2))
        doc_var = tk.StringVar()
        ttk.Combobox(form, textvariable=doc_var,
                      values=[f"{dd[0]} - {dd[1]}" for dd in doctors], state="readonly").pack(fill="x", ipady=3)

        tk.Label(form, text="Diagnosis", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(5, 2))
        diag = tk.Text(form, bg=C["input_bg"], fg=C["text"], font=F["input"], height=3, relief="flat")
        diag.pack(fill="x")

        tk.Label(form, text="Medicines (one per line)", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(5, 2))
        meds = tk.Text(form, bg=C["input_bg"], fg=C["text"], font=F["input"], height=4, relief="flat")
        meds.pack(fill="x")

        tk.Label(form, text="Instructions", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(5, 2))
        instr = tk.Text(form, bg=C["input_bg"], fg=C["text"], font=F["input"], height=2, relief="flat")
        instr.pack(fill="x")

        tk.Label(form, text="Follow-up Date", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(5, 2))
        followup = tk.Entry(form, bg=C["input_bg"], fg=C["text"], font=F["input"], relief="flat")
        followup.pack(fill="x", ipady=4)

        def save():
            if not pat_var.get() or not doc_var.get():
                messagebox.showerror("Error", "Select patient and doctor!")
                return
            pat_name = pat_var.get().split(" - ")[1]
            doc_parts = doc_var.get().split(" - ")
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""INSERT INTO prescriptions (patient_id, patient_name, doctor_id, doctor_name, diagnosis, medicines, instructions, follow_up)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                         (pat_var.get().split(" - ")[0], pat_name, doc_parts[0], doc_parts[1],
                          diag.get("1.0", "end").strip(), meds.get("1.0", "end").strip(),
                          instr.get("1.0", "end").strip(), followup.get()))
                conn.commit()
                d.destroy()
                self._show_prescriptions()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Save Prescription", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=10)

    # ============================== LAB REPORTS ==============================

    def _show_lab(self):
        self._clear()
        self._set_active("lab")
        h = self._header("Lab Reports", "Test Requests & Results")

        tk.Button(h, text="+ Request Test", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=15, pady=5,
                  command=self._request_lab_test, cursor="hand2").pack(side="right")

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        cols = ("Test ID", "Patient", "Doctor", "Test Name", "Category", "Fee", "Result", "Status", "Date")
        self.lab_tree = ttk.Treeview(tf, columns=cols, show="headings", height=16)
        for col, w in zip(cols, [75, 130, 120, 130, 90, 70, 100, 70, 85]):
            self.lab_tree.heading(col, text=col)
            self.lab_tree.column(col, width=w, minwidth=40)

        conn = get_conn()
        c = conn.cursor()
        c.execute("""SELECT test_id, patient_name, doctor_name, test_name, test_category, fee, result, status, created_at
                    FROM lab_tests ORDER BY id DESC""")
        for r in c.fetchall():
            self.lab_tree.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4], f"Rs {r[5]:,.0f}", r[6][:30] or "-", r[7], r[8][:10]))
        conn.close()
        self.lab_tree.pack(fill="both", expand=True)
        self.lab_tree.bind("<Double-1>", lambda e: self._update_lab_result())

        tk.Label(tf, text="Double-click to enter result", bg=C["card"], fg=C["text_muted"],
                 font=F["body_small"]).pack(pady=3)

    def _request_lab_test(self):
        d = tk.Toplevel(self.root)
        d.title("Request Lab Test")
        d.geometry("480x400")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Lab Test Request", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(15, 10))

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT patient_id, name FROM patients WHERE status='Active'")
        patients = c.fetchall()
        c.execute("SELECT doctor_id, name FROM doctors WHERE status='Active'")
        doctors = c.fetchall()
        conn.close()

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)

        tk.Label(form, text="Patient", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(5, 2))
        pat_var = tk.StringVar()
        ttk.Combobox(form, textvariable=pat_var,
                      values=[f"{p[0]} - {p[1]}" for p in patients], state="readonly").pack(fill="x", ipady=3)

        tk.Label(form, text="Referred by Doctor", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(5, 2))
        doc_var = tk.StringVar()
        ttk.Combobox(form, textvariable=doc_var,
                      values=[f"{dd[0]} - {dd[1]}" for dd in doctors], state="readonly").pack(fill="x", ipady=3)

        form2 = tk.Frame(d, bg=C["bg"])
        form2.pack(fill="x", padx=25)
        form2.grid_columnconfigure(1, weight=1)

        test_categories = ["Blood Test", "Urine Test", "X-Ray", "CT Scan", "MRI", "Ultrasound", "ECG", "Other"]

        fields = {}
        fields["test_name"] = self._make_entry(form2, "Test Name *", "", 0)
        tk.Label(form2, text="Category", bg=C["bg"], fg=C["text_secondary"],
                 font=F["body_small"]).grid(row=1, column=0, sticky="w", pady=(8, 2), padx=5)
        cat_var = tk.StringVar(value="Blood Test")
        ttk.Combobox(form2, textvariable=cat_var, values=test_categories,
                      state="readonly").grid(row=1, column=1, sticky="ew", pady=(8, 2), padx=5)
        fields["fee"] = self._make_entry(form2, "Fee (Rs)", "500", 2)

        def save():
            if not pat_var.get() or not fields["test_name"].get().strip():
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
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                         (test_id, pat_parts[0], pat_parts[1], doc_id, doc_name,
                          fields["test_name"].get(), cat_var.get(), float(fields["fee"].get() or 0)))
                conn.commit()
                d.destroy()
                self._show_lab()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Submit Request", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=12)

    def _update_lab_result(self):
        sel = self.lab_tree.selection()
        if not sel:
            return
        test_id = self.lab_tree.item(sel[0])["values"][0]

        d = tk.Toplevel(self.root)
        d.title(f"Lab Result: {test_id}")
        d.geometry("400x280")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text=f"Enter Result: {test_id}", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 14, "bold")).pack(pady=(15, 10))

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)

        tk.Label(form, text="Result", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(5, 2))
        result = tk.Text(form, bg=C["input_bg"], fg=C["text"], font=F["input"], height=4, relief="flat")
        result.pack(fill="x")

        tk.Label(form, text="Normal Range", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(5, 2))
        normal = tk.Entry(form, bg=C["input_bg"], fg=C["text"], font=F["input"], relief="flat")
        normal.pack(fill="x", ipady=4)

        def save():
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""UPDATE lab_tests SET result=?, normal_range=?, status='Completed', report_date=?
                            WHERE test_id=?""",
                         (result.get("1.0", "end").strip(), normal.get(),
                          datetime.now().strftime("%Y-%m-%d"), test_id))
                conn.commit()
                d.destroy()
                self._show_lab()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Save Result", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=10)

    # ============================== BED MANAGEMENT ==============================

    def _show_beds(self):
        self._clear()
        self._set_active("beds")
        h = self._header("Bed Management", "Ward & Admission")

        tk.Button(h, text="Admit Patient", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=15, pady=5,
                  command=self._admit_patient, cursor="hand2").pack(side="right")

        # Ward summary
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

        # Ward cards
        ward_frame = tk.Frame(self.main, bg=C["bg"])
        ward_frame.pack(fill="x", padx=30, pady=(0, 10))

        for i, w in enumerate(wards):
            card = tk.Frame(ward_frame, bg=C["card"], padx=12, pady=10)
            card.grid(row=i // 4, column=i % 4, padx=4, pady=4, sticky="nsew")
            ward_frame.grid_columnconfigure(i % 4, weight=1)

            available = w[3] or 0
            occupied = w[4] or 0
            color = C["success"] if available > 0 else C["danger"]

            tk.Label(card, text=w[0], bg=C["card"], fg=C["primary"],
                     font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(card, text=f"{available} free / {occupied} occupied",
                     bg=C["card"], fg=color, font=("Segoe UI", 9)).pack(anchor="w")
            tk.Label(card, text=f"Rs {w[5]:,.0f}/day", bg=C["card"], fg=C["text_muted"],
                     font=("Segoe UI", 8)).pack(anchor="w")

        # Bed list
        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        cols = ("Bed No", "Ward", "Status", "Patient", "Admission Date", "Doctor")
        self.bed_tree = ttk.Treeview(tf, columns=cols, show="headings", height=12)
        for col, w in zip(cols, [80, 140, 80, 150, 110, 130]):
            self.bed_tree.heading(col, text=col)
            self.bed_tree.column(col, width=w, minwidth=40)

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT bed_no, ward_name, status, patient_name, admission_date, doctor_id FROM beds ORDER BY ward_name, bed_no")
        for r in c.fetchall():
            self.bed_tree.insert("", "end", values=(r[0], r[1], r[2], r[3] or "-", r[4] or "-", r[5] or "-"))
        conn.close()
        self.bed_tree.pack(fill="both", expand=True)
        self.bed_tree.bind("<Double-1>", lambda e: self._discharge_patient())

        tk.Label(tf, text="Double-click occupied bed to discharge patient",
                 bg=C["card"], fg=C["text_muted"], font=F["body_small"]).pack(pady=3)

    def _admit_patient(self):
        d = tk.Toplevel(self.root)
        d.title("Admit Patient")
        d.geometry("450x350")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Admit Patient (IPD)", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(15, 10))

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

        tk.Label(form, text="Patient", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(8, 2))
        pat_var = tk.StringVar()
        ttk.Combobox(form, textvariable=pat_var,
                      values=[f"{p[0]} - {p[1]}" for p in patients], state="readonly").pack(fill="x", ipady=3)

        tk.Label(form, text="Available Bed", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(8, 2))
        bed_var = tk.StringVar()
        ttk.Combobox(form, textvariable=bed_var,
                      values=[f"{b[0]} ({b[1]})" for b in beds], state="readonly").pack(fill="x", ipady=3)

        tk.Label(form, text="Attending Doctor", bg=C["bg"], fg=C["text_secondary"]).pack(anchor="w", pady=(8, 2))
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
                d.destroy()
                self._show_beds()
                messagebox.showinfo("Admitted", f"{pat_parts[1]} admitted to {bed_no}")
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Admit", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=12)

    def _discharge_patient(self):
        sel = self.bed_tree.selection()
        if not sel:
            return
        vals = self.bed_tree.item(sel[0])["values"]
        if vals[2] != "Occupied":
            return

        if messagebox.askyesno("Discharge", f"Discharge {vals[3]} from bed {vals[0]}?"):
            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("""UPDATE beds SET status='Available', patient_id='', patient_name='',
                            admission_date='', doctor_id='' WHERE bed_no=?""", (vals[0],))
                conn.commit()
                self._show_beds()
            finally:
                conn.close()

    # ============================== BILLING ==============================

    def _show_billing(self):
        self._clear()
        self._set_active("billing")
        h = self._header("Billing", "Invoices & Payments")

        tk.Button(h, text="+ Create Bill", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=15, pady=5,
                  command=self._create_bill, cursor="hand2").pack(side="right")

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        cols = ("Bill No", "Patient", "Type", "Consultation", "Lab", "Pharmacy", "Bed", "Total", "Paid", "Status")
        tree = ttk.Treeview(tf, columns=cols, show="headings", height=18)
        for col, w in zip(cols, [85, 130, 50, 85, 70, 75, 70, 90, 80, 70]):
            tree.heading(col, text=col)
            tree.column(col, width=w, minwidth=40)

        conn = get_conn()
        c = conn.cursor()
        c.execute("""SELECT bill_no, patient_name, bill_type, consultation_fee, lab_charges, pharmacy_charges,
                    bed_charges, grand_total, paid, payment_status FROM bills ORDER BY id DESC""")
        for r in c.fetchall():
            tree.insert("", "end", values=(r[0], r[1], r[2], f"Rs {r[3]:,.0f}", f"Rs {r[4]:,.0f}",
                                           f"Rs {r[5]:,.0f}", f"Rs {r[6]:,.0f}", f"Rs {r[7]:,.0f}",
                                           f"Rs {r[8]:,.0f}", r[9]))
        conn.close()
        tree.pack(fill="both", expand=True)

    def _create_bill(self):
        d = tk.Toplevel(self.root)
        d.title("Create Bill")
        d.geometry("500x520")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Create Bill / Invoice", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(15, 10))

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT patient_id, name FROM patients WHERE status='Active'")
        patients = c.fetchall()
        conn.close()

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)
        form.grid_columnconfigure(1, weight=1)

        bill_no = f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        tk.Label(form, text="Patient", bg=C["bg"], fg=C["text_secondary"]).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        pat_var = tk.StringVar()
        ttk.Combobox(form, textvariable=pat_var,
                      values=[f"{p[0]} - {p[1]}" for p in patients],
                      state="readonly").grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(form, text="Type", bg=C["bg"], fg=C["text_secondary"]).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        type_var = tk.StringVar(value="OPD")
        ttk.Combobox(form, textvariable=type_var, values=["OPD", "IPD", "Emergency"],
                      state="readonly").grid(row=1, column=1, sticky="ew", padx=5, pady=5)

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

        tk.Label(form, text="Payment", bg=C["bg"], fg=C["text_secondary"]).grid(row=8, column=0, sticky="w", padx=5, pady=5)
        pay_var = tk.StringVar(value="Cash")
        ttk.Combobox(form, textvariable=pay_var, values=["Cash", "Card", "Online", "Insurance", "Credit"],
                      state="readonly").grid(row=8, column=1, sticky="ew", padx=5, pady=5)

        def save():
            if not pat_var.get():
                messagebox.showerror("Error", "Select patient!")
                return
            pat_parts = pat_var.get().split(" - ")

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
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (bill_no, pat_parts[0], pat_parts[1], type_var.get(),
                          consult, lab, pharma, bed, other, subtotal, discount, grand,
                          grand, 0, pay_var.get(), "Paid"))
                conn.commit()
                d.destroy()
                self._show_billing()
                messagebox.showinfo("Bill Created", f"Bill: {bill_no}\nTotal: Rs {grand:,.0f}")
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                conn.close()

        tk.Button(d, text="Generate Bill", bg=C["accent"], fg="black",
                  font=F["button"], relief="flat", padx=20, pady=7,
                  command=save, cursor="hand2").pack(pady=12)

    # ============================== REPORTS ==============================

    def _show_reports(self):
        self._clear()
        self._set_active("reports")
        h = self._header("Reports & Analytics", "Business Intelligence")

        tk.Button(h, text="Export All Data", bg=C["primary"], fg="white",
                  font=F["button"], relief="flat", padx=15, pady=5,
                  command=self._export_all, cursor="hand2").pack(side="right")

        if not MATPLOTLIB_AVAILABLE:
            tk.Label(self.main, text="Install matplotlib for charts:\npip install matplotlib",
                     bg=C["bg"], fg=C["warning"], font=("Segoe UI", 14)).pack(pady=50)
            return

        conn = get_conn()
        c = conn.cursor()

        # Revenue last 7 days
        dates, revenues = [], []
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            c.execute("SELECT COALESCE(SUM(grand_total), 0) FROM bills WHERE created_at LIKE ?", (f"{date}%",))
            bill_rev = c.fetchone()[0]
            c.execute("SELECT COALESCE(SUM(total), 0) FROM pharmacy_sales WHERE created_at LIKE ?", (f"{date}%",))
            pharma_rev = c.fetchone()[0]
            revenues.append(bill_rev + pharma_rev)
            dates.append((datetime.now() - timedelta(days=i)).strftime("%d/%m"))

        # Department patient distribution
        c.execute("""SELECT department, COUNT(*) FROM appointments
                    GROUP BY department ORDER BY COUNT(*) DESC LIMIT 6""")
        dept_data = c.fetchall()

        # Payment methods
        c.execute("SELECT payment_method, COUNT(*) FROM bills GROUP BY payment_method")
        pay_data = c.fetchall()

        conn.close()

        fig = Figure(figsize=(10, 5), facecolor=C["bg"])

        # Revenue chart
        ax1 = fig.add_subplot(131)
        ax1.set_facecolor(C["card"])
        ax1.bar(dates, revenues, color=C["accent"])
        ax1.set_title("7-Day Revenue", color=C["text"], fontsize=10)
        ax1.tick_params(colors=C["text_muted"], labelsize=7)
        for spine in ax1.spines.values():
            spine.set_color(C["border"])

        # Department pie
        if dept_data:
            ax2 = fig.add_subplot(132)
            labels = [d[0] or "Other" for d in dept_data]
            vals = [d[1] for d in dept_data]
            ax2.pie(vals, labels=labels, autopct="%1.0f%%", textprops={"color": C["text"], "fontsize": 8})
            ax2.set_title("Patients by Dept", color=C["text"], fontsize=10)

        # Payment pie
        if pay_data:
            ax3 = fig.add_subplot(133)
            labels = [p[0] for p in pay_data]
            vals = [p[1] for p in pay_data]
            ax3.pie(vals, labels=labels, autopct="%1.0f%%", textprops={"color": C["text"], "fontsize": 8})
            ax3.set_title("Payment Methods", color=C["text"], fontsize=10)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, self.main)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=30, pady=(0, 20))

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

        # Patients
        ws = wb.active
        ws.title = "Patients"
        ws.append(["ID", "Name", "Father", "CNIC", "Age", "Gender", "Phone", "Type", "Blood", "Status"])
        c.execute("SELECT patient_id, name, father_name, cnic, age, gender, phone, patient_type, blood_group, status FROM patients")
        for r in c.fetchall():
            ws.append(list(r))

        # Doctors
        ws2 = wb.create_sheet("Doctors")
        ws2.append(["ID", "Name", "Specialization", "Department", "Qualification", "Fee", "Phone", "Schedule", "Status"])
        c.execute("SELECT doctor_id, name, specialization, department, qualification, fee, phone, schedule, status FROM doctors")
        for r in c.fetchall():
            ws2.append(list(r))

        # Appointments
        ws3 = wb.create_sheet("Appointments")
        ws3.append(["Token", "Patient", "Doctor", "Department", "Date", "Time", "Fee", "Status"])
        c.execute("SELECT token_no, patient_name, doctor_name, department, date, time, fee, status FROM appointments ORDER BY date DESC")
        for r in c.fetchall():
            ws3.append(list(r))

        # Medicines
        ws4 = wb.create_sheet("Medicines")
        ws4.append(["Name", "Generic", "Category", "Price", "Stock", "Min Stock", "Expiry", "Manufacturer"])
        c.execute("SELECT name, generic_name, category, price, stock, min_stock, expiry_date, manufacturer FROM medicines")
        for r in c.fetchall():
            ws4.append(list(r))

        # Bills
        ws5 = wb.create_sheet("Bills")
        ws5.append(["Bill No", "Patient", "Type", "Consultation", "Lab", "Pharmacy", "Bed", "Total", "Paid", "Status"])
        c.execute("SELECT bill_no, patient_name, bill_type, consultation_fee, lab_charges, pharmacy_charges, bed_charges, grand_total, paid, payment_status FROM bills")
        for r in c.fetchall():
            ws5.append(list(r))

        # Lab Tests
        ws6 = wb.create_sheet("Lab Tests")
        ws6.append(["Test ID", "Patient", "Doctor", "Test", "Category", "Fee", "Result", "Status", "Date"])
        c.execute("SELECT test_id, patient_name, doctor_name, test_name, test_category, fee, result, status, created_at FROM lab_tests")
        for r in c.fetchall():
            ws6.append(list(r))

        conn.close()
        wb.save(fp)
        messagebox.showinfo("Exported!", f"All hospital data saved to:\n{fp}")

    # ============================== RUN ==============================

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = HospitalApp()
    app.run()
