"""
Employee Management System - Professional HR Software
By: Matrix Tech Solutions (Fiverr Portfolio)

Features:
- Employee Database (Add, Edit, Delete, Search)
- Attendance Tracking (Check-in/Check-out)
- Salary Management (Basic + Allowances + Deductions)
- Leave Management (Apply, Approve, Reject)
- Department Management
- Monthly Payroll Reports
- Attendance Reports with Charts
- Data Export to Excel
- Professional Dark Theme
- SQLite Database

This is a COMPLETE HR management application.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
import calendar

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# ============ DATABASE ============

DB_FILE = "employees.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        head TEXT DEFAULT ''
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT UNIQUE,
        name TEXT NOT NULL,
        email TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        department TEXT DEFAULT '',
        designation TEXT DEFAULT '',
        join_date TEXT DEFAULT '',
        basic_salary REAL DEFAULT 0,
        allowances REAL DEFAULT 0,
        status TEXT DEFAULT 'Active',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT,
        date TEXT,
        check_in TEXT DEFAULT '',
        check_out TEXT DEFAULT '',
        status TEXT DEFAULT 'Present',
        hours REAL DEFAULT 0,
        UNIQUE(emp_id, date)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS leaves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT,
        emp_name TEXT,
        leave_type TEXT DEFAULT 'Casual',
        start_date TEXT,
        end_date TEXT,
        days INTEGER DEFAULT 1,
        reason TEXT DEFAULT '',
        status TEXT DEFAULT 'Pending',
        applied_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS payroll (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT,
        emp_name TEXT,
        month TEXT,
        basic REAL DEFAULT 0,
        allowances REAL DEFAULT 0,
        deductions REAL DEFAULT 0,
        net_salary REAL DEFAULT 0,
        status TEXT DEFAULT 'Pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # Default departments
    defaults = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"]
    for dept in defaults:
        try:
            c.execute("INSERT OR IGNORE INTO departments (name) VALUES (?)", (dept,))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()


# ============ COLORS ============

C = {
    "bg": "#0d1117",
    "sidebar": "#161b22",
    "card": "#1c2128",
    "primary": "#79c0ff",
    "success": "#56d364",
    "warning": "#e3b341",
    "danger": "#f85149",
    "purple": "#bc8cff",
    "text": "#e6edf3",
    "muted": "#8b949e",
    "border": "#30363d",
    "input": "#0d1117",
}


# ============ APPLICATION ============

class EmployeeApp:
    def __init__(self):
        init_db()

        self.root = tk.Tk()
        self.root.title("Employee Management System — Matrix Tech")
        self.root.geometry("1200x750")
        self.root.configure(bg=C["bg"])
        self.root.minsize(1000, 600)

        self._create_sidebar()
        self._create_main()
        self._show_dashboard()

    def _create_sidebar(self):
        sb = tk.Frame(self.root, bg=C["sidebar"], width=210)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        tk.Label(sb, text="HR MANAGER", bg=C["sidebar"], fg=C["primary"],
                 font=("Segoe UI", 17, "bold")).pack(pady=(25, 3))
        tk.Label(sb, text="Employee Management", bg=C["sidebar"], fg=C["muted"],
                 font=("Segoe UI", 9)).pack(pady=(0, 30))

        menus = [
            ("Dashboard", "dash", self._show_dashboard),
            ("Employees", "emp", self._show_employees),
            ("Attendance", "att", self._show_attendance),
            ("Leave Mgmt", "leave", self._show_leaves),
            ("Payroll", "pay", self._show_payroll),
            ("Departments", "dept", self._show_departments),
            ("Reports", "report", self._show_reports),
        ]

        self.btns = {}
        for text, key, cmd in menus:
            btn = tk.Button(sb, text=f"  {text}", bg=C["sidebar"], fg=C["muted"],
                            font=("Segoe UI", 11), relief="flat", anchor="w", padx=18, pady=7,
                            activebackground=C["card"], cursor="hand2", command=cmd)
            btn.pack(fill="x", padx=8, pady=2)
            self.btns[key] = btn

        tk.Label(sb, text="Matrix Tech Solutions", bg=C["sidebar"],
                 fg=C["muted"], font=("Segoe UI", 8)).pack(side="bottom", pady=12)

    def _active(self, key):
        for k, b in self.btns.items():
            b.configure(bg=C["card"] if k == key else C["sidebar"],
                        fg=C["primary"] if k == key else C["muted"])

    def _create_main(self):
        self.main = tk.Frame(self.root, bg=C["bg"])
        self.main.pack(side="right", fill="both", expand=True)

    def _clear(self):
        for w in self.main.winfo_children():
            w.destroy()

    def _header(self, title, sub=""):
        h = tk.Frame(self.main, bg=C["bg"])
        h.pack(fill="x", padx=25, pady=(20, 12))
        tk.Label(h, text=title, bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 20, "bold")).pack(side="left")
        if sub:
            tk.Label(h, text=sub, bg=C["bg"], fg=C["muted"],
                     font=("Segoe UI", 10)).pack(side="left", padx=15, pady=(6, 0))
        return h

    # ============ DASHBOARD ============

    def _show_dashboard(self):
        self._clear()
        self._active("dash")
        self._header("Dashboard", "HR Overview")

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM employees WHERE status='Active'")
        active = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM employees")
        total = c.fetchone()[0]

        today = datetime.now().strftime("%Y-%m-%d")
        c.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND status='Present'", (today,))
        present = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM leaves WHERE status='Pending'")
        pending_leaves = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM departments")
        depts = c.fetchone()[0]

        month = datetime.now().strftime("%Y-%m")
        c.execute("SELECT COALESCE(SUM(net_salary), 0) FROM payroll WHERE month=?", (month,))
        payroll_total = c.fetchone()[0]

        conn.close()

        cards = tk.Frame(self.main, bg=C["bg"])
        cards.pack(fill="x", padx=25, pady=8)

        stats = [
            ("Active Employees", str(active), C["success"]),
            ("Present Today", str(present), C["primary"]),
            ("Pending Leaves", str(pending_leaves), C["warning"]),
            ("Departments", str(depts), C["purple"]),
            ("Total Employees", str(total), C["primary"]),
            ("This Month Payroll", f"Rs {payroll_total:,.0f}", C["success"]),
        ]

        for i, (label, val, color) in enumerate(stats):
            card = tk.Frame(cards, bg=C["card"], padx=18, pady=13)
            card.grid(row=i // 3, column=i % 3, padx=6, pady=6, sticky="nsew")
            cards.grid_columnconfigure(i % 3, weight=1)
            tk.Label(card, text=val, bg=C["card"], fg=color,
                     font=("Segoe UI", 22, "bold")).pack(anchor="w")
            tk.Label(card, text=label, bg=C["card"], fg=C["muted"],
                     font=("Segoe UI", 10)).pack(anchor="w")

        # Recent activity
        recent = tk.Frame(self.main, bg=C["card"], padx=18, pady=13)
        recent.pack(fill="both", expand=True, padx=25, pady=(10, 20))

        tk.Label(recent, text="Recent Attendance", bg=C["card"], fg=C["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""SELECT a.emp_id, e.name, a.date, a.check_in, a.check_out, a.status
                    FROM attendance a LEFT JOIN employees e ON a.emp_id = e.emp_id
                    ORDER BY a.id DESC LIMIT 10""")
        rows = c.fetchall()
        conn.close()

        if rows:
            cols = ("Emp ID", "Name", "Date", "Check In", "Check Out", "Status")
            tree = ttk.Treeview(recent, columns=cols, show="headings", height=8)
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=110)
            for r in rows:
                tree.insert("", "end", values=r)
            tree.pack(fill="both", expand=True)
        else:
            tk.Label(recent, text="No attendance records yet.", bg=C["card"],
                     fg=C["muted"], font=("Segoe UI", 11)).pack(pady=25)

    # ============ EMPLOYEES ============

    def _show_employees(self):
        self._clear()
        self._active("emp")
        h = self._header("Employees", "Manage employee records")

        tk.Button(h, text="+ Add Employee", bg=C["success"], fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=4,
                  cursor="hand2", command=self._add_employee).pack(side="right")

        # Search
        sf = tk.Frame(self.main, bg=C["bg"])
        sf.pack(fill="x", padx=25, pady=(0, 8))
        self.emp_search = tk.Entry(sf, bg=C["input"], fg=C["text"], font=("Segoe UI", 11),
                                    relief="flat", insertbackground=C["text"])
        self.emp_search.pack(side="left", fill="x", expand=True, ipady=7)
        self.emp_search.insert(0, "Search by name, ID, department...")
        self.emp_search.bind("<FocusIn>", lambda e: self.emp_search.delete(0, "end") if "Search" in self.emp_search.get() else None)
        self.emp_search.bind("<KeyRelease>", lambda e: self._load_employees())

        # Table
        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        cols = ("Emp ID", "Name", "Department", "Designation", "Salary", "Status", "Join Date")
        self.emp_tree = ttk.Treeview(tf, columns=cols, show="headings", height=16)
        for col, w in zip(cols, [80, 160, 120, 130, 100, 80, 100]):
            self.emp_tree.heading(col, text=col)
            self.emp_tree.column(col, width=w)

        sb = ttk.Scrollbar(tf, orient="vertical", command=self.emp_tree.yview)
        self.emp_tree.configure(yscrollcommand=sb.set)
        self.emp_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.emp_tree.bind("<Double-1>", lambda e: self._edit_employee())

        self._load_employees()

    def _load_employees(self):
        search = self.emp_search.get().strip()
        if "Search" in search:
            search = ""

        for item in self.emp_tree.get_children():
            self.emp_tree.delete(item)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        if search:
            c.execute("""SELECT emp_id, name, department, designation, basic_salary, status, join_date
                        FROM employees WHERE name LIKE ? OR emp_id LIKE ? OR department LIKE ?""",
                       (f"%{search}%", f"%{search}%", f"%{search}%"))
        else:
            c.execute("SELECT emp_id, name, department, designation, basic_salary, status, join_date FROM employees ORDER BY id DESC")

        for r in c.fetchall():
            self.emp_tree.insert("", "end", values=(r[0], r[1], r[2], r[3], f"Rs {r[4]:,.0f}", r[5], r[6]))
        conn.close()

    def _add_employee(self):
        d = tk.Toplevel(self.root)
        d.title("Add Employee")
        d.geometry("480x580")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Add New Employee", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(18, 12))

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT name FROM departments")
        dept_list = [r[0] for r in c.fetchall()]
        conn.close()

        fields = {}
        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=28)

        for label, key, default in [
            ("Employee ID", "emp_id", f"EMP-{datetime.now().strftime('%Y%m%d%H%M')}"),
            ("Full Name", "name", ""),
            ("Email", "email", ""),
            ("Phone", "phone", ""),
            ("Designation", "designation", ""),
            ("Join Date", "join_date", datetime.now().strftime("%Y-%m-%d")),
            ("Basic Salary (Rs)", "basic_salary", "0"),
            ("Allowances (Rs)", "allowances", "0"),
        ]:
            tk.Label(form, text=label, bg=C["bg"], fg=C["muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(6, 1))
            e = tk.Entry(form, bg=C["input"], fg=C["text"], font=("Segoe UI", 10),
                         relief="flat", insertbackground=C["text"])
            e.pack(fill="x", ipady=4)
            e.insert(0, default)
            fields[key] = e

        tk.Label(form, text="Department", bg=C["bg"], fg=C["muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(6, 1))
        dept_var = tk.StringVar(value=dept_list[0] if dept_list else "")
        dept_combo = ttk.Combobox(form, textvariable=dept_var, values=dept_list, state="readonly")
        dept_combo.pack(fill="x", ipady=2)

        def save():
            name = fields["name"].get().strip()
            eid = fields["emp_id"].get().strip()
            if not name or not eid:
                messagebox.showerror("Error", "Employee ID and Name required!")
                return
            try:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("""INSERT INTO employees (emp_id, name, email, phone, department, designation, join_date, basic_salary, allowances)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (eid, name, fields["email"].get(), fields["phone"].get(), dept_var.get(),
                          fields["designation"].get(), fields["join_date"].get(),
                          float(fields["basic_salary"].get() or 0), float(fields["allowances"].get() or 0)))
                conn.commit()
                conn.close()
                d.destroy()
                self._load_employees()
                messagebox.showinfo("Success", f"Employee '{name}' added!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Employee ID already exists!")
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        tk.Button(d, text="Save Employee", bg=C["success"], fg="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", padx=18, pady=6,
                  command=save, cursor="hand2").pack(pady=15)

    def _edit_employee(self):
        sel = self.emp_tree.selection()
        if not sel:
            return
        eid = self.emp_tree.item(sel[0])["values"][0]

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM employees WHERE emp_id=?", (eid,))
        emp = c.fetchone()
        c.execute("SELECT name FROM departments")
        depts = [r[0] for r in c.fetchall()]
        conn.close()

        if not emp:
            return

        d = tk.Toplevel(self.root)
        d.title(f"Edit {emp[2]}")
        d.geometry("480x580")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text=f"Edit: {emp[2]}", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 15, "bold")).pack(pady=(18, 12))

        fields = {}
        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=28)

        for label, key, val in [
            ("Name", "name", emp[2]),
            ("Email", "email", emp[3] or ""),
            ("Phone", "phone", emp[4] or ""),
            ("Designation", "designation", emp[6] or ""),
            ("Join Date", "join_date", emp[7] or ""),
            ("Basic Salary", "basic_salary", str(emp[8])),
            ("Allowances", "allowances", str(emp[9])),
        ]:
            tk.Label(form, text=label, bg=C["bg"], fg=C["muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(6, 1))
            e = tk.Entry(form, bg=C["input"], fg=C["text"], font=("Segoe UI", 10),
                         relief="flat", insertbackground=C["text"])
            e.pack(fill="x", ipady=4)
            e.insert(0, val)
            fields[key] = e

        tk.Label(form, text="Department", bg=C["bg"], fg=C["muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(6, 1))
        dept_var = tk.StringVar(value=emp[5] or "")
        ttk.Combobox(form, textvariable=dept_var, values=depts, state="readonly").pack(fill="x", ipady=2)

        tk.Label(form, text="Status", bg=C["bg"], fg=C["muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(6, 1))
        status_var = tk.StringVar(value=emp[10] or "Active")
        ttk.Combobox(form, textvariable=status_var, values=["Active", "Inactive", "On Leave", "Terminated"],
                      state="readonly").pack(fill="x", ipady=2)

        def save():
            try:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("""UPDATE employees SET name=?, email=?, phone=?, department=?, designation=?,
                            join_date=?, basic_salary=?, allowances=?, status=? WHERE emp_id=?""",
                         (fields["name"].get(), fields["email"].get(), fields["phone"].get(),
                          dept_var.get(), fields["designation"].get(), fields["join_date"].get(),
                          float(fields["basic_salary"].get() or 0), float(fields["allowances"].get() or 0),
                          status_var.get(), eid))
                conn.commit()
                conn.close()
                d.destroy()
                self._load_employees()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        def delete():
            if messagebox.askyesno("Confirm", f"Delete employee {emp[2]}?"):
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("DELETE FROM employees WHERE emp_id=?", (eid,))
                conn.commit()
                conn.close()
                d.destroy()
                self._load_employees()

        bf = tk.Frame(d, bg=C["bg"])
        bf.pack(pady=12)
        tk.Button(bf, text="Save", bg=C["success"], fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=15, pady=5, command=save, cursor="hand2").pack(side="left", padx=4)
        tk.Button(bf, text="Delete", bg=C["danger"], fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=15, pady=5, command=delete, cursor="hand2").pack(side="left", padx=4)

    # ============ ATTENDANCE ============

    def _show_attendance(self):
        self._clear()
        self._active("att")
        h = self._header("Attendance", "Track employee attendance")

        tk.Button(h, text="Mark Attendance", bg=C["success"], fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=4,
                  cursor="hand2", command=self._mark_attendance).pack(side="right")

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        cols = ("Emp ID", "Name", "Date", "Check In", "Check Out", "Hours", "Status")
        tree = ttk.Treeview(tf, columns=cols, show="headings", height=18)
        for col, w in zip(cols, [80, 150, 100, 90, 90, 70, 90]):
            tree.heading(col, text=col)
            tree.column(col, width=w)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""SELECT a.emp_id, e.name, a.date, a.check_in, a.check_out, a.hours, a.status
                    FROM attendance a LEFT JOIN employees e ON a.emp_id = e.emp_id
                    ORDER BY a.date DESC, a.id DESC LIMIT 50""")
        for r in c.fetchall():
            tree.insert("", "end", values=r)
        conn.close()
        tree.pack(fill="both", expand=True)

    def _mark_attendance(self):
        d = tk.Toplevel(self.root)
        d.title("Mark Attendance")
        d.geometry("400x400")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Mark Attendance", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 14, "bold")).pack(pady=(15, 10))

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT emp_id, name FROM employees WHERE status='Active'")
        emps = c.fetchall()
        conn.close()

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)

        tk.Label(form, text="Employee", bg=C["bg"], fg=C["muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 2))
        emp_var = tk.StringVar()
        emp_vals = [f"{e[0]} - {e[1]}" for e in emps]
        ttk.Combobox(form, textvariable=emp_var, values=emp_vals, state="readonly").pack(fill="x", ipady=3)

        tk.Label(form, text="Date", bg=C["bg"], fg=C["muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 2))
        date_entry = tk.Entry(form, bg=C["input"], fg=C["text"], font=("Segoe UI", 10), relief="flat")
        date_entry.pack(fill="x", ipady=4)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(form, text="Check In", bg=C["bg"], fg=C["muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 2))
        checkin = tk.Entry(form, bg=C["input"], fg=C["text"], font=("Segoe UI", 10), relief="flat")
        checkin.pack(fill="x", ipady=4)
        checkin.insert(0, "09:00")

        tk.Label(form, text="Check Out", bg=C["bg"], fg=C["muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 2))
        checkout = tk.Entry(form, bg=C["input"], fg=C["text"], font=("Segoe UI", 10), relief="flat")
        checkout.pack(fill="x", ipady=4)
        checkout.insert(0, "17:00")

        tk.Label(form, text="Status", bg=C["bg"], fg=C["muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 2))
        status_var = tk.StringVar(value="Present")
        ttk.Combobox(form, textvariable=status_var, values=["Present", "Absent", "Late", "Half Day", "Work from Home"],
                      state="readonly").pack(fill="x", ipady=3)

        def save():
            if not emp_var.get():
                messagebox.showerror("Error", "Select an employee!")
                return
            eid = emp_var.get().split(" - ")[0]
            try:
                ci = checkin.get()
                co = checkout.get()
                hours = 0
                if ci and co:
                    t1 = datetime.strptime(ci, "%H:%M")
                    t2 = datetime.strptime(co, "%H:%M")
                    hours = round((t2 - t1).seconds / 3600, 1)

                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("""INSERT OR REPLACE INTO attendance (emp_id, date, check_in, check_out, status, hours)
                            VALUES (?, ?, ?, ?, ?, ?)""",
                         (eid, date_entry.get(), ci, co, status_var.get(), hours))
                conn.commit()
                conn.close()
                d.destroy()
                self._show_attendance()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        tk.Button(d, text="Save", bg=C["success"], fg="white", font=("Segoe UI", 11, "bold"),
                  relief="flat", padx=18, pady=6, command=save, cursor="hand2").pack(pady=12)

    # ============ LEAVE MANAGEMENT ============

    def _show_leaves(self):
        self._clear()
        self._active("leave")
        h = self._header("Leave Management", "Apply and manage leaves")

        tk.Button(h, text="+ Apply Leave", bg=C["success"], fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=4,
                  cursor="hand2", command=self._apply_leave).pack(side="right")

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        cols = ("ID", "Emp Name", "Type", "From", "To", "Days", "Reason", "Status")
        self.leave_tree = ttk.Treeview(tf, columns=cols, show="headings", height=16)
        for col, w in zip(cols, [40, 130, 80, 90, 90, 50, 160, 80]):
            self.leave_tree.heading(col, text=col)
            self.leave_tree.column(col, width=w)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, emp_name, leave_type, start_date, end_date, days, reason, status FROM leaves ORDER BY id DESC")
        for r in c.fetchall():
            self.leave_tree.insert("", "end", values=r)
        conn.close()
        self.leave_tree.pack(fill="both", expand=True)
        self.leave_tree.bind("<Double-1>", lambda e: self._approve_leave())

        tk.Label(tf, text="Double-click a pending leave to approve/reject", bg=C["card"],
                 fg=C["muted"], font=("Segoe UI", 9)).pack(pady=3)

    def _apply_leave(self):
        d = tk.Toplevel(self.root)
        d.title("Apply Leave")
        d.geometry("400x420")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Apply for Leave", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 14, "bold")).pack(pady=(15, 10))

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT emp_id, name FROM employees WHERE status='Active'")
        emps = c.fetchall()
        conn.close()

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)

        tk.Label(form, text="Employee", bg=C["bg"], fg=C["muted"]).pack(anchor="w", pady=(8, 2))
        emp_var = tk.StringVar()
        ttk.Combobox(form, textvariable=emp_var, values=[f"{e[0]} - {e[1]}" for e in emps],
                      state="readonly").pack(fill="x", ipady=3)

        tk.Label(form, text="Leave Type", bg=C["bg"], fg=C["muted"]).pack(anchor="w", pady=(8, 2))
        type_var = tk.StringVar(value="Casual")
        ttk.Combobox(form, textvariable=type_var, values=["Casual", "Sick", "Annual", "Maternity", "Unpaid"],
                      state="readonly").pack(fill="x", ipady=3)

        tk.Label(form, text="Start Date", bg=C["bg"], fg=C["muted"]).pack(anchor="w", pady=(8, 2))
        start = tk.Entry(form, bg=C["input"], fg=C["text"], font=("Segoe UI", 10), relief="flat")
        start.pack(fill="x", ipady=4)
        start.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(form, text="End Date", bg=C["bg"], fg=C["muted"]).pack(anchor="w", pady=(8, 2))
        end = tk.Entry(form, bg=C["input"], fg=C["text"], font=("Segoe UI", 10), relief="flat")
        end.pack(fill="x", ipady=4)
        end.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(form, text="Reason", bg=C["bg"], fg=C["muted"]).pack(anchor="w", pady=(8, 2))
        reason = tk.Entry(form, bg=C["input"], fg=C["text"], font=("Segoe UI", 10), relief="flat")
        reason.pack(fill="x", ipady=4)

        def save():
            if not emp_var.get():
                messagebox.showerror("Error", "Select employee!")
                return
            parts = emp_var.get().split(" - ")
            eid = parts[0]
            ename = parts[1] if len(parts) > 1 else ""
            try:
                s = datetime.strptime(start.get(), "%Y-%m-%d")
                e_date = datetime.strptime(end.get(), "%Y-%m-%d")
                days = (e_date - s).days + 1

                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("""INSERT INTO leaves (emp_id, emp_name, leave_type, start_date, end_date, days, reason)
                            VALUES (?, ?, ?, ?, ?, ?, ?)""",
                         (eid, ename, type_var.get(), start.get(), end.get(), days, reason.get()))
                conn.commit()
                conn.close()
                d.destroy()
                self._show_leaves()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        tk.Button(d, text="Submit", bg=C["success"], fg="white", font=("Segoe UI", 11, "bold"),
                  relief="flat", padx=18, pady=6, command=save, cursor="hand2").pack(pady=12)

    def _approve_leave(self):
        sel = self.leave_tree.selection()
        if not sel:
            return
        vals = self.leave_tree.item(sel[0])["values"]
        lid = vals[0]
        status = vals[7]

        if status != "Pending":
            messagebox.showinfo("Info", f"Leave already {status}.")
            return

        result = messagebox.askyesnocancel("Leave Decision",
                                            f"Leave #{lid} for {vals[1]}\n\nYes = Approve\nNo = Reject\nCancel = Close")
        if result is None:
            return

        new_status = "Approved" if result else "Rejected"
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE leaves SET status=? WHERE id=?", (new_status, lid))
        conn.commit()
        conn.close()
        self._show_leaves()

    # ============ PAYROLL ============

    def _show_payroll(self):
        self._clear()
        self._active("pay")
        h = self._header("Payroll", "Monthly salary management")

        tk.Button(h, text="Generate Payroll", bg=C["success"], fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=4,
                  cursor="hand2", command=self._generate_payroll).pack(side="right")

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        cols = ("ID", "Emp ID", "Name", "Month", "Basic", "Allowances", "Deductions", "Net Salary", "Status")
        tree = ttk.Treeview(tf, columns=cols, show="headings", height=16)
        for col, w in zip(cols, [40, 80, 140, 80, 90, 90, 90, 100, 80]):
            tree.heading(col, text=col)
            tree.column(col, width=w)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, emp_id, emp_name, month, basic, allowances, deductions, net_salary, status FROM payroll ORDER BY id DESC")
        for r in c.fetchall():
            tree.insert("", "end", values=(r[0], r[1], r[2], r[3],
                                           f"Rs {r[4]:,.0f}", f"Rs {r[5]:,.0f}",
                                           f"Rs {r[6]:,.0f}", f"Rs {r[7]:,.0f}", r[8]))
        conn.close()
        tree.pack(fill="both", expand=True)

    def _generate_payroll(self):
        month = datetime.now().strftime("%Y-%m")

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM payroll WHERE month=?", (month,))
        if c.fetchone()[0] > 0:
            if not messagebox.askyesno("Warning", f"Payroll for {month} already exists. Regenerate?"):
                conn.close()
                return
            c.execute("DELETE FROM payroll WHERE month=?", (month,))

        c.execute("SELECT emp_id, name, basic_salary, allowances FROM employees WHERE status='Active'")
        employees = c.fetchall()

        count = 0
        for emp in employees:
            eid, name, basic, allowances = emp

            # Calculate deductions based on attendance
            c.execute("SELECT COUNT(*) FROM attendance WHERE emp_id=? AND date LIKE ? AND status='Absent'",
                       (eid, f"{month}%"))
            absent_days = c.fetchone()[0]
            daily_rate = basic / 30
            deductions = round(absent_days * daily_rate, 0)
            net = basic + allowances - deductions

            c.execute("""INSERT INTO payroll (emp_id, emp_name, month, basic, allowances, deductions, net_salary, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'Generated')""",
                     (eid, name, month, basic, allowances, deductions, net))
            count += 1

        conn.commit()
        conn.close()
        messagebox.showinfo("Payroll Generated", f"Generated payroll for {count} employees\nMonth: {month}")
        self._show_payroll()

    # ============ DEPARTMENTS ============

    def _show_departments(self):
        self._clear()
        self._active("dept")
        h = self._header("Departments", "Manage departments")

        tk.Button(h, text="+ Add Department", bg=C["success"], fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=4,
                  cursor="hand2", command=self._add_department).pack(side="right")

        tf = tk.Frame(self.main, bg=C["card"])
        tf.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT d.id, d.name, d.head, COUNT(e.id) FROM departments d LEFT JOIN employees e ON d.name = e.department GROUP BY d.id ORDER BY d.name")
        depts = c.fetchall()
        conn.close()

        cols = ("ID", "Department", "Head", "Employees")
        tree = ttk.Treeview(tf, columns=cols, show="headings", height=16)
        for col, w in zip(cols, [50, 200, 200, 100]):
            tree.heading(col, text=col)
            tree.column(col, width=w)

        for d in depts:
            tree.insert("", "end", values=d)
        tree.pack(fill="both", expand=True)

    def _add_department(self):
        d = tk.Toplevel(self.root)
        d.title("Add Department")
        d.geometry("350x200")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()

        tk.Label(d, text="Add Department", bg=C["bg"], fg=C["primary"],
                 font=("Segoe UI", 14, "bold")).pack(pady=(15, 10))

        form = tk.Frame(d, bg=C["bg"])
        form.pack(fill="x", padx=25)

        tk.Label(form, text="Name", bg=C["bg"], fg=C["muted"]).pack(anchor="w", pady=(8, 2))
        name_entry = tk.Entry(form, bg=C["input"], fg=C["text"], font=("Segoe UI", 10), relief="flat")
        name_entry.pack(fill="x", ipady=4)

        def save():
            name = name_entry.get().strip()
            if not name:
                return
            try:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("INSERT INTO departments (name) VALUES (?)", (name,))
                conn.commit()
                conn.close()
                d.destroy()
                self._show_departments()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Department already exists!")

        tk.Button(d, text="Save", bg=C["success"], fg="white", font=("Segoe UI", 11, "bold"),
                  relief="flat", padx=18, pady=6, command=save, cursor="hand2").pack(pady=12)

    # ============ REPORTS ============

    def _show_reports(self):
        self._clear()
        self._active("report")
        h = self._header("Reports", "Analytics & data export")

        tk.Button(h, text="Export All to Excel", bg=C["primary"], fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=4,
                  cursor="hand2", command=self._export_all).pack(side="right")

        if not MATPLOTLIB_AVAILABLE:
            tk.Label(self.main, text="Install matplotlib for charts:\npip install matplotlib",
                     bg=C["bg"], fg=C["warning"], font=("Segoe UI", 13)).pack(pady=40)
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        # Department distribution
        c.execute("SELECT department, COUNT(*) FROM employees WHERE status='Active' GROUP BY department")
        dept_data = c.fetchall()

        # Monthly attendance
        c.execute("""SELECT date, COUNT(*) FROM attendance WHERE status='Present'
                    GROUP BY date ORDER BY date DESC LIMIT 14""")
        att_data = list(reversed(c.fetchall()))

        # Salary distribution
        c.execute("SELECT name, basic_salary + allowances FROM employees WHERE status='Active' ORDER BY basic_salary DESC LIMIT 10")
        sal_data = c.fetchall()

        conn.close()

        fig = Figure(figsize=(10, 5), facecolor=C["bg"])

        # Dept pie
        if dept_data:
            ax1 = fig.add_subplot(131)
            labels = [d[0] or "Other" for d in dept_data]
            vals = [d[1] for d in dept_data]
            ax1.pie(vals, labels=labels, autopct="%1.0f%%", textprops={"color": C["text"], "fontsize": 8})
            ax1.set_title("Employees by Dept", color=C["text"], fontsize=10)

        # Attendance bar
        if att_data:
            ax2 = fig.add_subplot(132)
            ax2.set_facecolor(C["card"])
            dates = [d[0][5:] for d in att_data]
            counts = [d[1] for d in att_data]
            ax2.bar(dates, counts, color=C["success"])
            ax2.set_title("Daily Attendance", color=C["text"], fontsize=10)
            ax2.tick_params(colors=C["muted"], labelsize=7, rotation=45)
            for spine in ax2.spines.values():
                spine.set_color(C["border"])

        # Salary bar
        if sal_data:
            ax3 = fig.add_subplot(133)
            ax3.set_facecolor(C["card"])
            names = [s[0][:12] for s in sal_data]
            sals = [s[1] for s in sal_data]
            ax3.barh(names, sals, color=C["primary"])
            ax3.set_title("Top Salaries", color=C["text"], fontsize=10)
            ax3.tick_params(colors=C["muted"], labelsize=7)
            for spine in ax3.spines.values():
                spine.set_color(C["border"])

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, self.main)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=25, pady=(0, 20))

    def _export_all(self):
        try:
            import openpyxl
        except ImportError:
            messagebox.showerror("Error", "Install openpyxl:\npip install openpyxl")
            return

        fp = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if not fp:
            return

        wb = openpyxl.Workbook()
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        ws = wb.active
        ws.title = "Employees"
        ws.append(["Emp ID", "Name", "Email", "Phone", "Department", "Designation", "Join Date", "Salary", "Allowances", "Status"])
        c.execute("SELECT emp_id, name, email, phone, department, designation, join_date, basic_salary, allowances, status FROM employees")
        for r in c.fetchall():
            ws.append(list(r))

        ws2 = wb.create_sheet("Attendance")
        ws2.append(["Emp ID", "Date", "Check In", "Check Out", "Hours", "Status"])
        c.execute("SELECT emp_id, date, check_in, check_out, hours, status FROM attendance ORDER BY date DESC")
        for r in c.fetchall():
            ws2.append(list(r))

        ws3 = wb.create_sheet("Leaves")
        ws3.append(["Emp Name", "Type", "From", "To", "Days", "Reason", "Status"])
        c.execute("SELECT emp_name, leave_type, start_date, end_date, days, reason, status FROM leaves")
        for r in c.fetchall():
            ws3.append(list(r))

        ws4 = wb.create_sheet("Payroll")
        ws4.append(["Emp ID", "Name", "Month", "Basic", "Allowances", "Deductions", "Net Salary", "Status"])
        c.execute("SELECT emp_id, emp_name, month, basic, allowances, deductions, net_salary, status FROM payroll")
        for r in c.fetchall():
            ws4.append(list(r))

        conn.close()
        wb.save(fp)
        messagebox.showinfo("Exported!", f"All data saved to:\n{fp}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = EmployeeApp()
    app.run()
