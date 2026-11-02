from bs4 import BeautifulSoup
import sqlite3
import glob
import os
import re

conn = sqlite3.connect("hil_intelligence.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS report_summary(
    report_name TEXT,
    test_script TEXT,
    hil_name TEXT,
    msid TEXT,
    vehicle_line TEXT,
    model_year TEXT,
    tester_id TEXT,
    total_tests INTEGER,
    passed INTEGER,
    failed INTEGER,
    na_count INTEGER,
    pass_rate REAL
)
""")

cur.execute("DELETE FROM report_summary")

for file in glob.glob("Reports/*.html"):

    print("Processing:", file)

    with open(file, encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "html.parser")

    tables = soup.find_all("table")

    summary_text = ""
    property_text = ""

    for table in tables:

        text = table.get_text(" ", strip=True)

        if "Total" in text and "Passed" in text:
            summary_text = text

        if "HIL Name" in text:
            property_text = text

    # summary
    total = int(re.search(r"Total\s+(\d+)", summary_text).group(1))
    passed = int(re.search(r"Passed\s+(\d+)", summary_text).group(1))
    failed = int(re.search(r"Failed\s+(\d+)", summary_text).group(1))
    na = int(re.search(r"NA\s+(\d+)", summary_text).group(1))

    # properties
    msid = re.search(r"MSID/TestReqID:\s*(\d+)", property_text)
    msid = msid.group(1) if msid else "Unknown"

    hil = re.search(r"HIL Name:\s*([A-Za-z0-9_]+)", property_text)
    hil = hil.group(1) if hil else "Unknown"

    tester = re.search(r"Tester ID:\s*([A-Za-z0-9_]+)", property_text)
    tester = tester.group(1) if tester else "Unknown"

    vehicle = re.search(r"Vehicle Line:\s*([A-Za-z0-9_]+)", property_text)
    vehicle = vehicle.group(1) if vehicle else "Unknown"

    model = re.search(r"Model Year:\s*(\d+)", property_text)
    model = model.group(1) if model else "Unknown"

    script = re.search(r"Test Script:\s*([A-Za-z0-9_.]+)", property_text)
    script = script.group(1) if script else os.path.basename(file)
    if total > 0:
        pass_rate = round((passed / total) * 100, 2)
    else:
        pass_rate = 0

    cur.execute("""
    INSERT INTO report_summary
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
    """,
    (
        os.path.basename(file),
        script,
        hil,
        msid,
        vehicle,
        model,
        tester,
        total,
        passed,
        failed,
        na,
        pass_rate
    ))

conn.commit()
conn.close()

print("VF Reports Imported Successfully")
