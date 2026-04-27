"""
Hospital Management System - Database Module
Complete database schema for HMS with all tables.
"""

import sqlite3
from datetime import datetime

DB_FILE = "hospital.db"


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Departments
    c.execute("""CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        floor TEXT DEFAULT '',
        head_doctor TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        status TEXT DEFAULT 'Active'
    )""")

    # Doctors
    c.execute("""CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id TEXT UNIQUE,
        name TEXT NOT NULL,
        specialization TEXT DEFAULT '',
        department TEXT DEFAULT '',
        qualification TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        email TEXT DEFAULT '',
        fee REAL DEFAULT 0,
        schedule TEXT DEFAULT 'Mon-Sat 9AM-5PM',
        status TEXT DEFAULT 'Active',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # Patients
    c.execute("""CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT UNIQUE,
        name TEXT NOT NULL,
        father_name TEXT DEFAULT '',
        cnic TEXT DEFAULT '',
        age INTEGER DEFAULT 0,
        gender TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        email TEXT DEFAULT '',
        address TEXT DEFAULT '',
        blood_group TEXT DEFAULT '',
        emergency_contact TEXT DEFAULT '',
        patient_type TEXT DEFAULT 'OPD',
        status TEXT DEFAULT 'Active',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # Appointments
    c.execute("""CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_no INTEGER DEFAULT 0,
        patient_id TEXT,
        patient_name TEXT,
        doctor_id TEXT,
        doctor_name TEXT,
        department TEXT DEFAULT '',
        date TEXT,
        time TEXT DEFAULT '',
        fee REAL DEFAULT 0,
        status TEXT DEFAULT 'Waiting',
        notes TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # Medicines (Pharmacy)
    c.execute("""CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        generic_name TEXT DEFAULT '',
        category TEXT DEFAULT '',
        manufacturer TEXT DEFAULT '',
        batch_no TEXT DEFAULT '',
        price REAL DEFAULT 0,
        cost_price REAL DEFAULT 0,
        stock INTEGER DEFAULT 0,
        min_stock INTEGER DEFAULT 10,
        expiry_date TEXT DEFAULT '',
        shelf_location TEXT DEFAULT '',
        requires_prescription INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Active',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # Pharmacy Sales
    c.execute("""CREATE TABLE IF NOT EXISTS pharmacy_sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT UNIQUE,
        patient_id TEXT DEFAULT '',
        patient_name TEXT DEFAULT 'Walk-in',
        items_count INTEGER DEFAULT 0,
        subtotal REAL DEFAULT 0,
        discount REAL DEFAULT 0,
        total REAL DEFAULT 0,
        payment_method TEXT DEFAULT 'Cash',
        sold_by TEXT DEFAULT 'Admin',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS pharmacy_sale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER,
        medicine_id INTEGER,
        medicine_name TEXT,
        quantity INTEGER DEFAULT 1,
        price REAL DEFAULT 0,
        total REAL DEFAULT 0
    )""")

    # Prescriptions
    c.execute("""CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        patient_name TEXT,
        doctor_id TEXT,
        doctor_name TEXT,
        diagnosis TEXT DEFAULT '',
        medicines TEXT DEFAULT '',
        instructions TEXT DEFAULT '',
        follow_up TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # Lab Tests
    c.execute("""CREATE TABLE IF NOT EXISTS lab_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id TEXT UNIQUE,
        patient_id TEXT,
        patient_name TEXT,
        doctor_id TEXT DEFAULT '',
        doctor_name TEXT DEFAULT '',
        test_name TEXT NOT NULL,
        test_category TEXT DEFAULT '',
        fee REAL DEFAULT 0,
        result TEXT DEFAULT '',
        normal_range TEXT DEFAULT '',
        status TEXT DEFAULT 'Pending',
        report_date TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # Beds/Wards (IPD)
    c.execute("""CREATE TABLE IF NOT EXISTS wards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        ward_type TEXT DEFAULT 'General',
        total_beds INTEGER DEFAULT 0,
        floor TEXT DEFAULT '',
        charge_per_day REAL DEFAULT 0,
        status TEXT DEFAULT 'Active'
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS beds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bed_no TEXT UNIQUE,
        ward_id INTEGER,
        ward_name TEXT DEFAULT '',
        status TEXT DEFAULT 'Available',
        patient_id TEXT DEFAULT '',
        patient_name TEXT DEFAULT '',
        admission_date TEXT DEFAULT '',
        doctor_id TEXT DEFAULT ''
    )""")

    # Billing
    c.execute("""CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_no TEXT UNIQUE,
        patient_id TEXT,
        patient_name TEXT,
        bill_type TEXT DEFAULT 'OPD',
        consultation_fee REAL DEFAULT 0,
        lab_charges REAL DEFAULT 0,
        pharmacy_charges REAL DEFAULT 0,
        bed_charges REAL DEFAULT 0,
        other_charges REAL DEFAULT 0,
        subtotal REAL DEFAULT 0,
        discount REAL DEFAULT 0,
        tax REAL DEFAULT 0,
        grand_total REAL DEFAULT 0,
        paid REAL DEFAULT 0,
        balance REAL DEFAULT 0,
        payment_method TEXT DEFAULT 'Cash',
        payment_status TEXT DEFAULT 'Unpaid',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # Default departments
    defaults = [
        ("General Medicine", "Ground Floor"),
        ("Surgery", "1st Floor"),
        ("Cardiology", "1st Floor"),
        ("Orthopedics", "2nd Floor"),
        ("Gynecology", "2nd Floor"),
        ("Pediatrics", "Ground Floor"),
        ("ENT", "Ground Floor"),
        ("Dermatology", "3rd Floor"),
        ("Neurology", "3rd Floor"),
        ("Radiology", "Basement"),
        ("Pathology", "Basement"),
        ("Emergency", "Ground Floor"),
        ("Pharmacy", "Ground Floor"),
    ]
    for name, floor in defaults:
        try:
            c.execute("INSERT OR IGNORE INTO departments (name, floor) VALUES (?, ?)", (name, floor))
        except sqlite3.IntegrityError:
            pass

    # Default wards
    ward_defaults = [
        ("General Ward A", "General", 20, "1st Floor", 2000),
        ("General Ward B", "General", 20, "1st Floor", 2000),
        ("Private Room", "Private", 10, "2nd Floor", 8000),
        ("Semi-Private", "Semi-Private", 15, "2nd Floor", 4000),
        ("ICU", "ICU", 8, "3rd Floor", 15000),
        ("NICU", "NICU", 5, "3rd Floor", 12000),
        ("Emergency Ward", "Emergency", 10, "Ground Floor", 3000),
    ]
    for name, wtype, beds_count, floor, charge in ward_defaults:
        try:
            c.execute("INSERT OR IGNORE INTO wards (name, ward_type, total_beds, floor, charge_per_day) VALUES (?, ?, ?, ?, ?)",
                     (name, wtype, beds_count, floor, charge))
        except sqlite3.IntegrityError:
            pass

    # Create beds for wards
    c.execute("SELECT id, name, total_beds FROM wards")
    wards = c.fetchall()
    for ward_id, ward_name, total_beds in wards:
        for i in range(1, total_beds + 1):
            bed_no = f"{ward_name[:3].upper()}-{i:03d}"
            try:
                c.execute("INSERT OR IGNORE INTO beds (bed_no, ward_id, ward_name) VALUES (?, ?, ?)",
                         (bed_no, ward_id, ward_name))
            except sqlite3.IntegrityError:
                pass

    conn.commit()
    conn.close()


def generate_id(prefix, table, id_col):
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"SELECT MAX(id) FROM {table}")
    result = c.fetchone()[0]
    conn.close()
    num = (result or 0) + 1
    return f"{prefix}-{num:05d}"
