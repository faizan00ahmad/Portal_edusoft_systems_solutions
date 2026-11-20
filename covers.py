"""Generate a cover image per product: assets/covers/<slug>.svg

Every cover is a small, product-specific app screen (sidebar menu, figures, chart, list)
on a dark Edusoft-green stage tinted with the industry colour, so all cards share one look.
Edit SPEC below to change what a cover shows, then run:  python covers.py && python build.py
"""
import json, math, random
from pathlib import Path
from html import escape as e

ROOT = Path(__file__).parent
cat = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8-sig"))
raw = {r["id"]: r for r in json.loads((ROOT / "data.json").read_text(encoding="utf-8-sig"))}
COLORS = {"healthcare": "#0e8f9a", "education": "#5856d6", "retail": "#e2702a", "food": "#d9443a", "agri": "#6f9a1e", "enterprise": "#12884a"}
OUT = ROOT / "assets" / "covers"
FONT = "Inter, 'Segoe UI', Roboto, Arial, sans-serif"

# kpis: (label, value)  chart: bars|line|donut  rows: (title, meta, status)  chip: (title, sub)
SPEC = {
 "edubsstd-web": dict(screen="Dashboard", kpis=[("Sales today", "Rs 4.8L"), ("Receivable", "Rs 12.1L"), ("Stock items", "3,240")], chart="line",
                      rows=[("Invoice #10482", "Al-Noor Traders", "Paid"), ("Purchase #2291", "Metro Supply", "Due"), ("Voucher #771", "Cash book", "Posted")], chip=("Synced", "Desktop and web, one database")),
 "educampus-core-erp": dict(screen="Students", kpis=[("Students", "1,286"), ("Present today", "94%"), ("Campuses", "3")], chart="bars",
                      rows=[("Ayesha Khan", "Class 7-B", "Present"), ("Hamza Ali", "Class 9-A", "Present"), ("Sara Ahmed", "Class 5-C", "Leave")], chip=("Result cards", "Term 2 printed for 9-A")),
 "educampus-finance-accounts": dict(screen="Fee collection", kpis=[("Collected", "Rs 18.6L"), ("Pending", "Rs 2.4L"), ("Vouchers", "1,240")], chart="donut",
                      rows=[("Fee voucher Nov", "Class 8-A", "Paid"), ("Fee voucher Nov", "Class 6-B", "Due"), ("Late fee", "Class 10-A", "Paid")], chip=("Defaulters list", "SMS sent to 38 parents")),
 "hospital-management-hmis": dict(screen="Hospital overview", kpis=[("Admitted", "142"), ("Beds free", "28"), ("OT today", "9")], chart="bars",
                      rows=[("Ward B, Bed 12", "Dr. Imran", "Admitted"), ("OT-2", "Appendectomy", "In progress"), ("Discharge", "Room 204", "Billed")], chip=("Lab report ready", "MR# 22581 · CBC")),
 "poultry-erp": dict(screen="Flock performance", kpis=[("Live birds", "48,600"), ("Mortality", "1.8%"), ("Avg weight", "1.92 kg")], chart="line",
                      rows=[("Shed 3", "Day 28 · 12,400 birds", "On track"), ("Feed issue", "Starter · 40 bags", "Issued"), ("Vaccine", "ND + IB · Shed 1", "Due")], chip=("FCR 1.58", "Shed 3, best this cycle")),
 "sanitary-erp": dict(screen="Duty roster", kpis=[("Staff on duty", "86"), ("Areas covered", "24"), ("Complaints", "5")], chart="bars",
                      rows=[("Zone A · Block 4", "Morning shift", "Done"), ("Zone C · Market", "Evening shift", "Pending"), ("Zone B · Park", "Morning shift", "Done")], chip=("Attendance marked", "86 of 90 staff")),
 "electric-store-erp": dict(screen="Billing", kpis=[("Sales today", "Rs 2.1L"), ("Items", "4,820"), ("Low stock", "17")], chart="bars",
                      rows=[("LED bulb 12W", "x 24", "Rs 5,760"), ("Copper wire 7/29", "x 3 coil", "Rs 31,500"), ("Ceiling fan 56\"", "x 2", "Rs 23,000")], chip=("Barcode scanned", "Item added to bill")),
 "lab-diagnostic-erp": dict(screen="Test tracking", kpis=[("Samples today", "214"), ("Reports ready", "176"), ("Pending", "38")], chart="donut",
                      rows=[("CBC", "Sample S-8812", "Ready"), ("Lipid profile", "Sample S-8813", "Processing"), ("HbA1c", "Sample S-8815", "Collected")], chip=("Report printed", "Template: Lipid profile")),
 "patient-registration-token": dict(screen="Token counter", kpis=[("Registered", "318"), ("Waiting", "24"), ("Departments", "11")], chart="bars",
                      rows=[("Token 047", "Medicine OPD", "Called"), ("Token 048", "Paeds OPD", "Waiting"), ("Token 112", "Gynae OPD", "Waiting")], chip=("Now serving", "Token 047 · Room 3")),
 "opd-management": dict(screen="Appointments", kpis=[("Appointments", "96"), ("Doctors in", "14"), ("Avg wait", "12 min")], chart="line",
                      rows=[("10:30  Fatima Noor", "Dr. Saeed · Cardio", "Checked in"), ("10:45  Bilal Raza", "Dr. Hina · ENT", "Booked"), ("11:00  Usman Tariq", "Dr. Saeed · Cardio", "Booked")], chip=("Prescription saved", "Next visit in 2 weeks")),
 "financial-accounts": dict(screen="Balance sheet", kpis=[("Cash & bank", "Rs 36.2L"), ("Payables", "Rs 8.9L"), ("This month", "+12.4%")], chart="line",
                      rows=[("JV-1182", "Rent expense", "Posted"), ("BPV-406", "Supplier payment", "Posted"), ("CRV-915", "Customer receipt", "Draft")], chip=("Trial balance", "Debits equal credits")),
 "employee-payroll": dict(screen="Payroll · November", kpis=[("Employees", "212"), ("Net payroll", "Rs 74.5L"), ("On leave", "9")], chart="bars",
                      rows=[("Ahmed Raza", "Accounts", "Processed"), ("Maria Iqbal", "HR", "Processed"), ("Kashif Mehmood", "Sales", "On hold")], chip=("Salary slips", "212 slips generated")),
 "business-solutions-enterprise": dict(screen="Group overview", kpis=[("Companies", "4"), ("Branches", "17"), ("Revenue YTD", "Rs 9.4Cr")], chart="bars",
                      rows=[("Multan branch", "Sales · Stock · Accounts", "Live"), ("Lahore branch", "Sales · Stock", "Live"), ("Karachi warehouse", "Stock transfer", "In transit")], chip=("Consolidated", "All branches, one report")),
 "pharmacy-management": dict(screen="Counter sale", kpis=[("Sales today", "Rs 1.6L"), ("Near expiry", "23"), ("Branches", "3")], chart="donut",
                      rows=[("Panadol 500mg", "Batch P2231 · Exp 08/27", "x 2"), ("Augmentin 625", "Batch A9910 · Exp 03/27", "x 1"), ("Brufen syrup", "Batch B1140 · Exp 11/26", "x 1")], chip=("Expiry alert", "23 items within 90 days")),
 "digital-invoicing-fbr": dict(screen="FBR invoices", kpis=[("Invoices", "1,084"), ("Validated", "1,079"), ("Sales tax", "Rs 6.2L")], chart="line",
                      rows=[("INV-24-1084", "HS 8544.4910", "Validated"), ("INV-24-1083", "HS 3926.9099", "Validated"), ("INV-24-1082", "HS 8536.5090", "Retry")], chip=("FBR accepted", "QR code on invoice")),
 "restaurant-manager-app": dict(screen="Orders", kpis=[("Open tables", "7"), ("Orders", "63")], chart="bars",
                      rows=[("Table 4", "2x Karahi, 4x Naan", "Kitchen"), ("Table 9", "Biryani, Raita", "Served"), ("Takeaway 31", "Burger meal x3", "Ready")], chip=("Order sent", "Table 4 · to kitchen")),
 "business-solution-app": dict(screen="Order booking", kpis=[("Orders today", "41"), ("Collection", "Rs 3.2L")], chart="line",
                      rows=[("Al-Madina Store", "Balance Rs 42,300", "Booked"), ("City Mart", "Balance Rs 18,900", "Booked"), ("Rehman Traders", "Balance Rs 7,450", "Visit")], chip=("Stock check", "Item available: 340")),
 "electric-store-app": dict(screen="Quick sale", kpis=[("Sales today", "Rs 84K"), ("Bills", "37")], chart="bars",
                      rows=[("Switch 2-gang", "x 10", "Rs 2,400"), ("LED tube 20W", "x 6", "Rs 3,900"), ("Extension board", "x 2", "Rs 1,800")], chip=("Day summary", "37 bills · Rs 84K")),
}

def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]; b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))

def T(x, y, s, size=11, fill="#1b2a22", weight=500, anchor="start", op=1):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" opacity="{op}">{e(s)}</text>'

STATUS_GOOD = ("paid", "present", "done", "posted", "ready", "live", "processed", "validated", "served", "on track", "admitted", "billed", "called", "checked in", "issued", "booked")

def pill(x, y, s, c):
    good = s.lower() in STATUS_GOOD
    col = c if good else "#e08a12"
    w = 14 + len(s) * 6.1
    return (f'<rect x="{x - w:.0f}" y="{y - 13}" width="{w:.0f}" height="20" rx="10" fill="{col}" opacity=".13"/>'
            + T(x - w / 2, y + 1, s, 10, col, 700, "middle"))

def chart(kind, x, y, w, h, c, rnd):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#fff" stroke="#e6ece8"/>']
    out.append(T(x + 14, y + 22, "Last 12 weeks" if kind != "donut" else "This month", 10.5, "#6b7a71", 600))
    if kind == "bars":
        n, bw = 12, (w - 40) / 12
        for i in range(n):
            v = 0.3 + 0.6 * (0.5 + 0.5 * math.sin(i * 0.7 + rnd.random())) * (0.7 + i / n * 0.4)
            bh = (h - 52) * min(v, 1)
            op = 1 if i == n - 2 else .35 + .04 * i
            out.append(f'<rect x="{x + 20 + i * bw:.1f}" y="{y + h - 14 - bh:.1f}" width="{bw * .62:.1f}" height="{bh:.1f}" rx="3" fill="{c}" opacity="{op:.2f}"/>')
    elif kind == "line":
        pts = []
        for i in range(12):
            v = 0.25 + 0.5 * i / 11 + 0.15 * math.sin(i * 1.3 + rnd.random() * 2)
            pts.append((x + 18 + i * (w - 36) / 11, y + h - 16 - (h - 54) * v))
        d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)
        out.append(f'<path d="{d} L{pts[-1][0]:.1f},{y + h - 12} L{pts[0][0]:.1f},{y + h - 12} Z" fill="url(#area)"/>')
        out.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>')
        lx, ly = pts[-1]
        out.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="5" fill="#fff" stroke="{c}" stroke-width="2.6"/>')
    else:  # donut
        cx, cy, r = x + w * .32, y + h / 2 + 10, min(w, h) * .3
        segs, a0 = [(.62, 1), (.24, .55), (.14, .25)], -math.pi / 2
        for frac, op in segs:
            a1 = a0 + frac * 2 * math.pi
            big = 1 if frac > .5 else 0
            out.append(f'<path d="M{cx + r * math.cos(a0):.1f},{cy + r * math.sin(a0):.1f} A{r},{r} 0 {big} 1 {cx + r * math.cos(a1):.1f},{cy + r * math.sin(a1):.1f}" fill="none" stroke="{c}" stroke-opacity="{op}" stroke-width="{r * .42:.1f}"/>')
            a0 = a1
        out.append(T(cx, cy + 5, "62%", 15, "#1b2a22", 800, "middle"))
        for i, (lab, op) in enumerate([("Done", 1), ("In progress", .55), ("Pending", .25)]):
            ly = y + 52 + i * 24
            out.append(f'<rect x="{x + w * .62}" y="{ly - 9}" width="10" height="10" rx="3" fill="{c}" opacity="{op}"/>' + T(x + w * .62 + 16, ly, lab, 10.5, "#3b4a42", 600))
    return "".join(out)

def glyph(cx, cy, c):
    return (f'<circle cx="{cx}" cy="{cy}" r="17" fill="{c}"/>'
            f'<path d="M{cx - 7},{cy} l5,5 l9,-10" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')

def stage(c):
    dark = mix(c, "#04140c", .78); dark2 = mix(c, "#020a06", .9)
    grid = "".join(f'<path d="M{i * 40} 0 V500" stroke="#fff" stroke-opacity=".035"/>' for i in range(21)) + "".join(f'<path d="M0 {i * 40} H800" stroke="#fff" stroke-opacity=".035"/>' for i in range(13))
    return f'''<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{dark}"/><stop offset="1" stop-color="{dark2}"/></linearGradient>
<radialGradient id="glow" cx=".78" cy=".2" r=".6"><stop offset="0" stop-color="{c}" stop-opacity=".55"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>
<radialGradient id="glow2" cx=".05" cy="1" r=".5"><stop offset="0" stop-color="#f39a1e" stop-opacity=".28"/><stop offset="1" stop-color="#f39a1e" stop-opacity="0"/></radialGradient>
<linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c}" stop-opacity=".28"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></linearGradient>
<filter id="sh" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#000" flood-opacity=".38"/></filter>
<filter id="sh2" x="-30%" y="-40%" width="160%" height="200%"><feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="#000" flood-opacity=".3"/></filter>
</defs>
<rect width="800" height="500" fill="url(#bg)"/>{grid}<rect width="800" height="500" fill="url(#glow)"/><rect width="800" height="500" fill="url(#glow2)"/>'''

def desktop(p, s, c, rnd):
    X, Y, W, H = 70, 62, 690, 410  # window
    menu = [f[0] for f in p["features"]][:6]
    o = [f'<g filter="url(#sh)"><rect x="{X}" y="{Y}" width="{W}" height="{H}" rx="16" fill="#f7f9f7"/></g>']
    # title bar
    o.append(f'<path d="M{X} {Y + 16} a16 16 0 0 1 16 -16 h{W - 32} a16 16 0 0 1 16 16 v14 h-{W} z" fill="#fff"/>')
    o.append("".join(f'<circle cx="{X + 18 + i * 14}" cy="{Y + 16}" r="4.5" fill="{col}"/>' for i, col in enumerate(("#ff5f57", "#febc2e", "#28c840"))))
    o.append(f'<rect x="{X + W / 2 - 110}" y="{Y + 8}" width="220" height="16" rx="8" fill="#eef2ef"/>' + T(X + W / 2, Y + 20, f"{p['slug'].split('-')[0]}.edusoftsolutions.com", 9.5, "#6b7a71", 500, "middle"))
    # sidebar
    sx, sy, sw = X, Y + 30, 150
    o.append(f'<path d="M{sx} {sy} h{sw} v{H - 30} h-{sw - 16} a16 16 0 0 1 -16 -16 z" fill="{mix(c, "#0b1f15", .55)}"/>')
    o.append(f'<rect x="{sx + 14}" y="{sy + 14}" width="26" height="26" rx="8" fill="{c}"/>' + T(sx + 27, sy + 32, p["name"][0], 13, "#fff", 800, "middle"))
    short = p["name"].split("(")[0].replace("Management", "").replace("System", "").replace("Software", "").strip()
    short = short if len(short) <= 16 else short[:15] + "…"
    o.append(T(sx + 48, sy + 31, short, 11, "#fff", 700))
    for i, m in enumerate(menu):
        my = sy + 66 + i * 32
        if i == 0:
            o.append(f'<rect x="{sx + 10}" y="{my - 15}" width="{sw - 20}" height="26" rx="8" fill="#fff" opacity=".14"/><rect x="{sx + 10}" y="{my - 15}" width="3" height="26" rx="1.5" fill="#f39a1e"/>')
        o.append(f'<rect x="{sx + 20}" y="{my - 7}" width="10" height="10" rx="3" fill="#fff" opacity="{.95 if i == 0 else .4}"/>')
        o.append(T(sx + 38, my + 2, m if len(m) <= 18 else m[:17] + "…", 10, "#fff", 600 if i == 0 else 500, op=.95 if i == 0 else .62))
    # header
    cx0 = sx + sw + 22; cw = X + W - cx0 - 22
    o.append(T(cx0, Y + 66, s["screen"], 17, "#14231b", 800))
    o.append(T(cx0, Y + 84, "Edusoft · live demo", 10, "#7a887f", 500))
    o.append(f'<rect x="{X + W - 128}" y="{Y + 52}" width="106" height="26" rx="13" fill="{c}"/>' + T(X + W - 75, Y + 69, "+ New entry", 10.5, "#fff", 700, "middle"))
    # kpis
    ky, kw = Y + 100, (cw - 24) / 3
    for i, (lab, val) in enumerate(s["kpis"][:3]):
        kx = cx0 + i * (kw + 12)
        o.append(f'<rect x="{kx:.0f}" y="{ky}" width="{kw:.0f}" height="62" rx="12" fill="#fff" stroke="#e6ece8"/>')
        o.append(f'<rect x="{kx + 12:.0f}" y="{ky + 12}" width="6" height="6" rx="3" fill="{c if i != 2 else "#f39a1e"}"/>' + T(kx + 24, ky + 19, lab, 10, "#6b7a71", 600))
        o.append(T(kx + 12, ky + 46, val, 19, "#14231b", 800))
    # chart + list
    gy = ky + 76; gh = Y + H - gy - 18
    o.append(chart(s["chart"], cx0, gy, cw * .46, gh, c, rnd))
    lx = cx0 + cw * .46 + 12; lw = cw - cw * .46 - 12
    o.append(f'<rect x="{lx:.0f}" y="{gy}" width="{lw:.0f}" height="{gh}" rx="12" fill="#fff" stroke="#e6ece8"/>' + T(lx + 14, gy + 22, "Recent", 10.5, "#6b7a71", 600))
    for i, (t, m, st) in enumerate(s["rows"]):
        ry = gy + 50 + i * ((gh - 50) / 3)
        o.append(f'<circle cx="{lx + 26:.0f}" cy="{ry:.0f}" r="11" fill="{c}" opacity=".14"/>' + T(lx + 26, ry + 4, t[0], 10, c, 800, "middle"))
        o.append(T(lx + 44, ry - 2, t, 11, "#14231b", 700) + T(lx + 44, ry + 12, m, 9.5, "#7a887f", 500))
        o.append(pill(lx + lw - 12, ry + 2, st, c))
        if i < 2:
            o.append(f'<path d="M{lx + 14:.0f} {ry + (gh - 50) / 6 + 1:.0f} H{lx + lw - 14:.0f}" stroke="#eef2ef"/>')
    return "".join(o)

def phone(p, s, c, rnd):
    o = []
    # a blurred desktop window behind, for depth
    o.append(f'<g opacity=".22"><rect x="40" y="90" width="430" height="300" rx="14" fill="#fff"/><rect x="40" y="90" width="110" height="300" rx="14" fill="{c}"/>'
             + "".join(f'<rect x="{170 + i * 96}" y="130" width="84" height="50" rx="8" fill="{c}" opacity=".4"/>' for i in range(3))
             + "".join(f'<rect x="{180 + i * 22}" y="{340 - 30 - (i * 37 % 90)}" width="12" height="{30 + (i * 37 % 90)}" rx="3" fill="{c}"/>' for i in range(12)) + '</g>')
    PX, PY, PW, PH = 480, 28, 236, 470
    o.append(f'<g filter="url(#sh)"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="34" fill="#0d1511"/></g>')
    sx, sy, sw, sh = PX + 10, PY + 10, PW - 20, PH - 20
    o.append(f'<clipPath id="scr"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="26"/></clipPath><g clip-path="url(#scr)">')
    o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="#f5f7f5"/>')
    o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="118" fill="{c}"/><rect x="{sx}" y="{sy}" width="{sw}" height="118" fill="url(#glow)" opacity=".6"/>')
    o.append(f'<rect x="{sx + sw / 2 - 34}" y="{sy + 8}" width="68" height="16" rx="8" fill="#0d1511"/>')
    o.append(T(sx + 16, sy + 54, s["screen"], 16, "#fff", 800) + T(sx + 16, sy + 72, p["name"], 9.5, "#fff", 500, op=.8))
    for i, (lab, val) in enumerate(s["kpis"][:2]):
        kx = sx + 12 + i * ((sw - 32) / 2 + 8); kw = (sw - 32) / 2
        o.append(f'<g filter="url(#sh2)"><rect x="{kx:.0f}" y="{sy + 90}" width="{kw:.0f}" height="56" rx="12" fill="#fff"/></g>')
        o.append(T(kx + 10, sy + 109, lab, 9, "#6b7a71", 600) + T(kx + 10, sy + 132, val, 15, "#14231b", 800))
    o.append(chart(s["chart"], sx + 12, sy + 160, sw - 24, 110, c, rnd))
    for i, (t, m, st) in enumerate(s["rows"]):
        ry = sy + 284 + i * 42
        o.append(f'<rect x="{sx + 12}" y="{ry - 18}" width="{sw - 24}" height="40" rx="10" fill="#fff"/>')
        o.append(T(sx + 22, ry, t, 10.5, "#14231b", 700) + T(sx + 22, ry + 13, m if len(m) < 24 else m[:23] + "…", 8.5, "#7a887f", 500))
        o.append(pill(sx + sw - 20, ry + 2, st, c))
    o.append(f'<rect x="{sx + 12}" y="{sy + sh - 52}" width="{sw - 24}" height="36" rx="12" fill="{c}"/>' + T(sx + sw / 2, sy + sh - 29, "+ New order" if p["industry"] != "retail" else "+ New sale", 11, "#fff", 700, "middle"))
    o.append('</g>')
    return "".join(o)

def chip(s, c, x, y):
    t, sub = s["chip"]
    w = max(len(t) * 7.6, len(sub) * 5.9) + 70
    if x < 0: x = 800 + x - w  # negative x = distance from the right edge
    return (f'<g filter="url(#sh2)"><rect x="{x}" y="{y}" width="{w:.0f}" height="54" rx="14" fill="#fff"/></g>'
            + glyph(x + 28, y + 27, c) + T(x + 54, y + 24, t, 12.5, "#14231b", 800) + T(x + 54, y + 40, sub, 9.5, "#6b7a71", 500))

def cover(p):
    c = COLORS[p["industry"]]
    s = SPEC[p["slug"]]
    rnd = random.Random(p["id"])
    android = raw[p["id"]]["type"] == "android"
    body = phone(p, s, c, rnd) if android else desktop(p, s, c, rnd)
    ch = chip(s, c, 70, 380) if android else chip(s, c, -26, 424)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" font-family="{FONT}">'
            + stage(c) + body + ch + "</svg>")

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for p in cat["products"]:
        (OUT / f"{p['slug']}.svg").write_text(cover(p), encoding="utf-8")
    print("wrote", len(cat["products"]), "covers to", OUT)
