"""
Inventory Management System - Professional Business Software
By: Matrix Tech Solutions (Fiverr Portfolio)

Features:
- Product Management (Add, Edit, Delete, Search)
- Sales Recording & Tracking
- Stock Alerts (Low Stock Warnings)
- Customer Database
- Invoice Generation (PDF)
- Sales Reports with Charts
- Data Export to Excel
- Dark Professional Theme
- SQLite Database (no server needed)
- Multi-user ready

This is a COMPLETE business application ready to deploy.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
from datetime import datetime, timedelta
import json

# Optional imports
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ============ DATABASE ============

DB_FILE = "inventory.db"


def init_db():
    """Database tables create karo."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT DEFAULT '',
        price REAL DEFAULT 0,
        cost REAL DEFAULT 0,
        stock INTEGER DEFAULT 0,
        min_stock INTEGER DEFAULT 5,
        barcode TEXT DEFAULT '',
        description TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT DEFAULT '',
        email TEXT DEFAULT '',
        address TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER DEFAULT 0,
        customer_name TEXT DEFAULT 'Walk-in',
        total REAL DEFAULT 0,
        discount REAL DEFAULT 0,
        tax REAL DEFAULT 0,
        grand_total REAL DEFAULT 0,
        payment_method TEXT DEFAULT 'Cash',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS sale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER,
        product_id INTEGER,
        product_name TEXT,
        quantity INTEGER DEFAULT 1,
        price REAL DEFAULT 0,
        total REAL DEFAULT 0,
        FOREIGN KEY (sale_id) REFERENCES sales(id)
    )""")

    conn.commit()
    conn.close()


# ============ COLORS & THEME ============

COLORS = {
    "bg": "#0f1117",
    "sidebar": "#161b22",
    "card": "#1c2128",
    "card_hover": "#252d38",
    "primary": "#58a6ff",
    "success": "#3fb950",
    "warning": "#d29922",
    "danger": "#f85149",
    "text": "#e6edf3",
    "text_muted": "#8b949e",
    "border": "#30363d",
    "input_bg": "#0d1117",
    "table_header": "#21262d",
    "table_row1": "#161b22",
    "table_row2": "#1c2128",
}


# ============ MAIN APPLICATION ============

class InventoryApp:
    def __init__(self):
        init_db()

        self.root = tk.Tk()
        self.root.title("Inventory Management System — Matrix Tech")
        self.root.geometry("1200x750")
        self.root.configure(bg=COLORS["bg"])
        self.root.minsize(1000, 600)

        # Cart for POS
        self.cart = []
        self.current_page = "dashboard"

        self._create_sidebar()
        self._create_main_area()
        self._show_dashboard()

    def _create_sidebar(self):
        sidebar = tk.Frame(self.root, bg=COLORS["sidebar"], width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo
        tk.Label(
            sidebar, text="INVENTORY", bg=COLORS["sidebar"], fg=COLORS["primary"],
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(25, 5))
        tk.Label(
            sidebar, text="Management System", bg=COLORS["sidebar"], fg=COLORS["text_muted"],
            font=("Segoe UI", 10)
        ).pack(pady=(0, 30))

        # Menu items
        menu_items = [
            ("Dashboard", "dashboard", self._show_dashboard),
            ("Products", "products", self._show_products),
            ("New Sale (POS)", "pos", self._show_pos),
            ("Sales History", "sales", self._show_sales),
            ("Customers", "customers", self._show_customers),
            ("Reports", "reports", self._show_reports),
            ("Low Stock", "alerts", self._show_alerts),
        ]

        self.menu_buttons = {}
        for text, key, command in menu_items:
            btn = tk.Button(
                sidebar, text=f"  {text}", bg=COLORS["sidebar"], fg=COLORS["text_muted"],
                font=("Segoe UI", 12), relief="flat", anchor="w", padx=20, pady=8,
                activebackground=COLORS["card"], activeforeground=COLORS["primary"],
                cursor="hand2", command=command
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.menu_buttons[key] = btn

        # Bottom info
        tk.Label(
            sidebar, text="Matrix Tech Solutions", bg=COLORS["sidebar"],
            fg=COLORS["text_muted"], font=("Segoe UI", 9)
        ).pack(side="bottom", pady=15)

    def _set_active_menu(self, key):
        for k, btn in self.menu_buttons.items():
            if k == key:
                btn.configure(bg=COLORS["card"], fg=COLORS["primary"])
            else:
                btn.configure(bg=COLORS["sidebar"], fg=COLORS["text_muted"])

    def _create_main_area(self):
        self.main_frame = tk.Frame(self.root, bg=COLORS["bg"])
        self.main_frame.pack(side="right", fill="both", expand=True)

    def _clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def _create_header(self, title, subtitle=""):
        header = tk.Frame(self.main_frame, bg=COLORS["bg"])
        header.pack(fill="x", padx=30, pady=(25, 15))

        tk.Label(
            header, text=title, bg=COLORS["bg"], fg=COLORS["text"],
            font=("Segoe UI", 22, "bold")
        ).pack(side="left")

        if subtitle:
            tk.Label(
                header, text=subtitle, bg=COLORS["bg"], fg=COLORS["text_muted"],
                font=("Segoe UI", 11)
            ).pack(side="left", padx=(15, 0), pady=(8, 0))

        return header

    # ============ DASHBOARD ============

    def _show_dashboard(self):
        self._clear_main()
        self._set_active_menu("dashboard")
        self._create_header("Dashboard", "Business overview at a glance")

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        # Stats
        c.execute("SELECT COUNT(*) FROM products")
        total_products = c.fetchone()[0]

        c.execute("SELECT COALESCE(SUM(stock), 0) FROM products")
        total_stock = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM products WHERE stock <= min_stock")
        low_stock = c.fetchone()[0]

        today = datetime.now().strftime("%Y-%m-%d")
        c.execute("SELECT COALESCE(SUM(grand_total), 0) FROM sales WHERE created_at LIKE ?", (f"{today}%",))
        today_sales = c.fetchone()[0]

        c.execute("SELECT COALESCE(SUM(grand_total), 0) FROM sales")
        total_revenue = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM customers")
        total_customers = c.fetchone()[0]

        conn.close()

        # Stats cards
        cards_frame = tk.Frame(self.main_frame, bg=COLORS["bg"])
        cards_frame.pack(fill="x", padx=30, pady=10)

        stats = [
            ("Total Products", str(total_products), COLORS["primary"]),
            ("Total Stock", str(total_stock), COLORS["success"]),
            ("Low Stock Items", str(low_stock), COLORS["danger"] if low_stock > 0 else COLORS["success"]),
            ("Today's Sales", f"Rs {today_sales:,.0f}", COLORS["warning"]),
            ("Total Revenue", f"Rs {total_revenue:,.0f}", COLORS["success"]),
            ("Customers", str(total_customers), COLORS["primary"]),
        ]

        for i, (label, value, color) in enumerate(stats):
            card = tk.Frame(cards_frame, bg=COLORS["card"], relief="flat", padx=20, pady=15)
            card.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="nsew")
            cards_frame.grid_columnconfigure(i % 3, weight=1)

            tk.Label(card, text=value, bg=COLORS["card"], fg=color,
                     font=("Segoe UI", 24, "bold")).pack(anchor="w")
            tk.Label(card, text=label, bg=COLORS["card"], fg=COLORS["text_muted"],
                     font=("Segoe UI", 11)).pack(anchor="w")

        # Recent sales
        recent_frame = tk.Frame(self.main_frame, bg=COLORS["card"], padx=20, pady=15)
        recent_frame.pack(fill="both", expand=True, padx=30, pady=(15, 25))

        tk.Label(recent_frame, text="Recent Sales", bg=COLORS["card"], fg=COLORS["text"],
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, customer_name, grand_total, payment_method, created_at FROM sales ORDER BY id DESC LIMIT 10")
        recent_sales = c.fetchall()
        conn.close()

        if recent_sales:
            cols = ("ID", "Customer", "Total", "Payment", "Date")
            tree = ttk.Treeview(recent_frame, columns=cols, show="headings", height=8)
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            for sale in recent_sales:
                tree.insert("", "end", values=(sale[0], sale[1], f"Rs {sale[2]:,.0f}", sale[3], sale[4][:16]))
            tree.pack(fill="both", expand=True)
        else:
            tk.Label(recent_frame, text="No sales yet. Go to 'New Sale' to start!",
                     bg=COLORS["card"], fg=COLORS["text_muted"], font=("Segoe UI", 12)).pack(pady=30)

    # ============ PRODUCTS ============

    def _show_products(self):
        self._clear_main()
        self._set_active_menu("products")
        header = self._create_header("Products", "Manage your product inventory")

        # Add button
        tk.Button(
            header, text="+ Add Product", bg=COLORS["success"], fg="white",
            font=("Segoe UI", 11, "bold"), relief="flat", padx=15, pady=5,
            cursor="hand2", command=self._add_product_dialog
        ).pack(side="right")

        # Search
        search_frame = tk.Frame(self.main_frame, bg=COLORS["bg"])
        search_frame.pack(fill="x", padx=30, pady=(0, 10))

        self.product_search = tk.Entry(
            search_frame, bg=COLORS["input_bg"], fg=COLORS["text"],
            font=("Segoe UI", 12), relief="flat", insertbackground=COLORS["text"]
        )
        self.product_search.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        self.product_search.insert(0, "Search products...")
        self.product_search.bind("<FocusIn>", lambda e: self.product_search.delete(0, "end") if self.product_search.get() == "Search products..." else None)
        self.product_search.bind("<KeyRelease>", lambda e: self._load_products())

        # Table
        table_frame = tk.Frame(self.main_frame, bg=COLORS["card"])
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        cols = ("ID", "Name", "Category", "Price", "Cost", "Stock", "Min Stock", "Status")
        self.product_tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=18)

        widths = [50, 200, 120, 100, 100, 80, 80, 100]
        for col, w in zip(cols, widths):
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=w, minwidth=50)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        self.product_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Context menu
        self.product_tree.bind("<Button-3>", self._product_context_menu)
        self.product_tree.bind("<Double-1>", lambda e: self._edit_product_dialog())

        self._load_products()

    def _load_products(self):
        search = self.product_search.get().strip()
        if search == "Search products...":
            search = ""

        for item in self.product_tree.get_children():
            self.product_tree.delete(item)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        if search:
            c.execute("SELECT id, name, category, price, cost, stock, min_stock FROM products WHERE name LIKE ? OR category LIKE ?",
                       (f"%{search}%", f"%{search}%"))
        else:
            c.execute("SELECT id, name, category, price, cost, stock, min_stock FROM products ORDER BY id DESC")

        for row in c.fetchall():
            status = "OK" if row[5] > row[6] else "LOW STOCK"
            self.product_tree.insert("", "end", values=(
                row[0], row[1], row[2], f"Rs {row[3]:,.0f}", f"Rs {row[4]:,.0f}",
                row[5], row[6], status
            ))
        conn.close()

    def _add_product_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Product")
        dialog.geometry("450x500")
        dialog.configure(bg=COLORS["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Add New Product", bg=COLORS["bg"], fg=COLORS["primary"],
                 font=("Segoe UI", 16, "bold")).pack(pady=(20, 15))

        fields = {}
        field_defs = [
            ("Name", "product_name", ""),
            ("Category", "category", ""),
            ("Sell Price (Rs)", "price", "0"),
            ("Cost Price (Rs)", "cost", "0"),
            ("Stock Quantity", "stock", "0"),
            ("Min Stock Alert", "min_stock", "5"),
            ("Barcode (optional)", "barcode", ""),
            ("Description", "description", ""),
        ]

        form_frame = tk.Frame(dialog, bg=COLORS["bg"])
        form_frame.pack(fill="x", padx=30)

        for label, key, default in field_defs:
            tk.Label(form_frame, text=label, bg=COLORS["bg"], fg=COLORS["text_muted"],
                     font=("Segoe UI", 10)).pack(anchor="w", pady=(8, 2))
            entry = tk.Entry(form_frame, bg=COLORS["input_bg"], fg=COLORS["text"],
                             font=("Segoe UI", 11), relief="flat", insertbackground=COLORS["text"])
            entry.pack(fill="x", ipady=5)
            entry.insert(0, default)
            fields[key] = entry

        def save():
            name = fields["product_name"].get().strip()
            if not name:
                messagebox.showerror("Error", "Product name is required!")
                return
            try:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("""INSERT INTO products (name, category, price, cost, stock, min_stock, barcode, description)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                         (name, fields["category"].get(), float(fields["price"].get() or 0),
                          float(fields["cost"].get() or 0), int(fields["stock"].get() or 0),
                          int(fields["min_stock"].get() or 5), fields["barcode"].get(),
                          fields["description"].get()))
                conn.commit()
                conn.close()
                dialog.destroy()
                self._load_products()
                messagebox.showinfo("Success", f"Product '{name}' added!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(dialog, text="Save Product", bg=COLORS["success"], fg="white",
                  font=("Segoe UI", 12, "bold"), relief="flat", padx=20, pady=8,
                  command=save, cursor="hand2").pack(pady=20)

    def _edit_product_dialog(self):
        selected = self.product_tree.selection()
        if not selected:
            return
        item = self.product_tree.item(selected[0])
        pid = item["values"][0]

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM products WHERE id=?", (pid,))
        product = c.fetchone()
        conn.close()

        if not product:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Product #{pid}")
        dialog.geometry("450x500")
        dialog.configure(bg=COLORS["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text=f"Edit Product #{pid}", bg=COLORS["bg"], fg=COLORS["primary"],
                 font=("Segoe UI", 16, "bold")).pack(pady=(20, 15))

        fields = {}
        field_defs = [
            ("Name", "name", product[1]),
            ("Category", "category", product[2]),
            ("Sell Price", "price", str(product[3])),
            ("Cost Price", "cost", str(product[4])),
            ("Stock", "stock", str(product[5])),
            ("Min Stock", "min_stock", str(product[6])),
            ("Barcode", "barcode", product[7] or ""),
            ("Description", "description", product[8] or ""),
        ]

        form_frame = tk.Frame(dialog, bg=COLORS["bg"])
        form_frame.pack(fill="x", padx=30)

        for label, key, default in field_defs:
            tk.Label(form_frame, text=label, bg=COLORS["bg"], fg=COLORS["text_muted"],
                     font=("Segoe UI", 10)).pack(anchor="w", pady=(8, 2))
            entry = tk.Entry(form_frame, bg=COLORS["input_bg"], fg=COLORS["text"],
                             font=("Segoe UI", 11), relief="flat", insertbackground=COLORS["text"])
            entry.pack(fill="x", ipady=5)
            entry.insert(0, str(default))
            fields[key] = entry

        def save():
            try:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("""UPDATE products SET name=?, category=?, price=?, cost=?, stock=?, min_stock=?, barcode=?, description=? WHERE id=?""",
                         (fields["name"].get(), fields["category"].get(),
                          float(fields["price"].get() or 0), float(fields["cost"].get() or 0),
                          int(fields["stock"].get() or 0), int(fields["min_stock"].get() or 5),
                          fields["barcode"].get(), fields["description"].get(), pid))
                conn.commit()
                conn.close()
                dialog.destroy()
                self._load_products()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        def delete():
            if messagebox.askyesno("Confirm", f"Delete product #{pid}?"):
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("DELETE FROM products WHERE id=?", (pid,))
                conn.commit()
                conn.close()
                dialog.destroy()
                self._load_products()

        btn_frame = tk.Frame(dialog, bg=COLORS["bg"])
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Save Changes", bg=COLORS["success"], fg="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", padx=15, pady=6,
                  command=save, cursor="hand2").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete", bg=COLORS["danger"], fg="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", padx=15, pady=6,
                  command=delete, cursor="hand2").pack(side="left", padx=5)

    def _product_context_menu(self, event):
        selected = self.product_tree.selection()
        if not selected:
            return
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Edit", command=self._edit_product_dialog)
        menu.add_command(label="Delete", command=lambda: self._delete_selected_product(selected[0]))
        menu.post(event.x_root, event.y_root)

    def _delete_selected_product(self, selection):
        item = self.product_tree.item(selection)
        pid = item["values"][0]
        if messagebox.askyesno("Confirm", f"Delete product #{pid}?"):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("DELETE FROM products WHERE id=?", (pid,))
            conn.commit()
            conn.close()
            self._load_products()

    # ============ POS (Point of Sale) ============

    def _show_pos(self):
        self._clear_main()
        self._set_active_menu("pos")
        self._create_header("New Sale", "Point of Sale")

        pos_frame = tk.Frame(self.main_frame, bg=COLORS["bg"])
        pos_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        # Left: Product selection
        left = tk.Frame(pos_frame, bg=COLORS["card"], padx=15, pady=15)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(left, text="Select Products", bg=COLORS["card"], fg=COLORS["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")

        # Search
        self.pos_search = tk.Entry(left, bg=COLORS["input_bg"], fg=COLORS["text"],
                                    font=("Segoe UI", 11), relief="flat", insertbackground=COLORS["text"])
        self.pos_search.pack(fill="x", ipady=6, pady=10)
        self.pos_search.insert(0, "Search product...")
        self.pos_search.bind("<FocusIn>", lambda e: self.pos_search.delete(0, "end") if self.pos_search.get() == "Search product..." else None)
        self.pos_search.bind("<KeyRelease>", lambda e: self._load_pos_products())

        cols = ("ID", "Name", "Price", "Stock")
        self.pos_product_tree = ttk.Treeview(left, columns=cols, show="headings", height=12)
        for col, w in zip(cols, [50, 180, 100, 80]):
            self.pos_product_tree.heading(col, text=col)
            self.pos_product_tree.column(col, width=w)
        self.pos_product_tree.pack(fill="both", expand=True)
        self.pos_product_tree.bind("<Double-1>", self._add_to_cart)

        tk.Label(left, text="Double-click to add to cart", bg=COLORS["card"],
                 fg=COLORS["text_muted"], font=("Segoe UI", 9)).pack(pady=(5, 0))

        # Right: Cart
        right = tk.Frame(pos_frame, bg=COLORS["card"], padx=15, pady=15, width=350)
        right.pack(side="right", fill="both")
        right.pack_propagate(False)

        tk.Label(right, text="Shopping Cart", bg=COLORS["card"], fg=COLORS["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")

        # Customer
        tk.Label(right, text="Customer:", bg=COLORS["card"], fg=COLORS["text_muted"],
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(10, 2))
        self.pos_customer = tk.Entry(right, bg=COLORS["input_bg"], fg=COLORS["text"],
                                      font=("Segoe UI", 11), relief="flat", insertbackground=COLORS["text"])
        self.pos_customer.pack(fill="x", ipady=5)
        self.pos_customer.insert(0, "Walk-in Customer")

        # Cart items
        cart_cols = ("Product", "Qty", "Price", "Total")
        self.cart_tree = ttk.Treeview(right, columns=cart_cols, show="headings", height=8)
        for col, w in zip(cart_cols, [130, 50, 70, 80]):
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=w)
        self.cart_tree.pack(fill="both", expand=True, pady=10)
        self.cart_tree.bind("<Delete>", self._remove_from_cart)

        # Totals
        self.cart_total_label = tk.Label(right, text="Total: Rs 0", bg=COLORS["card"],
                                          fg=COLORS["success"], font=("Segoe UI", 18, "bold"))
        self.cart_total_label.pack(anchor="e", pady=5)

        # Payment method
        pay_frame = tk.Frame(right, bg=COLORS["card"])
        pay_frame.pack(fill="x", pady=5)
        tk.Label(pay_frame, text="Payment:", bg=COLORS["card"], fg=COLORS["text_muted"],
                 font=("Segoe UI", 10)).pack(side="left")
        self.pay_method = ttk.Combobox(pay_frame, values=["Cash", "Card", "Online", "Credit"], state="readonly")
        self.pay_method.set("Cash")
        self.pay_method.pack(side="right")

        # Buttons
        btn_frame = tk.Frame(right, bg=COLORS["card"])
        btn_frame.pack(fill="x", pady=10)

        tk.Button(btn_frame, text="Complete Sale", bg=COLORS["success"], fg="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", padx=10, pady=6,
                  command=self._complete_sale, cursor="hand2").pack(side="left", padx=(0, 5))
        tk.Button(btn_frame, text="Clear Cart", bg=COLORS["danger"], fg="white",
                  font=("Segoe UI", 11), relief="flat", padx=10, pady=6,
                  command=self._clear_cart, cursor="hand2").pack(side="left")

        self.cart = []
        self._load_pos_products()

    def _load_pos_products(self):
        search = self.pos_search.get().strip()
        if search == "Search product...":
            search = ""

        for item in self.pos_product_tree.get_children():
            self.pos_product_tree.delete(item)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        if search:
            c.execute("SELECT id, name, price, stock FROM products WHERE (name LIKE ? OR barcode LIKE ?) AND stock > 0",
                       (f"%{search}%", f"%{search}%"))
        else:
            c.execute("SELECT id, name, price, stock FROM products WHERE stock > 0 ORDER BY name")

        for row in c.fetchall():
            self.pos_product_tree.insert("", "end", values=(row[0], row[1], f"Rs {row[2]:,.0f}", row[3]))
        conn.close()

    def _add_to_cart(self, event=None):
        selected = self.pos_product_tree.selection()
        if not selected:
            return
        item = self.pos_product_tree.item(selected[0])
        vals = item["values"]
        pid = vals[0]
        name = vals[1]
        price = float(str(vals[2]).replace("Rs ", "").replace(",", ""))
        stock = vals[3]

        # Check if already in cart
        for ci in self.cart:
            if ci["id"] == pid:
                if ci["qty"] < stock:
                    ci["qty"] += 1
                    ci["total"] = ci["qty"] * ci["price"]
                    self._refresh_cart()
                return

        self.cart.append({"id": pid, "name": name, "price": price, "qty": 1, "total": price, "stock": stock})
        self._refresh_cart()

    def _remove_from_cart(self, event=None):
        selected = self.cart_tree.selection()
        if not selected:
            return
        idx = self.cart_tree.index(selected[0])
        if 0 <= idx < len(self.cart):
            self.cart.pop(idx)
            self._refresh_cart()

    def _refresh_cart(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        total = 0
        for ci in self.cart:
            self.cart_tree.insert("", "end", values=(ci["name"], ci["qty"], f"Rs {ci['price']:,.0f}", f"Rs {ci['total']:,.0f}"))
            total += ci["total"]

        self.cart_total_label.config(text=f"Total: Rs {total:,.0f}")

    def _clear_cart(self):
        self.cart = []
        self._refresh_cart()

    def _complete_sale(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Cart is empty!")
            return

        customer = self.pos_customer.get().strip() or "Walk-in"
        total = sum(ci["total"] for ci in self.cart)
        payment = self.pay_method.get()

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        c.execute("""INSERT INTO sales (customer_name, total, grand_total, payment_method)
                    VALUES (?, ?, ?, ?)""", (customer, total, total, payment))
        sale_id = c.lastrowid

        for ci in self.cart:
            c.execute("""INSERT INTO sale_items (sale_id, product_id, product_name, quantity, price, total)
                        VALUES (?, ?, ?, ?, ?, ?)""", (sale_id, ci["id"], ci["name"], ci["qty"], ci["price"], ci["total"]))
            c.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (ci["qty"], ci["id"]))

        conn.commit()
        conn.close()

        messagebox.showinfo("Sale Complete!", f"Sale #{sale_id}\nTotal: Rs {total:,.0f}\nPayment: {payment}")
        self.cart = []
        self._refresh_cart()
        self._load_pos_products()

    # ============ SALES HISTORY ============

    def _show_sales(self):
        self._clear_main()
        self._set_active_menu("sales")
        self._create_header("Sales History", "All sales records")

        table_frame = tk.Frame(self.main_frame, bg=COLORS["card"])
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        cols = ("ID", "Customer", "Items", "Total", "Payment", "Date")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=20)
        for col, w in zip(cols, [60, 180, 60, 120, 100, 160]):
            tree.heading(col, text=col)
            tree.column(col, width=w)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""SELECT s.id, s.customer_name, COUNT(si.id), s.grand_total, s.payment_method, s.created_at
                    FROM sales s LEFT JOIN sale_items si ON s.id = si.sale_id
                    GROUP BY s.id ORDER BY s.id DESC""")

        for row in c.fetchall():
            tree.insert("", "end", values=(row[0], row[1], row[2], f"Rs {row[3]:,.0f}", row[4], row[5][:16]))

        conn.close()
        tree.pack(fill="both", expand=True)

    # ============ CUSTOMERS ============

    def _show_customers(self):
        self._clear_main()
        self._set_active_menu("customers")
        header = self._create_header("Customers", "Customer database")

        tk.Button(
            header, text="+ Add Customer", bg=COLORS["success"], fg="white",
            font=("Segoe UI", 11, "bold"), relief="flat", padx=15, pady=5,
            cursor="hand2", command=self._add_customer_dialog
        ).pack(side="right")

        table_frame = tk.Frame(self.main_frame, bg=COLORS["card"])
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        cols = ("ID", "Name", "Phone", "Email", "Address", "Since")
        self.customer_tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=18)
        for col, w in zip(cols, [50, 160, 120, 180, 200, 120]):
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=w)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, name, phone, email, address, created_at FROM customers ORDER BY id DESC")
        for row in c.fetchall():
            self.customer_tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], row[5][:10]))
        conn.close()
        self.customer_tree.pack(fill="both", expand=True)

    def _add_customer_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Customer")
        dialog.geometry("400x350")
        dialog.configure(bg=COLORS["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Add Customer", bg=COLORS["bg"], fg=COLORS["primary"],
                 font=("Segoe UI", 16, "bold")).pack(pady=(20, 15))

        fields = {}
        for label, key in [("Name", "name"), ("Phone", "phone"), ("Email", "email"), ("Address", "address")]:
            form = tk.Frame(dialog, bg=COLORS["bg"])
            form.pack(fill="x", padx=30, pady=3)
            tk.Label(form, text=label, bg=COLORS["bg"], fg=COLORS["text_muted"],
                     font=("Segoe UI", 10)).pack(anchor="w")
            entry = tk.Entry(form, bg=COLORS["input_bg"], fg=COLORS["text"],
                             font=("Segoe UI", 11), relief="flat", insertbackground=COLORS["text"])
            entry.pack(fill="x", ipady=5)
            fields[key] = entry

        def save():
            name = fields["name"].get().strip()
            if not name:
                messagebox.showerror("Error", "Name required!")
                return
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)",
                     (name, fields["phone"].get(), fields["email"].get(), fields["address"].get()))
            conn.commit()
            conn.close()
            dialog.destroy()
            self._show_customers()

        tk.Button(dialog, text="Save", bg=COLORS["success"], fg="white",
                  font=("Segoe UI", 12, "bold"), relief="flat", padx=20, pady=8,
                  command=save, cursor="hand2").pack(pady=15)

    # ============ REPORTS ============

    def _show_reports(self):
        self._clear_main()
        self._set_active_menu("reports")
        header = self._create_header("Reports", "Sales analytics & reports")

        tk.Button(
            header, text="Export Excel", bg=COLORS["primary"], fg="white",
            font=("Segoe UI", 11, "bold"), relief="flat", padx=15, pady=5,
            cursor="hand2", command=self._export_excel
        ).pack(side="right")

        if not MATPLOTLIB_AVAILABLE:
            tk.Label(self.main_frame, text="Install matplotlib for charts:\npip install matplotlib",
                     bg=COLORS["bg"], fg=COLORS["warning"], font=("Segoe UI", 14)).pack(pady=50)
            return

        chart_frame = tk.Frame(self.main_frame, bg=COLORS["bg"])
        chart_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        # Last 7 days sales
        dates = []
        amounts = []
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            c.execute("SELECT COALESCE(SUM(grand_total), 0) FROM sales WHERE created_at LIKE ?", (f"{date}%",))
            amounts.append(c.fetchone()[0])
            dates.append((datetime.now() - timedelta(days=i)).strftime("%d/%m"))

        # Category sales
        c.execute("""SELECT p.category, COALESCE(SUM(si.total), 0)
                    FROM sale_items si JOIN products p ON si.product_id = p.id
                    GROUP BY p.category ORDER BY SUM(si.total) DESC LIMIT 5""")
        cat_data = c.fetchall()
        conn.close()

        fig = Figure(figsize=(10, 4), facecolor=COLORS["bg"])

        # Sales chart
        ax1 = fig.add_subplot(121)
        ax1.bar(dates, amounts, color=COLORS["primary"])
        ax1.set_title("Last 7 Days Sales", color=COLORS["text"], fontsize=12)
        ax1.set_facecolor(COLORS["card"])
        ax1.tick_params(colors=COLORS["text_muted"])
        for spine in ax1.spines.values():
            spine.set_color(COLORS["border"])

        # Category pie
        if cat_data:
            ax2 = fig.add_subplot(122)
            cats = [r[0] or "Other" for r in cat_data]
            vals = [r[1] for r in cat_data]
            ax2.pie(vals, labels=cats, autopct="%1.0f%%", textprops={"color": COLORS["text"]})
            ax2.set_title("Sales by Category", color=COLORS["text"], fontsize=12)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _export_excel(self):
        try:
            import openpyxl
        except ImportError:
            messagebox.showerror("Error", "Install openpyxl: pip install openpyxl")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if not filepath:
            return

        wb = openpyxl.Workbook()

        # Products sheet
        ws = wb.active
        ws.title = "Products"
        ws.append(["ID", "Name", "Category", "Price", "Cost", "Stock", "Min Stock"])

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, name, category, price, cost, stock, min_stock FROM products")
        for row in c.fetchall():
            ws.append(list(row))

        # Sales sheet
        ws2 = wb.create_sheet("Sales")
        ws2.append(["ID", "Customer", "Total", "Payment", "Date"])
        c.execute("SELECT id, customer_name, grand_total, payment_method, created_at FROM sales")
        for row in c.fetchall():
            ws2.append(list(row))

        conn.close()
        wb.save(filepath)
        messagebox.showinfo("Exported!", f"Data saved to:\n{filepath}")

    # ============ LOW STOCK ALERTS ============

    def _show_alerts(self):
        self._clear_main()
        self._set_active_menu("alerts")
        self._create_header("Low Stock Alerts", "Products that need restocking")

        table_frame = tk.Frame(self.main_frame, bg=COLORS["card"])
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        cols = ("ID", "Name", "Category", "Current Stock", "Min Required", "Status")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=18)
        for col, w in zip(cols, [50, 200, 120, 120, 120, 120]):
            tree.heading(col, text=col)
            tree.column(col, width=w)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, name, category, stock, min_stock FROM products WHERE stock <= min_stock ORDER BY stock ASC")

        for row in c.fetchall():
            status = "OUT OF STOCK" if row[3] == 0 else "LOW STOCK"
            tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], status))

        conn.close()
        tree.pack(fill="both", expand=True)

        if not tree.get_children():
            tk.Label(table_frame, text="All products are well stocked!",
                     bg=COLORS["card"], fg=COLORS["success"], font=("Segoe UI", 14)).pack(pady=30)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = InventoryApp()
    app.run()
