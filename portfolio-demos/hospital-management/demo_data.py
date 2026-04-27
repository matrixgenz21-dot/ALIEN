"""
Hospital Management System - Demo Data Generator
Creates realistic demo data for showcasing the system.
"""

import sqlite3
import random
from datetime import datetime, timedelta
from database import get_conn, init_db, generate_id, audit_log, add_notification

# Pakistani names for realistic data
MALE_NAMES = [
    "Ahmed Khan", "Muhammad Ali", "Hassan Raza", "Bilal Ahmed", "Usman Ghani",
    "Imran Malik", "Saad Iqbal", "Faisal Javed", "Zubair Hussain", "Kamran Shah",
    "Naveed Ahmad", "Waqar Younis", "Shahid Afridi", "Tariq Mehmood", "Adnan Sami",
    "Rizwan Ahmed", "Asad Shafiq", "Babar Azam", "Danish Kaneria", "Ejaz Mahmood",
]

FEMALE_NAMES = [
    "Fatima Noor", "Ayesha Siddiqui", "Zainab Ali", "Maryam Khan", "Sana Malik",
    "Hira Bashir", "Nadia Hussain", "Rabia Butt", "Sadia Ahmed", "Uzma Akhtar",
    "Kiran Baloch", "Amna Ilyas", "Mehwish Hayat", "Sajal Ali", "Iqra Aziz",
]

FATHER_NAMES = [
    "Muhammad Akram", "Abdul Rashid", "Ghulam Mustafa", "Muhammad Aslam",
    "Abdul Qadir", "Muhammad Rafiq", "Haji Azeem", "Chaudhry Amir", "Malik Nadeem",
    "Sardar Iqbal", "Muhammad Nasir", "Abdul Wahab", "Muhammad Yousaf", "Haji Karim",
]

ADDRESSES = [
    "House 45, Street 12, Model Town, Lahore",
    "Flat 7, Block C, DHA Phase 5, Lahore",
    "234/B, Gulberg III, Lahore",
    "Shop 12, Liberty Market, Lahore",
    "House 78, Johar Town, Lahore",
    "45-B, Cantt Area, Rawalpindi",
    "House 23, Satellite Town, Rawalpindi",
    "Flat 3, F-8 Markaz, Islamabad",
    "House 56, G-11/4, Islamabad",
    "67-A, Clifton Block 5, Karachi",
    "House 89, Bahria Town, Lahore",
    "123, Wapda Town, Lahore",
    "House 34, Garden Town, Lahore",
    "Flat 9, Askari 10, Lahore Cantt",
]

DOCTOR_SPECS = [
    ("Dr. Ahmad Raza", "MBBS, FCPS (Medicine)", "General Medicine", 1500),
    ("Dr. Sana Fatima", "MBBS, FCPS (Surgery)", "Surgery", 2000),
    ("Dr. Khalid Mahmood", "MBBS, MRCP, FCPS (Cardiology)", "Cardiology", 3000),
    ("Dr. Nadia Hussain", "MBBS, MS (Ortho)", "Orthopedics", 2500),
    ("Dr. Asma Jabeen", "MBBS, FCPS (Gynae)", "Gynecology", 2000),
    ("Dr. Imran Shah", "MBBS, DCH, FCPS (Paeds)", "Pediatrics", 1500),
    ("Dr. Rashid Ali", "MBBS, DLO (ENT)", "ENT", 1500),
    ("Dr. Farah Naz", "MBBS, FCPS (Dermatology)", "Dermatology", 1800),
    ("Dr. Shahid Iqbal", "MBBS, FCPS (Neurology)", "Neurology", 3500),
    ("Dr. Ayesha Tariq", "MBBS, DMRD (Radiology)", "Radiology", 2000),
]

# (name, generic, category, manufacturer, price, cost, stock, supplier, supplier_phone, interaction_group)
MEDICINES = [
    ("Panadol 500mg", "Paracetamol", "Pain Relief", "GSK Pakistan", 25, 15, 500, "Medic Distributors", "042-37654321", ""),
    ("Augmentin 625mg", "Amoxicillin/Clavulanate", "Antibiotic", "GSK Pakistan", 120, 80, 200, "Medic Distributors", "042-37654321", "Antibiotic"),
    ("Flagyl 400mg", "Metronidazole", "Antibiotic", "Sanofi Pakistan", 35, 20, 350, "Al-Shifa Pharma", "042-36543210", "Antibiotic"),
    ("Brufen 400mg", "Ibuprofen", "Pain Relief", "Abbott Pakistan", 30, 18, 400, "Medicare Supplies", "042-35432109", "NSAID"),
    ("Omeprazole 20mg", "Omeprazole", "Gastric", "Getz Pharma", 45, 25, 300, "Health First Dist.", "042-34321098", ""),
    ("Amlodipine 5mg", "Amlodipine", "Cardiac", "Searle Pakistan", 55, 30, 250, "Cardio Suppliers", "042-33210987", ""),
    ("Metformin 500mg", "Metformin", "Diabetes", "Getz Pharma", 40, 22, 600, "Health First Dist.", "042-34321098", "Metformin"),
    ("Atorvastatin 20mg", "Atorvastatin", "Cholesterol", "Hilton Pharma", 75, 45, 180, "Prime Pharma", "042-32109876", "Statin"),
    ("Ceftriaxone 1g Inj", "Ceftriaxone", "Antibiotic", "Sami Pharma", 250, 150, 100, "Sami Distributors", "042-31098765", "Antibiotic"),
    ("Insulin Mixtard", "Insulin Human", "Diabetes", "Novo Nordisk", 1200, 900, 50, "Novo Nordisk Pak", "042-30987654", ""),
    ("Losartan 50mg", "Losartan", "Cardiac", "Searle Pakistan", 65, 35, 200, "Cardio Suppliers", "042-33210987", ""),
    ("Diclofenac 50mg", "Diclofenac", "Pain Relief", "Novartis Pakistan", 20, 12, 450, "Medicare Supplies", "042-35432109", "NSAID"),
    ("Ciprofloxacin 500mg", "Ciprofloxacin", "Antibiotic", "Searle Pakistan", 50, 28, 300, "Al-Shifa Pharma", "042-36543210", "Antibiotic"),
    ("Azithromycin 500mg", "Azithromycin", "Antibiotic", "Getz Pharma", 80, 45, 200, "Health First Dist.", "042-34321098", "Antibiotic"),
    ("Ranitidine 150mg", "Ranitidine", "Gastric", "GSK Pakistan", 35, 18, 400, "Medic Distributors", "042-37654321", ""),
    ("Montelukast 10mg", "Montelukast", "Respiratory", "Getz Pharma", 60, 35, 150, "Health First Dist.", "042-34321098", ""),
    ("Cetirizine 10mg", "Cetirizine", "Allergy", "GSK Pakistan", 20, 10, 500, "Medic Distributors", "042-37654321", ""),
    ("Prednisolone 5mg", "Prednisolone", "Steroid", "Sanofi Pakistan", 15, 8, 300, "Al-Shifa Pharma", "042-36543210", ""),
    ("Amoxicillin 500mg", "Amoxicillin", "Antibiotic", "GSK Pakistan", 40, 22, 400, "Medic Distributors", "042-37654321", "Antibiotic"),
    ("Aspirin 75mg", "Aspirin", "Cardiac", "Bayer Pakistan", 15, 8, 800, "Prime Pharma", "042-32109876", "Blood Thinner"),
    ("Enalapril 5mg", "Enalapril", "Cardiac", "Getz Pharma", 45, 25, 200, "Cardio Suppliers", "042-33210987", "ACE Inhibitor"),
    ("Glimepiride 2mg", "Glimepiride", "Diabetes", "Sanofi Pakistan", 50, 28, 250, "Al-Shifa Pharma", "042-36543210", ""),
    ("Pantoprazole 40mg", "Pantoprazole", "Gastric", "Hilton Pharma", 55, 30, 350, "Prime Pharma", "042-32109876", ""),
    ("Vitamin D3 200000IU", "Cholecalciferol", "Vitamin", "Sami Pharma", 300, 180, 100, "Sami Distributors", "042-31098765", ""),
    ("Multivitamins", "Multivitamins", "Vitamin", "Abbott Pakistan", 150, 90, 200, "Medicare Supplies", "042-35432109", ""),
    ("Warfarin 5mg", "Warfarin", "Cardiac", "Sanofi Pakistan", 30, 18, 150, "Al-Shifa Pharma", "042-36543210", "Blood Thinner"),
]

ALLERGIES = ["", "", "", "", "", "Penicillin", "Sulfa drugs", "Aspirin", "NSAIDs", "Latex"]
CHRONIC_CONDITIONS = ["", "", "", "", "", "Diabetes", "Hypertension", "Asthma", "Diabetes, Hypertension", "Arthritis"]

LAB_TESTS = [
    ("Complete Blood Count (CBC)", "Blood Test", 800),
    ("Blood Sugar Fasting", "Blood Test", 300),
    ("Blood Sugar Random", "Blood Test", 300),
    ("HbA1c", "Blood Test", 1200),
    ("Lipid Profile", "Blood Test", 1500),
    ("Liver Function Test (LFT)", "Blood Test", 1200),
    ("Kidney Function Test (RFT)", "Blood Test", 1000),
    ("Thyroid Profile (T3, T4, TSH)", "Blood Test", 2500),
    ("Urine R/E", "Urine Test", 300),
    ("Urine Culture", "Urine Test", 800),
    ("Chest X-Ray", "X-Ray", 1500),
    ("X-Ray Spine", "X-Ray", 2000),
    ("Ultrasound Abdomen", "Ultrasound", 3000),
    ("Echocardiography", "Ultrasound", 5000),
    ("ECG (12 Lead)", "ECG", 1000),
    ("CT Scan Brain", "CT Scan", 12000),
    ("MRI Brain", "MRI", 18000),
    ("MRI Spine", "MRI", 20000),
    ("Hepatitis B Surface Ag", "Blood Test", 800),
    ("COVID-19 PCR", "Blood Test", 2500),
]


def generate_demo_data():
    init_db()
    conn = get_conn()
    c = conn.cursor()

    # Check if demo data already exists
    c.execute("SELECT COUNT(*) FROM patients")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    # Add doctors
    for i, (name, qual, spec, fee) in enumerate(DOCTOR_SPECS, 1):
        did = f"DOC-{i:05d}"
        phone = f"0300-{random.randint(1000000, 9999999)}"
        dept = spec
        schedules = ["Mon-Fri 9AM-2PM", "Mon-Sat 10AM-4PM", "Mon-Wed-Fri 2PM-8PM",
                      "Tue-Thu-Sat 9AM-1PM", "Mon-Sat 9AM-5PM"]
        c.execute("""INSERT OR IGNORE INTO doctors (doctor_id, name, specialization, department, qualification, phone, fee, schedule)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                 (did, name, spec, dept, qual, phone, fee, random.choice(schedules)))

    # Add patients
    all_names = MALE_NAMES + FEMALE_NAMES
    for i, name in enumerate(all_names, 1):
        pid = f"PAT-{i:05d}"
        gender = "Male" if name in MALE_NAMES else "Female"
        age = random.randint(5, 75)
        cnic = f"{random.randint(30000, 45000)}-{random.randint(1000000, 9999999)}-{random.randint(1, 9)}"
        phone = f"03{random.randint(0, 4)}{random.randint(0, 9)}-{random.randint(1000000, 9999999)}"
        blood = random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        ptype = random.choice(["OPD", "OPD", "OPD", "IPD"])  # 75% OPD
        father = random.choice(FATHER_NAMES)
        addr = random.choice(ADDRESSES)

        allergy = random.choice(ALLERGIES)
        chronic = random.choice(CHRONIC_CONDITIONS)
        c.execute("""INSERT OR IGNORE INTO patients (patient_id, name, father_name, cnic, age, gender, phone, blood_group, patient_type, address, allergies, chronic_conditions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                 (pid, name, father, cnic, age, gender, phone, blood, ptype, addr, allergy, chronic))

    # Add appointments (last 7 days)
    for day_offset in range(7):
        date = (datetime.now() - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        num_appts = random.randint(8, 20)
        for token in range(1, num_appts + 1):
            pat = random.choice(all_names)
            pat_id = f"PAT-{all_names.index(pat) + 1:05d}"
            doc_idx = random.randint(0, len(DOCTOR_SPECS) - 1)
            doc_name, _, dept, fee = DOCTOR_SPECS[doc_idx]
            doc_id = f"DOC-{doc_idx + 1:05d}"
            time_str = f"{random.randint(9, 16)}:{random.choice(['00', '15', '30', '45'])}"
            status = random.choice(["Completed", "Completed", "Completed", "Waiting", "In Progress"]) if day_offset == 0 else "Completed"

            c.execute("""INSERT INTO appointments (token_no, patient_id, patient_name, doctor_id, doctor_name, department, date, time, fee, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     (token, pat_id, pat, doc_id, doc_name, dept, date, time_str, fee, status))

    # Add medicines
    for med in MEDICINES:
        name, generic, cat, mfg, price, cost, stock = med[0], med[1], med[2], med[3], med[4], med[5], med[6]
        supplier = med[7] if len(med) > 7 else ""
        sup_phone = med[8] if len(med) > 8 else ""
        interaction = med[9] if len(med) > 9 else ""
        batch = f"B{random.randint(1000, 9999)}"
        shelf = f"{random.choice('ABCDEFGH')}-{random.randint(1, 20)}"
        expiry = (datetime.now() + timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d")
        min_stock = random.choice([10, 20, 30, 50])

        c.execute("""INSERT OR IGNORE INTO medicines (name, generic_name, category, manufacturer, batch_no, price, cost_price, stock, min_stock, expiry_date, shelf_location, supplier, supplier_phone, interaction_group)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                 (name, generic, cat, mfg, batch, price, cost, stock, min_stock, expiry, shelf, supplier, sup_phone, interaction))

    # Add pharmacy sales
    for day_offset in range(7):
        date = (datetime.now() - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        num_sales = random.randint(5, 15)
        for s in range(num_sales):
            inv_no = f"PH-{date.replace('-', '')}{s:03d}"
            customer = random.choice(all_names + ["Walk-in"] * 5)
            num_items = random.randint(1, 5)
            total = 0
            items_data = []
            for _ in range(num_items):
                med = random.choice(MEDICINES)
                qty = random.randint(1, 5)
                item_total = qty * med[4]
                total += item_total
                items_data.append((med[0], qty, med[4], item_total))

            try:
                c.execute("""INSERT INTO pharmacy_sales (invoice_no, patient_name, items_count, subtotal, total, created_at)
                            VALUES (?, ?, ?, ?, ?, ?)""",
                         (inv_no, customer, len(items_data), total, total, f"{date} {random.randint(9, 17)}:{random.randint(0, 59):02d}:00"))
                sale_id = c.lastrowid
                for med_name, qty, price, itotal in items_data:
                    c.execute("""INSERT INTO pharmacy_sale_items (sale_id, medicine_name, quantity, price, total)
                                VALUES (?, ?, ?, ?, ?)""",
                             (sale_id, med_name, qty, price, itotal))
            except sqlite3.IntegrityError:
                pass

    # Add bills
    for day_offset in range(7):
        date = (datetime.now() - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        num_bills = random.randint(5, 12)
        for b in range(num_bills):
            bill_no = f"BILL-{date.replace('-', '')}{b:03d}"
            pat = random.choice(all_names)
            pat_id = f"PAT-{all_names.index(pat) + 1:05d}"
            btype = random.choice(["OPD", "OPD", "IPD", "Emergency"])
            consult = random.choice([1000, 1500, 2000, 2500, 3000])
            lab = random.choice([0, 0, 500, 1000, 1500, 2500])
            pharma = random.choice([0, 200, 500, 800, 1200])
            bed = random.choice([0, 0, 0, 2000, 4000, 8000]) if btype == "IPD" else 0
            other = random.choice([0, 0, 500])
            subtotal = consult + lab + pharma + bed + other
            discount = random.choice([0, 0, 0, 200, 500])
            grand = subtotal - discount
            pay = random.choice(["Cash", "Cash", "Card", "Online", "Insurance"])

            try:
                c.execute("""INSERT INTO bills (bill_no, patient_id, patient_name, bill_type,
                            consultation_fee, lab_charges, pharmacy_charges, bed_charges, other_charges,
                            subtotal, discount, grand_total, paid, balance, payment_method, payment_status, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (bill_no, pat_id, pat, btype, consult, lab, pharma, bed, other,
                          subtotal, discount, grand, grand, 0, pay, "Paid",
                          f"{date} {random.randint(9, 17)}:{random.randint(0, 59):02d}:00"))
            except sqlite3.IntegrityError:
                pass

    # Add lab tests
    for day_offset in range(7):
        date = (datetime.now() - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        num_tests = random.randint(3, 10)
        for t in range(num_tests):
            test_info = random.choice(LAB_TESTS)
            test_id = f"LAB-{date.replace('-', '')}{t:03d}"
            pat = random.choice(all_names)
            pat_id = f"PAT-{all_names.index(pat) + 1:05d}"
            doc = random.choice(DOCTOR_SPECS)
            status = "Completed" if day_offset > 0 else random.choice(["Pending", "Completed", "Completed"])
            result = "Normal" if status == "Completed" else ""

            try:
                c.execute("""INSERT INTO lab_tests (test_id, patient_id, patient_name, doctor_name, test_name, test_category, fee, result, status, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (test_id, pat_id, pat, doc[0], test_info[0], test_info[1], test_info[2],
                          result, status, f"{date} {random.randint(9, 17)}:{random.randint(0, 59):02d}:00"))
            except sqlite3.IntegrityError:
                pass

    # Add prescriptions
    for i in range(20):
        pat = random.choice(all_names)
        pat_id = f"PAT-{all_names.index(pat) + 1:05d}"
        doc = random.choice(DOCTOR_SPECS)
        doc_id = f"DOC-{DOCTOR_SPECS.index(doc) + 1:05d}"
        diagnoses = ["Fever & Flu", "Hypertension", "Type 2 Diabetes", "Gastritis", "Lower Back Pain",
                      "Urinary Tract Infection", "Bronchitis", "Skin Allergy", "Migraine", "Osteoarthritis"]
        meds_list = random.sample([m[0] for m in MEDICINES], k=random.randint(2, 5))
        date = (datetime.now() - timedelta(days=random.randint(0, 14))).strftime("%Y-%m-%d %H:%M:%S")
        followup = (datetime.now() + timedelta(days=random.randint(7, 30))).strftime("%Y-%m-%d")

        c.execute("""INSERT INTO prescriptions (patient_id, patient_name, doctor_id, doctor_name, diagnosis, medicines, instructions, follow_up, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                 (pat_id, pat, doc_id, doc[0], random.choice(diagnoses),
                  "\n".join(meds_list), "Take after meals\nComplete course\nDrink plenty of water",
                  followup, date))

    # Admit some patients
    c.execute("SELECT bed_no FROM beds WHERE status='Available' ORDER BY RANDOM() LIMIT 12")
    available_beds = [r[0] for r in c.fetchall()]
    ipd_patients = [(f"PAT-{all_names.index(p) + 1:05d}", p) for p in random.sample(all_names, min(12, len(available_beds)))]

    for (pid, pname), bed_no in zip(ipd_patients, available_beds):
        doc = random.choice(DOCTOR_SPECS)
        doc_id = f"DOC-{DOCTOR_SPECS.index(doc) + 1:05d}"
        adm_date = (datetime.now() - timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d")
        c.execute("""UPDATE beds SET status='Occupied', patient_id=?, patient_name=?,
                    admission_date=?, doctor_id=? WHERE bed_no=?""",
                 (pid, pname, adm_date, doc_id, bed_no))

    # Add patient vitals
    for i in range(30):
        pat = random.choice(all_names)
        pat_id = f"PAT-{all_names.index(pat) + 1:05d}"
        bp_sys = random.randint(100, 160)
        bp_dia = random.randint(60, 100)
        temp = round(random.uniform(97.0, 102.0), 1)
        pulse = random.randint(60, 110)
        weight = round(random.uniform(40.0, 110.0), 1)
        height = round(random.uniform(140.0, 185.0), 1)
        sugar = round(random.uniform(70.0, 250.0), 0)
        o2 = random.randint(92, 100)
        resp = random.randint(14, 24)
        date = (datetime.now() - timedelta(days=random.randint(0, 14))).strftime("%Y-%m-%d %H:%M:%S")
        recorder = random.choice(["Dr. Ahmad Raza", "Dr. Sana Fatima", "Nurse Fatima", "Nurse Hira"])

        c.execute("""INSERT INTO patient_vitals (patient_id, patient_name, blood_pressure, temperature, pulse,
                    weight, height, blood_sugar, oxygen_level, respiratory_rate, recorded_by, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                 (pat_id, pat, f"{bp_sys}/{bp_dia}", temp, pulse, weight, height, sugar, o2, resp, recorder, date))

    # Add some notifications inline
    c.execute("INSERT INTO notifications (title, message, category) VALUES (?,?,?)",
             ("System Started", "HMS initialized with demo data", "info"))
    c.execute("INSERT INTO notifications (title, message, category) VALUES (?,?,?)",
             ("Welcome", "Hospital Management System V2 is ready!", "success"))

    conn.commit()
    conn.close()
    print("Demo data generated successfully!")


if __name__ == "__main__":
    generate_demo_data()
