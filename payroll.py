"""
PayrollAI — Complete Payroll Management System
Pure Python / Tkinter — No CSS / No JS / No HTML
Theme: Deep Noir + Electric Indigo + Jade + Gold
Font: Yu Gothic UI / Trebuchet MS throughout
"""

import time
import datetime
import os
import pickle
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ── Optional imports ──────────────────────────────────────────────
try:
    import matplotlib

    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    HAS_MPL = True
except ImportError:
    HAS_MPL = False

try:
    import numpy as np

    HAS_NP = True
except ImportError:
    HAS_NP = False

try:
    from fpdf import FPDF

    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

# ══════════════════════════════════════════════════════════════════
#  DESIGN SYSTEM — Deep Noir + Electric Indigo + Jade + Gold
# ══════════════════════════════════════════════════════════════════
F = "Trebuchet MS"
F_MONO = "Courier New"

# Backgrounds
BG = "#080B12"
PANEL = "#0C1018"
CARD = "#101520"
CARD2 = "#141C28"
BORDER = "#1C2840"
INPUT = "#0A0E18"

# Accent colors
INDIGO = "#6366F1"
INDIGO2 = "#4F46E5"
JADE = "#10B981"
GOLD = "#F59E0B"
CRIMSON = "#EF4444"
SKY = "#38BDF8"
PINK = "#EC4899"
LIME = "#84CC16"

# Text
T1 = "#EDF2FF"
T2 = "#7B90C4"
T3 = "#2E4070"

CHART_COLORS = [
    "#6366F1",
    "#10B981",
    "#F59E0B",
    "#EF4444",
    "#38BDF8",
    "#EC4899",
    "#84CC16",
    "#8B5CF6",
]

# Font sizes — increased
SZ_PAGE = 28
SZ_CH = 17
SZ_BODY = 15
SZ_LABEL = 14
SZ_SMALL = 12
SZ_MONO = 13
SZ_KPI = 30

# ══════════════════════════════════════════════════════════════════
#  DATA CONSTANTS
# ══════════════════════════════════════════════════════════════════
EMPLOYEE_FILE = "employees.pkl"
SALARY_FILE = "salaries.pkl"

DESIGNATIONS = [
    "Intern",
    "Junior Developer",
    "Senior Developer",
    "Team Lead",
    "Manager",
    "Director",
    "VP",
    "CTO",
]

SALARY_BANDS = {
    "Intern": (15000, 25000),
    "Junior Developer": (30000, 55000),
    "Senior Developer": (60000, 100000),
    "Team Lead": (90000, 140000),
    "Manager": (120000, 180000),
    "Director": (160000, 250000),
    "VP": (220000, 350000),
    "CTO": (300000, 500000),
}


# ══════════════════════════════════════════════════════════════════
#  DATA LAYER
# ══════════════════════════════════════════════════════════════════
def load_data(path):
    if not os.path.exists(path):
        return []
    records = []
    with open(path, "rb") as f:
        while True:
            try:
                records.append(pickle.load(f))
            except EOFError:
                break
    return records


def save_all(path, records):
    with open(path, "wb") as f:
        for r in records:
            pickle.dump(r, f)


def next_emp_id(employees):
    if not employees:
        return "EMP001"
    ids = [int(e["id"][3:]) for e in employees if e["id"].startswith("EMP")]
    return f"EMP{max(ids)+1:03d}"


def compute_salary(basic):
    da = int(0.55 * basic)
    hra = int(0.35 * basic)
    conv = int(0.15 * basic)
    gross = basic + da + hra + conv
    tax = int(gross * 0.10)
    pf = int(basic * 0.12)
    return dict(
        basic=basic,
        da=da,
        hra=hra,
        conveyance=conv,
        gross=gross,
        income_tax=tax,
        pf=pf,
        loan=0,
        advance=0,
        net=gross - tax - pf,
    )


def predict_fair_salary(designation, years_exp):
    if designation not in SALARY_BANDS:
        return None
    lo, hi = SALARY_BANDS[designation]
    t = min(years_exp / 20, 1.0)
    return int(lo + (hi - lo) * (3 * t**2 - 2 * t**3))


def salary_status(salary, designation):
    if designation not in SALARY_BANDS:
        return "unknown"
    lo, hi = SALARY_BANDS[designation]
    if salary < lo * 0.85:
        return "low"
    if salary > hi * 1.15:
        return "high"
    return "fair"


# ══════════════════════════════════════════════════════════════════
#  WIDGET HELPERS
# ══════════════════════════════════════════════════════════════════
def hsep(parent, color=BORDER, pad=0):
    f = tk.Frame(parent, height=1, bg=color)
    if pad:
        f.pack(fill="x", padx=pad)
    return f


def card(parent, **kw):
    kw.setdefault("bg", CARD)
    kw.setdefault("highlightthickness", 1)
    kw.setdefault("highlightbackground", BORDER)
    return tk.Frame(parent, bd=0, **kw)


def field_entry(parent, var, width=28, mono=False):
    fnt = (F_MONO, SZ_MONO) if mono else (F, SZ_BODY)
    return tk.Entry(
        parent,
        textvariable=var,
        bg=INPUT,
        fg=T1,
        insertbackground=INDIGO,
        relief="flat",
        highlightthickness=1,
        highlightcolor=INDIGO,
        highlightbackground=BORDER,
        font=fnt,
        width=width,
    )


def action_btn(
    parent, text, cmd, bg=INDIGO, fg=T1, size=SZ_BODY, padx=22, pady=10, **kw
):
    return tk.Button(
        parent,
        text=text,
        command=cmd,
        bg=bg,
        fg=fg,
        activebackground=INDIGO2,
        activeforeground=T1,
        relief="flat",
        cursor="hand2",
        font=(F, size, "bold"),
        padx=padx,
        pady=pady,
        **kw,
    )


def ghost_btn(parent, text, cmd, size=SZ_BODY, **kw):
    kw.setdefault("padx", 20)
    kw.setdefault("pady", 10)
    return tk.Button(
        parent,
        text=text,
        command=cmd,
        bg=CARD2,
        fg=T2,
        activebackground=BORDER,
        activeforeground=T1,
        relief="flat",
        cursor="hand2",
        font=(F, size),
        **kw   # pady=12 from caller will win; pady=10 default used otherwise
    )


def page_header(parent, title, sub=""):
    hdr = tk.Frame(parent, bg=BG)
    hdr.pack(fill="x", padx=36, pady=(28, 0))
    tk.Label(hdr, text=title, font=(F, SZ_PAGE, "bold"), bg=BG, fg=T1).pack(side="left")
    if sub:
        tk.Label(hdr, text=sub, font=(F, SZ_SMALL), bg=BG, fg=T2).pack(
            side="left", padx=18
        )
    hsep(parent, pad=36).pack(fill="x", pady=(14, 0))


# ══════════════════════════════════════════════════════════════════
#  APP
# ══════════════════════════════════════════════════════════════════
class PayrollApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PayrollAI — Intelligent Payroll System")
        self.geometry("1520x900")
        self.minsize(1280, 760)
        self.configure(bg=BG)
        self.resizable(True, True)
        self._setup_ttk()
        self.employees = load_data(EMPLOYEE_FILE)
        self.salaries = load_data(SALARY_FILE)
        self._build_shell()
        self.show_tab("dashboard")

    def _setup_ttk(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(
            "App.Treeview",
            background=CARD2,
            foreground=T1,
            fieldbackground=CARD2,
            rowheight=46,
            font=(F, SZ_BODY),
            borderwidth=0,
        )
        s.configure(
            "App.Treeview.Heading",
            background=CARD,
            foreground=INDIGO,
            font=(F, SZ_LABEL, "bold"),
            relief="flat",
            padding=(14, 12),
        )
        s.map(
            "App.Treeview",
            background=[("selected", INDIGO)],
            foreground=[("selected", T1)],
        )
        s.configure(
            "App.TCombobox",
            fieldbackground=INPUT,
            background=INPUT,
            foreground=T1,
            selectbackground=INDIGO,
            selectforeground=T1,
            borderwidth=0,
            arrowcolor=T2,
        )
        s.map(
            "App.TCombobox",
            fieldbackground=[("readonly", INPUT)],
            foreground=[("readonly", T1)],
            background=[("readonly", INPUT)],
        )
        s.configure(
            "App.Vertical.TScrollbar",
            background=CARD2,
            troughcolor=CARD,
            bordercolor=BORDER,
            arrowcolor=T3,
            relief="flat",
        )

    def _build_shell(self):
        # ── Sidebar ──────────────────────────────────────────────
        self.sidebar = tk.Frame(self, bg=PANEL, width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        lf = tk.Frame(self.sidebar, bg=PANEL)
        lf.pack(fill="x", padx=24, pady=(32, 0))
        # Decorative accent bar
        tk.Frame(lf, bg=INDIGO, width=4, height=42).pack(side="left")
        lt = tk.Frame(lf, bg=PANEL)
        lt.pack(side="left", padx=14)
        tk.Label(lt, text="PayrollAI", font=(F, 20, "bold"), bg=PANEL, fg=T1).pack(
            anchor="w"
        )
        tk.Label(
            lt, text="Management System", font=(F, SZ_SMALL), bg=PANEL, fg=T3
        ).pack(anchor="w")

        tk.Frame(self.sidebar, height=1, bg=BORDER).pack(fill="x", pady=(26, 10))
        tk.Label(
            self.sidebar,
            text="NAVIGATION",
            font=(F, 10, "bold"),
            bg=PANEL,
            fg=T3,
            anchor="w",
        ).pack(fill="x", padx=26, pady=(4, 8))

        self.nav_btns = {}
        for key, icon, label in [
            ("dashboard", "▦", "Dashboard"),
            ("add", "＋", "Add Employee"),
            ("employees", "☰", "All Employees"),
            ("payslip", "◈", "Payslip"),
        ]:
            self._nav_btn(key, icon, label)

        tk.Frame(self.sidebar, height=1, bg=BORDER).pack(fill="x", pady=10)
        tk.Label(
            self.sidebar,
            text="AI TOOLS",
            font=(F, 10, "bold"),
            bg=PANEL,
            fg=T3,
            anchor="w",
        ).pack(fill="x", padx=26, pady=(4, 8))
        for key, icon, label in [
            ("analytics", "⬡", "AI Analytics"),
            ("deductions", "−", "Deductions"),
        ]:
            self._nav_btn(key, icon, label)

        # Footer
        tk.Frame(self.sidebar, height=1, bg=BORDER).pack(fill="x", side="bottom")
        foot = tk.Frame(self.sidebar, bg=PANEL)
        foot.pack(side="bottom", fill="x", padx=24, pady=16)
        dr = tk.Frame(foot, bg=PANEL)
        dr.pack(fill="x")
        tk.Label(dr, text="●", font=(F, 12, "bold"), bg=PANEL, fg=JADE).pack(
            side="left"
        )
        tk.Label(dr, text="  System Online", font=(F, SZ_SMALL), bg=PANEL, fg=T3).pack(
            side="left"
        )
        tk.Label(
            foot,
            text=datetime.date.today().strftime("%d %B %Y"),
            font=(F, SZ_SMALL),
            bg=PANEL,
            fg=T3,
            anchor="w",
        ).pack(fill="x", pady=(8, 0))

        # ── Content area ─────────────────────────────────────────
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="right", fill="both", expand=True)
        self.frames = {}
        for key in [
            "dashboard",
            "add",
            "employees",
            "payslip",
            "analytics",
            "deductions",
        ]:
            f = tk.Frame(self.content, bg=BG)
            self.frames[key] = f
            f.place(relwidth=1, relheight=1)

        self._build_topbar()
        self._pg_dashboard()
        self._pg_add()
        self._pg_employees()
        self._pg_payslip()
        self._pg_analytics()
        self._pg_deductions()

    def _nav_btn(self, key, icon, label):
        row = tk.Frame(self.sidebar, bg=PANEL, cursor="hand2")
        row.pack(fill="x", padx=14, pady=3)
        # Active indicator bar
        ind = tk.Frame(row, bg=PANEL, width=3)
        ind.pack(side="left", fill="y")
        il = tk.Label(row, text=icon, font=(F, 14, "bold"), bg=PANEL, fg=T3, width=3)
        il.pack(side="left", padx=(8, 4), pady=12)
        tl = tk.Label(row, text=label, font=(F, SZ_BODY), bg=PANEL, fg=T2, anchor="w")
        tl.pack(side="left", fill="x", expand=True, pady=12)

        self.nav_btns[key] = (row, il, tl, ind)
        row._active = False

        for w in (row, il, tl, ind):
            w.bind("<Button-1>", lambda e, k=key: self.show_tab(k))
            w.bind(
                "<Enter>",
                lambda e, r=row, i=il, t=tl, d=ind: (
                    (
                        r.configure(bg=CARD2),
                        i.configure(bg=CARD2),
                        t.configure(bg=CARD2),
                        d.configure(bg=CARD2),
                    )
                    if not r._active
                    else None
                ),
            )
            w.bind(
                "<Leave>",
                lambda e, r=row, i=il, t=tl, d=ind: (
                    (
                        r.configure(bg=PANEL),
                        i.configure(bg=PANEL),
                        t.configure(bg=PANEL),
                        d.configure(bg=PANEL),
                    )
                    if not r._active
                    else None
                ),
            )

    def show_tab(self, key):
        self.frames[key].tkraise()
        titles = {
            "dashboard": ("Dashboard", "Overview of your payroll system"),
            "add": ("Add Employee", "Register a new team member"),
            "employees": ("All Employees", "Browse and manage workforce"),
            "payslip": ("Payslip", "Generate and export payslips"),
            "analytics": ("AI Analytics", "Intelligent salary insights"),
            "deductions": ("Deductions", "Manage employee deductions"),
        }
        t, s = titles.get(key, (key.title(), ""))
        self._tb_title.config(text=t)
        self._tb_sub.config(text=s)
        for k, (row, il, tl, ind) in self.nav_btns.items():
            a = k == key
            row._active = a
            if a:
                row.configure(bg=CARD2)
                il.configure(bg=CARD2, fg=INDIGO)
                tl.configure(bg=CARD2, fg=T1, font=(F, SZ_BODY, "bold"))
                ind.configure(bg=INDIGO)
            else:
                row.configure(bg=PANEL)
                il.configure(bg=PANEL, fg=T3)
                tl.configure(bg=PANEL, fg=T2, font=(F, SZ_BODY))
                ind.configure(bg=PANEL)

    def _build_topbar(self):
        bar = tk.Frame(self.content, bg=PANEL, height=68)
        bar.pack(side="top", fill="x")
        bar.pack_propagate(False)
        tk.Frame(bar, height=1, bg=BORDER).pack(side="bottom", fill="x")
        inn = tk.Frame(bar, bg=PANEL)
        inn.pack(fill="both", expand=True, padx=36)
        lft = tk.Frame(inn, bg=PANEL)
        lft.pack(side="left", fill="y")
        self._tb_title = tk.Label(
            lft, text="Dashboard", font=(F, 18, "bold"), bg=PANEL, fg=T1
        )
        self._tb_title.pack(side="left", anchor="center")
        self._tb_sub = tk.Label(lft, text="", font=(F, SZ_SMALL), bg=PANEL, fg=T2)
        self._tb_sub.pack(side="left", padx=18, anchor="center")
        rgt = tk.Frame(inn, bg=PANEL)
        rgt.pack(side="right", fill="y")
        dc = tk.Frame(rgt, bg=CARD2, highlightthickness=1, highlightbackground=BORDER)
        dc.pack(side="right", padx=(14, 0), pady=18)
        tk.Label(
            dc,
            text=datetime.date.today().strftime("%a, %d %b %Y"),
            font=(F, SZ_SMALL),
            bg=CARD2,
            fg=T2,
            padx=14,
            pady=5,
        ).pack()
        tk.Label(
            rgt,
            text="PA",
            font=(F, 12, "bold"),
            bg=INDIGO,
            fg=T1,
            width=3,
            padx=10,
            pady=7,
        ).pack(side="right", pady=14)

    # ══════════════════════════════════════════════════════════════
    #  DASHBOARD
    # ══════════════════════════════════════════════════════════════
    def _pg_dashboard(self):
        p = self.frames["dashboard"]
        page_header(p, "Dashboard Overview", "● LIVE")
        self.kpi_frame = tk.Frame(p, bg=BG)
        self.kpi_frame.pack(fill="x", padx=36, pady=24)
        kpis = [
            ("Total Employees", "👥", INDIGO, "Active headcount"),
            ("Monthly Payroll", "₹", JADE, "Gross this month"),
            ("Avg Net Salary", "≈", GOLD, "Per employee net"),
            ("Tax Collected", "⊕", CRIMSON, "Income tax + PF"),
        ]
        self.kpi_vars = {}
        for i, (title, icon, color, sub) in enumerate(kpis):
            self.kpi_frame.columnconfigure(i, weight=1)
            c = card(self.kpi_frame)
            c.grid(row=0, column=i, padx=9, sticky="ew")
            tk.Frame(c, bg=color, height=4).pack(fill="x")
            inn = tk.Frame(c, bg=CARD)
            inn.pack(fill="both", expand=True, padx=22, pady=20)
            top = tk.Frame(inn, bg=CARD)
            top.pack(fill="x")
            tk.Label(top, text=icon, font=(F, 24), bg=CARD, fg=color).pack(side="left")
            tk.Label(top, text=sub, font=(F, SZ_SMALL), bg=CARD, fg=T3).pack(
                side="right", anchor="se"
            )
            tk.Label(inn, text=title, font=(F, SZ_LABEL), bg=CARD, fg=T2).pack(
                anchor="w", pady=(10, 5)
            )
            v = tk.StringVar(value="—")
            self.kpi_vars[title] = v
            tk.Label(
                inn, textvariable=v, font=(F, SZ_KPI, "bold"), bg=CARD, fg=color
            ).pack(anchor="w")

        self.dcr = tk.Frame(p, bg=BG)
        self.dcr.pack(fill="both", expand=True, padx=36, pady=(0, 14))
        self.dcr.columnconfigure(0, weight=3)
        self.dcr.columnconfigure(1, weight=2)
        self.dash_bar = card(self.dcr)
        self.dash_bar.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self.dash_pie = card(self.dcr)
        self.dash_pie.grid(row=0, column=1, sticky="nsew")
        br = tk.Frame(p, bg=BG)
        br.pack(pady=(0, 18))
        action_btn(
            br,
            "⟳   Refresh Dashboard",
            self._refresh_dashboard,
            bg=INDIGO,
            padx=30,
            pady=12,
        ).pack()
        self._refresh_dashboard()

    def _refresh_dashboard(self):
        self.employees = load_data(EMPLOYEE_FILE)
        self.salaries = load_data(SALARY_FILE)
        n = len(self.employees)
        gross = sum(s["gross"] for s in self.salaries) if self.salaries else 0
        avg = int(sum(s["net"] for s in self.salaries) / n) if n else 0
        tax = sum(s["income_tax"] for s in self.salaries) if self.salaries else 0
        self.kpi_vars["Total Employees"].set(str(n))
        self.kpi_vars["Monthly Payroll"].set(f"₹{gross:,.0f}")
        self.kpi_vars["Avg Net Salary"].set(f"₹{avg:,.0f}")
        self.kpi_vars["Tax Collected"].set(f"₹{tax:,.0f}")
        if HAS_MPL:
            self._draw_dash_charts()

    def _draw_dash_charts(self):
        for w in self.dash_bar.winfo_children():
            w.destroy()
        for w in self.dash_pie.winfo_children():
            w.destroy()
        sm = {s["emp_id"]: s for s in self.salaries}

        fig1, ax1 = plt.subplots(figsize=(6.8, 3.6), facecolor=CARD)
        ax1.set_facecolor(CARD2)
        if self.employees and self.salaries:
            names, grosses, nets = [], [], []
            for e in self.employees[-10:]:
                s = sm.get(e["id"])
                if s:
                    names.append(e["name"].split()[0])
                    grosses.append(s["gross"])
                    nets.append(s["net"])
            x = range(len(names))
            w = 0.38
            ax1.bar(
                [i - w / 2 for i in x],
                grosses,
                width=w,
                color=INDIGO,
                alpha=0.85,
                label="Gross",
                zorder=3,
            )
            ax1.bar(
                [i + w / 2 for i in x],
                nets,
                width=w,
                color=JADE,
                alpha=0.9,
                label="Net",
                zorder=3,
            )
            ax1.set_xticks(list(x))
            ax1.set_xticklabels(names, color=T2, fontsize=11, rotation=20, ha="right")
            ax1.grid(axis="y", color=BORDER, linewidth=0.7, zorder=0)
            ax1.legend(
                facecolor=CARD,
                edgecolor=BORDER,
                labelcolor=T2,
                fontsize=11,
                framealpha=0.9,
            )
        ax1.set_title(
            "Gross vs Net Salary (Last 10)",
            color=T1,
            fontsize=13,
            fontweight="bold",
            pad=12,
        )
        ax1.tick_params(colors=T2, labelsize=11)
        for sp in ax1.spines.values():
            sp.set_color(BORDER)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"₹{v/1000:.0f}K"))
        fig1.tight_layout(pad=1.2)
        c1 = FigureCanvasTkAgg(fig1, master=self.dash_bar)
        c1.draw()
        c1.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)
        plt.close(fig1)

        counts = {}
        for e in self.employees:
            d = e.get("designation", "Unknown")
            counts[d] = counts.get(d, 0) + 1
        fig2, ax2 = plt.subplots(figsize=(4.2, 3.6), facecolor=CARD)
        ax2.set_facecolor(CARD)
        if counts:
            wedges, texts, pcts = ax2.pie(
                counts.values(),
                labels=None,
                autopct="%1.0f%%",
                startangle=90,
                colors=CHART_COLORS[: len(counts)],
                wedgeprops={"edgecolor": CARD, "linewidth": 2.8, "width": 0.62},
                pctdistance=0.78,
                textprops={"color": T1, "fontsize": 10},
            )
            for pt in pcts:
                pt.set_fontweight("bold")
                pt.set_color(CARD)
            ax2.legend(
                wedges,
                [f"{k} ({v})" for k, v in counts.items()],
                loc="lower center",
                bbox_to_anchor=(0.5, -0.24),
                ncol=2,
                fontsize=9,
                facecolor=CARD,
                edgecolor=BORDER,
                labelcolor=T2,
            )
        ax2.set_title("Team Breakdown", color=T1, fontsize=13, fontweight="bold", pad=8)
        fig2.tight_layout(pad=1.2)
        c2 = FigureCanvasTkAgg(fig2, master=self.dash_pie)
        c2.draw()
        c2.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)
        plt.close(fig2)

    # ══════════════════════════════════════════════════════════════
    #  ADD EMPLOYEE
    # ══════════════════════════════════════════════════════════════
    def _pg_add(self):
        p = self.frames["add"]
        page_header(p, "Add New Employee", "★ marks required fields")
        outer = tk.Frame(p, bg=BG)
        outer.pack(fill="both", expand=True, padx=36, pady=22)

        fc = card(outer)
        fc.pack(side="left", fill="both", expand=True, padx=(0, 18))
        tk.Frame(fc, bg=INDIGO, height=4).pack(fill="x")
        ct = tk.Frame(fc, bg=CARD)
        ct.pack(fill="x", padx=26, pady=(20, 0))
        tk.Label(
            ct, text="👤  Employee Details", font=(F, SZ_CH + 2, "bold"), bg=CARD, fg=T1
        ).pack(side="left")
        tk.Label(ct, text="★ Required", font=(F, SZ_SMALL), bg=CARD, fg=T3).pack(
            side="right"
        )
        hsep(fc, pad=26).pack(fill="x", pady=(16, 0))

        grid = tk.Frame(fc, bg=CARD)
        grid.pack(fill="both", expand=True, padx=26, pady=10)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        self.add_vars = {}

        def mf(parent, label, key, row, col, req=False):
            cell = tk.Frame(parent, bg=CARD)
            cell.grid(
                row=row,
                column=col,
                sticky="ew",
                padx=(0, 20) if col == 0 else 0,
                pady=11,
            )
            cell.columnconfigure(0, weight=1)
            lr = tk.Frame(cell, bg=CARD)
            lr.pack(fill="x", pady=(0, 6))
            tk.Label(
                lr,
                text="★  " if req else "   ",
                font=(F, SZ_SMALL, "bold"),
                bg=CARD,
                fg=INDIGO if req else T3,
            ).pack(side="left")
            tk.Label(lr, text=label, font=(F, SZ_LABEL, "bold"), bg=CARD, fg=T2).pack(
                side="left"
            )
            v = tk.StringVar()
            field_entry(cell, v).pack(fill="x", ipady=11)
            self.add_vars[key] = v

        mf(grid, "Full Name", "name", 0, 0, req=True)
        mf(grid, "Email Address", "email", 0, 1)
        mf(grid, "Phone Number", "phone", 1, 0)
        mf(grid, "Home Address", "address", 1, 1)
        mf(grid, "Joining Date", "join_date", 2, 0)
        mf(grid, "Date of Birth", "dob", 2, 1)
        mf(grid, "Basic Salary (₹)", "basic", 3, 0, req=True)
        mf(grid, "Years of Experience", "years_exp", 3, 1)

        dr = tk.Frame(fc, bg=CARD)
        dr.pack(fill="x", padx=26, pady=(4, 0))
        dr.columnconfigure(0, weight=1)
        dr.columnconfigure(1, weight=1)

        def dcell(parent, label, row, col):
            cell = tk.Frame(parent, bg=CARD)
            cell.grid(
                row=row,
                column=col,
                sticky="ew",
                padx=(0, 20) if col == 0 else 0,
                pady=11,
            )
            cell.columnconfigure(0, weight=1)
            tk.Label(
                cell, text=f"   {label}", font=(F, SZ_LABEL, "bold"), bg=CARD, fg=T2
            ).pack(anchor="w", pady=(0, 6))
            return cell

        dc = dcell(dr, "Designation", 0, 0)
        self.desig_var = tk.StringVar(value=DESIGNATIONS[0])
        dcb = ttk.Combobox(
            dc,
            textvariable=self.desig_var,
            values=DESIGNATIONS,
            state="readonly",
            font=(F, SZ_BODY),
            style="App.TCombobox",
        )
        dcb.pack(fill="x", ipady=9)
        dcb.bind("<<ComboboxSelected>>", self._on_desig_change)

        gc = dcell(dr, "Gender", 0, 1)
        self.sex_var = tk.StringVar(value="Male")
        ttk.Combobox(
            gc,
            textvariable=self.sex_var,
            values=["Male", "Female", "Other"],
            state="readonly",
            font=(F, SZ_BODY),
            style="App.TCombobox",
        ).pack(fill="x", ipady=9)

        hsep(fc, pad=26).pack(fill="x", pady=20)
        br = tk.Frame(fc, bg=CARD)
        br.pack(fill="x", padx=26, pady=(0, 26))
        action_btn(
            br,
            "＋   Add Employee",
            self._add_employee,
            bg=JADE,
            fg="#080B12",
            padx=32,
            pady=13,
        ).pack(side="left", padx=(0, 14))
        ghost_btn(br, "⊘   Clear Form", self._clear_add_form, pady=13).pack(side="left")
        tk.Label(
            br, text="ID is auto-generated", font=(F, SZ_SMALL), bg=CARD, fg=T3
        ).pack(side="right", padx=6)

        # AI panel
        ai = card(outer, width=400)
        ai.pack(side="right", fill="both")
        ai.pack_propagate(False)
        tk.Frame(ai, bg=SKY, height=4).pack(fill="x")
        aih = tk.Frame(ai, bg=CARD)
        aih.pack(fill="x", padx=24, pady=(22, 14))
        bf = tk.Frame(aih, bg=INDIGO)
        bf.pack(side="left")
        tk.Label(
            bf, text=" AI ", font=(F, 11, "bold"), bg=INDIGO, fg=T1, padx=8, pady=5
        ).pack()
        atc = tk.Frame(aih, bg=CARD)
        atc.pack(side="left", padx=14)
        tk.Label(
            atc, text="Salary Advisor", font=(F, SZ_CH + 1, "bold"), bg=CARD, fg=T1
        ).pack(anchor="w")
        tk.Label(
            atc, text="Polynomial regression model", font=(F, SZ_SMALL), bg=CARD, fg=SKY
        ).pack(anchor="w")
        hsep(ai, pad=24).pack(fill="x")
        tk.Label(
            ai,
            text=(
                "Predicts fair salary using a sigmoid-shaped\n"
                "polynomial curve (Hermite interpolation)\n"
                "trained on industry salary band data."
            ),
            font=(F, SZ_BODY),
            bg=CARD,
            fg=T2,
            justify="left",
        ).pack(anchor="w", padx=24, pady=18)
        action_btn(
            ai,
            "⬡   Predict Fair Salary",
            self._predict_salary,
            bg=INDIGO,
            fg=T1,
            padx=0,
            pady=15,
        ).pack(fill="x", padx=24, pady=(0, 18))
        hsep(ai, pad=24).pack(fill="x")
        tk.Label(
            ai, text="Prediction Output", font=(F, SZ_LABEL, "bold"), bg=CARD, fg=T3
        ).pack(anchor="w", padx=24, pady=(16, 10))
        rw = tk.Frame(ai, bg=INPUT, highlightthickness=1, highlightbackground=BORDER)
        rw.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        self.ai_result = tk.Text(
            rw,
            bg=INPUT,
            fg=T1,
            font=(F_MONO, SZ_MONO),
            relief="flat",
            wrap="word",
            highlightthickness=0,
            spacing1=6,
            spacing2=2,
            padx=16,
            pady=16,
        )
        self.ai_result.pack(fill="both", expand=True)
        self._reset_ai_text()

    def _reset_ai_text(self):
        self.ai_result.configure(state="normal")
        self.ai_result.delete("1.0", "end")
        self.ai_result.insert(
            "end",
            "  Select a designation and\n  enter years of experience,\n"
            "  then click Predict above.\n\n  ─────────────────────────\n"
            "  Output includes:\n  · Predicted basic/gross/net\n"
            "  · Salary band (min/max)\n  · Anomaly flag\n  · Full breakdown",
        )
        self.ai_result.configure(state="disabled")

    def _on_desig_change(self, _=None):
        self._predict_salary()

    def _predict_salary(self):
        self.ai_result.configure(state="normal")
        self.ai_result.delete("1.0", "end")
        desig = self.desig_var.get()
        try:
            yexp = float(self.add_vars["years_exp"].get() or "0")
        except Exception:
            yexp = 0
        try:
            given = float(self.add_vars["basic"].get() or "0")
        except Exception:
            given = 0
        pred = predict_fair_salary(desig, yexp)
        if pred is None:
            self.ai_result.insert("end", "  Unknown designation.\n")
            self.ai_result.configure(state="disabled")
            return
        sal = compute_salary(pred)
        band = SALARY_BANDS.get(desig, (0, 0))
        st = salary_status(int(given), desig) if given else None
        st_txt = {
            "low": "⚠  BELOW BAND",
            "fair": "✔  FAIR SALARY",
            "high": "▲  ABOVE BAND",
        }.get(st, "")
        result = (
            f"  Role        : {desig}\n  Experience  : {yexp:.0f} years\n\n"
            f"  ─────────────────────────\n  PREDICTED BASIC\n    ₹ {pred:>12,}\n\n"
            f"  GROSS SALARY\n    ₹ {sal['gross']:>12,}\n\n"
            f"  NET PAY (after tax & PF)\n    ₹ {sal['net']:>12,}\n\n"
            f"  ─────────────────────────\n  BAND  Min  ₹ {band[0]:>10,}\n"
            f"        Max  ₹ {band[1]:>10,}\n\n"
        )
        if st_txt:
            result += f"  STATUS :  {st_txt}\n\n"
        result += (
            f"  ─────────────────────────\n  DA  (55%) ₹ {sal['da']:>8,}\n"
            f"  HRA (35%) ₹ {sal['hra']:>8,}\n  Conv(15%) ₹ {sal['conveyance']:>8,}\n"
            f"  Tax (10%)-₹ {sal['income_tax']:>8,}\n  PF  (12%)-₹ {sal['pf']:>8,}\n\n"
            f"  f(t)=lo+(hi-lo)×(3t²-2t³)\n"
        )
        self.ai_result.insert("end", result)
        self.ai_result.configure(state="disabled")

    def _add_employee(self):
        self.employees = load_data(EMPLOYEE_FILE)
        self.salaries = load_data(SALARY_FILE)
        name = self.add_vars["name"].get().strip()
        bstr = self.add_vars["basic"].get().strip()
        if not name or not bstr:
            messagebox.showwarning(
                "Missing Fields", "Name and Basic Salary are required."
            )
            return
        try:
            basic = int(bstr)
        except Exception:
            messagebox.showerror("Invalid", "Basic Salary must be a whole number.")
            return
        emp_id = next_emp_id(self.employees)
        emp = {
            "id": emp_id,
            "name": name,
            "email": self.add_vars["email"].get().strip(),
            "phone": self.add_vars["phone"].get().strip(),
            "address": self.add_vars["address"].get().strip(),
            "join_date": self.add_vars["join_date"].get().strip()
            or str(datetime.date.today()),
            "dob": self.add_vars["dob"].get().strip(),
            "designation": self.desig_var.get(),
            "sex": self.sex_var.get(),
            "years_exp": self.add_vars["years_exp"].get().strip(),
            "basic": basic,
        }
        sal = compute_salary(basic)
        sal["emp_id"] = emp_id
        self.employees.append(emp)
        self.salaries.append(sal)
        save_all(EMPLOYEE_FILE, self.employees)
        save_all(SALARY_FILE, self.salaries)
        messagebox.showinfo("Employee Added", f"✔  {name} saved as {emp_id}")
        self._clear_add_form()
        self._refresh_employees_list()

    def _clear_add_form(self):
        for v in self.add_vars.values():
            v.set("")
        self.desig_var.set(DESIGNATIONS[0])
        self.sex_var.set("Male")
        self._reset_ai_text()

    # ══════════════════════════════════════════════════════════════
    #  ALL EMPLOYEES
    # ══════════════════════════════════════════════════════════════
    def _pg_employees(self):
        p = self.frames["employees"]
        page_header(p, "All Employees")
        tb = tk.Frame(p, bg=BG)
        tb.pack(fill="x", padx=36, pady=18)
        sf = tk.Frame(tb, bg=CARD2, highlightthickness=1, highlightbackground=BORDER)
        sf.pack(side="left")
        tk.Label(sf, text="🔍", font=(F, 14), bg=CARD2, fg=T3, padx=12).pack(
            side="left"
        )
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *_: self._refresh_employees_list())
        tk.Entry(
            sf,
            textvariable=self.search_var,
            bg=CARD2,
            fg=T1,
            insertbackground=INDIGO,
            relief="flat",
            font=(F, SZ_BODY),
            width=30,
        ).pack(side="left", pady=11, padx=(0, 14), ipady=5)
        self.emp_count_var = tk.StringVar(value="0 employees")
        tk.Label(
            tb,
            textvariable=self.emp_count_var,
            font=(F, SZ_SMALL),
            bg=BG,
            fg=T2,
            padx=16,
            pady=9,
        ).pack(side="left", padx=14)
        action_btn(
            tb,
            "⟳  Refresh",
            self._refresh_employees_list,
            bg=INDIGO,
            size=SZ_SMALL,
            padx=20,
            pady=9,
        ).pack(side="right")

        cols = ("ID", "Name", "Designation", "Basic", "Gross", "Net Pay", "Status")
        tw = tk.Frame(p, bg=BG)
        tw.pack(fill="both", expand=True, padx=36, pady=(0, 22))
        vsb = ttk.Scrollbar(tw, orient="vertical", style="App.Vertical.TScrollbar")
        vsb.pack(side="right", fill="y")
        self.emp_tree = ttk.Treeview(
            tw,
            columns=cols,
            show="headings",
            style="App.Treeview",
            yscrollcommand=vsb.set,
        )
        vsb.config(command=self.emp_tree.yview)
        self.emp_tree.pack(fill="both", expand=True)
        for col, w in zip(cols, [90, 190, 170, 120, 130, 130, 110]):
            self.emp_tree.heading(col, text=col)
            self.emp_tree.column(col, width=w, anchor="center", minwidth=w)
        self.emp_tree.tag_configure("fair", foreground=T1)
        self.emp_tree.tag_configure("low", foreground=GOLD)
        self.emp_tree.tag_configure("high", foreground=SKY)
        self._refresh_employees_list()

    def _refresh_employees_list(self, *_):
        self.employees = load_data(EMPLOYEE_FILE)
        self.salaries = load_data(SALARY_FILE)
        for row in self.emp_tree.get_children():
            self.emp_tree.delete(row)
        sm = {s["emp_id"]: s for s in self.salaries}
        query = self.search_var.get().lower() if hasattr(self, "search_var") else ""
        shown = 0
        for e in self.employees:
            if query and (
                query not in e["name"].lower()
                and query not in e["id"].lower()
                and query not in e.get("designation", "").lower()
            ):
                continue
            s = sm.get(e["id"], {})
            st = salary_status(e["basic"], e.get("designation", ""))
            si = {"fair": "✔ fair", "low": "⚠ low", "high": "▲ high"}.get(st, st)
            tag = st if st in ("fair", "low", "high") else "fair"
            self.emp_tree.insert(
                "",
                "end",
                tags=(tag,),
                values=(
                    e["id"],
                    e["name"],
                    e.get("designation", "—"),
                    f'₹{e["basic"]:,}',
                    f'₹{s.get("gross", 0):,}',
                    f'₹{s.get("net", 0):,}',
                    si,
                ),
            )
            shown += 1
        n = len(self.employees)
        self.emp_count_var.set(f"{shown} of {n} employee{'s' if n != 1 else ''}")

    # ══════════════════════════════════════════════════════════════
    #  PAYSLIP
    # ══════════════════════════════════════════════════════════════
    def _pg_payslip(self):
        p = self.frames["payslip"]
        page_header(p, "Generate Payslip")
        outer = tk.Frame(p, bg=BG)
        outer.pack(fill="both", expand=True, padx=36, pady=22)
        ctrl = card(outer, width=320)
        ctrl.pack(side="left", fill="y", padx=(0, 18))
        ctrl.pack_propagate(False)
        tk.Frame(ctrl, bg=INDIGO, height=4).pack(fill="x")
        inn = tk.Frame(ctrl, bg=CARD)
        inn.pack(fill="both", expand=True, padx=24, pady=22)
        tk.Label(
            inn, text="Lookup Employee", font=(F, SZ_CH, "bold"), bg=CARD, fg=T1
        ).pack(anchor="w")
        tk.Label(
            inn, text="Enter the employee ID below", font=(F, SZ_SMALL), bg=CARD, fg=T3
        ).pack(anchor="w", pady=(5, 18))
        tk.Label(
            inn, text="Employee ID", font=(F, SZ_LABEL, "bold"), bg=CARD, fg=T2
        ).pack(anchor="w", pady=(0, 6))
        self.payslip_id_var = tk.StringVar()
        field_entry(inn, self.payslip_id_var, width=22).pack(fill="x", ipady=11)
        tk.Frame(inn, height=14, bg=CARD).pack()
        action_btn(
            inn,
            "▶   Generate Payslip",
            self._generate_payslip,
            bg=INDIGO,
            padx=0,
            pady=13,
        ).pack(fill="x")
        hsep(inn).pack(fill="x", pady=16)
        if HAS_FPDF:
            action_btn(
                inn,
                "⇩   Export PDF",
                self._export_pdf,
                bg=JADE,
                fg="#080B12",
                padx=0,
                pady=13,
            ).pack(fill="x")
        else:
            tk.Label(
                inn,
                text="pip install fpdf2\nfor PDF export",
                font=(F, SZ_SMALL),
                bg=CARD,
                fg=T3,
                justify="center",
            ).pack(pady=5)

        self.payslip_preview = card(outer)
        self.payslip_preview.pack(side="right", fill="both", expand=True)
        self.payslip_text = tk.Text(
            self.payslip_preview,
            font=(F_MONO, SZ_MONO + 1),
            bg=CARD,
            fg=T1,
            relief="flat",
            wrap="none",
            highlightthickness=0,
            spacing1=7,
            spacing2=2,
            padx=30,
            pady=26,
        )
        self.payslip_text.pack(fill="both", expand=True)
        self.payslip_text.insert(
            "end",
            "\n\n\n   ◈  PayrollAI Payslip Generator\n\n"
            "   Enter an Employee ID in the panel\n"
            "   on the left and click Generate.\n\n"
            "   The formatted payslip will appear\n"
            "   here, ready to review or export.",
        )
        self.payslip_text.configure(state="disabled")

    def _generate_payslip(self):
        self.employees = load_data(EMPLOYEE_FILE)
        self.salaries = load_data(SALARY_FILE)
        eid = self.payslip_id_var.get().strip().upper()
        emp = next((e for e in self.employees if e["id"] == eid), None)
        if not emp:
            messagebox.showerror("Not Found", f"No employee found with ID {eid}")
            return
        sal = next((s for s in self.salaries if s["emp_id"] == eid), None)
        if not sal:
            messagebox.showerror("Data Error", "Salary record missing.")
            return
        now = datetime.datetime.now()
        ded = (
            sal.get("income_tax", 0)
            + sal.get("pf", 0)
            + sal.get("loan", 0)
            + sal.get("advance", 0)
        )
        slip = (
            f"\n  ╔══════════════════════════════════════════════╗\n"
            f"  ║           PayrollAI  —  PAY SLIP            ║\n"
            f"  ╚══════════════════════════════════════════════╝\n\n"
            f"  Period       :  {now.strftime('%B %Y')}\n"
            f"  Generated    :  {now.strftime('%d/%m/%Y  %H:%M')}\n\n"
            f"  ──────────────────────────────────────────────\n"
            f"  Employee ID  :  {emp['id']}\n"
            f"  Name         :  {emp['name']}\n"
            f"  Designation  :  {emp.get('designation', '—')}\n"
            f"  Joining Date :  {emp.get('join_date', '—')}\n\n"
            f"  ──────────────────────────────────────────────\n"
            f"  EARNINGS\n"
            f"  ──────────────────────────────────────────────\n"
            f"  Basic Salary      ₹  {sal['basic']:>12,}\n"
            f"  DA         (55%)  ₹  {sal['da']:>12,}\n"
            f"  HRA        (35%)  ₹  {sal['hra']:>12,}\n"
            f"  Conveyance (15%)  ₹  {sal['conveyance']:>12,}\n"
            f"  ──────────────────────────────────────────────\n"
            f"  GROSS SALARY      ₹  {sal['gross']:>12,}\n\n"
            f"  DEDUCTIONS\n"
            f"  ──────────────────────────────────────────────\n"
            f"  Income Tax (10%)  ₹  {sal['income_tax']:>12,}\n"
            f"  PF         (12%)  ₹  {sal['pf']:>12,}\n"
            f"  Loan              ₹  {sal.get('loan', 0):>12,}\n"
            f"  Advance           ₹  {sal.get('advance', 0):>12,}\n"
            f"  ──────────────────────────────────────────────\n"
            f"  TOTAL DEDUCTIONS  ₹  {ded:>12,}\n\n"
            f"  ══════════════════════════════════════════════\n"
            f"  NET PAY           ₹  {sal['net']:>12,}\n"
            f"  ══════════════════════════════════════════════\n\n"
            f"  Computer-generated payslip. No signature required.\n"
            f"  PayrollAI v2.0\n"
        )
        self.payslip_text.configure(state="normal")
        self.payslip_text.delete("1.0", "end")
        self.payslip_text.insert("end", slip)
        self.payslip_text.configure(state="disabled")
        self._last_payslip = slip

    def _export_pdf(self):
        if not hasattr(self, "_last_payslip"):
            messagebox.showinfo("No Payslip", "Generate a payslip first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=f"payslip_{self.payslip_id_var.get()}.pdf",
        )
        if not path:
            return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Courier", size=11)
        for line in self._last_payslip.split("\n"):
            pdf.cell(0, 7, line, ln=True)
        pdf.output(path)
        messagebox.showinfo("Exported", f"Payslip saved:\n{path}")

    # ══════════════════════════════════════════════════════════════
    #  AI ANALYTICS
    # ══════════════════════════════════════════════════════════════
    def _pg_analytics(self):
        p = self.frames["analytics"]
        page_header(
            p, "⬡  AI Analytics", "Intelligent salary insights and workforce analysis"
        )
        br = tk.Frame(p, bg=BG)
        br.pack(fill="x", padx=36, pady=18)
        self._abns = {}
        for key, label in [
            ("dist", "▦  Salary Distribution"),
            ("exp", "⬡  Salary vs Experience"),
            ("anomaly", "▣  Anomaly Report"),
            ("proj", "▲  6-Mo Projection"),
        ]:
            b = tk.Button(
                br,
                text=label,
                bg=CARD2,
                fg=T2,
                activebackground=INDIGO,
                activeforeground=T1,
                relief="flat",
                cursor="hand2",
                font=(F, SZ_BODY),
                padx=20,
                pady=10,
                highlightthickness=1,
                highlightbackground=BORDER,
                command=lambda k=key: self._show_analytics(k),
            )
            b.pack(side="left", padx=(0, 10))
            self._abns[key] = b
        self.analytics_frame = card(p)
        self.analytics_frame.pack(fill="both", expand=True, padx=36, pady=(0, 26))
        self._show_analytics("dist")

    def _show_analytics(self, kind):
        for k, b in self._abns.items():
            if k == kind:
                b.configure(bg=INDIGO, fg=T1, font=(F, SZ_BODY, "bold"))
            else:
                b.configure(bg=CARD2, fg=T2, font=(F, SZ_BODY))
        if not HAS_MPL:
            messagebox.showinfo("Missing", "pip install matplotlib")
            return
        for w in self.analytics_frame.winfo_children():
            w.destroy()
        self.employees = load_data(EMPLOYEE_FILE)
        self.salaries = load_data(SALARY_FILE)
        if not self.employees:
            tk.Label(
                self.analytics_frame,
                text="No employee data. Add employees first.",
                font=(F, SZ_CH),
                bg=CARD,
                fg=T3,
            ).pack(pady=60)
            return
        sm = {s["emp_id"]: s for s in self.salaries}
        fig, ax = plt.subplots(figsize=(10, 5.0), facecolor=CARD)
        ax.set_facecolor(CARD2)

        if kind == "dist":
            nets = [sm[e["id"]]["net"] for e in self.employees if e["id"] in sm]
            if nets:
                bins = np.linspace(min(nets), max(nets), 15) if HAS_NP else 12
                ax.hist(
                    nets,
                    bins=bins,
                    color=INDIGO,
                    edgecolor=CARD,
                    alpha=0.85,
                    rwidth=0.88,
                )
                ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
            ax.set_xlabel("Net Monthly Salary (₹)", color=T2, fontsize=12)
            ax.set_ylabel("Number of Employees", color=T2, fontsize=12)
            ax.set_title(
                "Net Salary Distribution",
                color=T1,
                fontsize=15,
                fontweight="bold",
                pad=14,
            )
            ax.xaxis.set_major_formatter(
                plt.FuncFormatter(lambda v, _: f"₹{v/1000:.0f}K")
            )

        elif kind == "exp":
            xs, ys, names = [], [], []
            for e in self.employees:
                try:
                    yexp = float(e.get("years_exp") or 0)
                    net = sm[e["id"]]["net"]
                    xs.append(yexp)
                    ys.append(net)
                    names.append(e["name"].split()[0])
                except Exception:
                    pass
            ax.scatter(
                xs,
                ys,
                color=INDIGO,
                s=100,
                zorder=5,
                alpha=0.9,
                edgecolors=CARD,
                linewidths=1.8,
            )
            if HAS_NP and len(xs) > 2:
                z = np.polyfit(xs, ys, 1)
                pf = np.poly1d(z)
                xr = np.linspace(min(xs), max(xs), 100)
                ax.plot(xr, pf(xr), "--", color=SKY, linewidth=2.2, label="Trend line")
                ax.legend(facecolor=CARD, edgecolor=BORDER, labelcolor=T2, fontsize=11)
            for i, name in enumerate(names):
                ax.annotate(
                    name,
                    (xs[i], ys[i]),
                    fontsize=9,
                    color=T2,
                    xytext=(7, 7),
                    textcoords="offset points",
                )
            ax.set_xlabel("Years of Experience", color=T2, fontsize=12)
            ax.set_ylabel("Net Salary (₹)", color=T2, fontsize=12)
            ax.set_title(
                "Salary vs Experience", color=T1, fontsize=15, fontweight="bold", pad=14
            )
            ax.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda v, _: f"₹{v/1000:.0f}K")
            )

        elif kind == "anomaly":
            low = fair = high = 0
            for e in self.employees:
                st = salary_status(e["basic"], e.get("designation", ""))
                if st == "low":
                    low += 1
                elif st == "fair":
                    fair += 1
                elif st == "high":
                    high += 1
            bars = ax.bar(
                ["Below Band", "Fair", "Above Band"],
                [low, fair, high],
                color=[GOLD, JADE, SKY],
                edgecolor=CARD,
                width=0.5,
                zorder=3,
            )
            for bar, val in zip(bars, [low, fair, high]):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.05,
                    str(val),
                    ha="center",
                    va="bottom",
                    color=T1,
                    fontsize=15,
                    fontweight="bold",
                )
            ax.set_title(
                "Salary Anomaly Detection",
                color=T1,
                fontsize=15,
                fontweight="bold",
                pad=14,
            )
            ax.set_ylabel("Number of Employees", color=T2, fontsize=12)
            ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
            ax.grid(axis="y", color=BORDER, linewidth=0.7, zorder=0)

        elif kind == "proj":
            if not HAS_NP:
                tk.Label(
                    self.analytics_frame,
                    text="NumPy required: pip install numpy",
                    font=(F, SZ_CH),
                    bg=CARD,
                    fg=GOLD,
                ).pack(pady=60)
                plt.close(fig)
                return
            total = sum(s["gross"] for s in self.salaries) if self.salaries else 0
            months = [f"M+{i}" for i in range(7)]
            proj = [total * (1.03**i) for i in range(7)]
            ax.fill_between(range(7), proj, alpha=0.12, color=JADE, zorder=1)
            ax.plot(
                range(7),
                proj,
                color=JADE,
                linewidth=2.8,
                marker="o",
                markersize=9,
                markerfacecolor=JADE,
                markeredgecolor=CARD,
                markeredgewidth=2.2,
                zorder=3,
                label="Projected payroll",
            )
            for i, v in enumerate(proj):
                ax.annotate(
                    f"₹{v/1000:.0f}K",
                    (i, proj[i]),
                    textcoords="offset points",
                    xytext=(0, 14),
                    ha="center",
                    color=T2,
                    fontsize=10,
                )
            ax.set_xticks(range(7))
            ax.set_xticklabels(months, color=T2, fontsize=11)
            ax.set_title(
                "Projected Payroll — Next 6 Months (3% growth)",
                color=T1,
                fontsize=15,
                fontweight="bold",
                pad=14,
            )
            ax.set_ylabel("Monthly Payroll (₹)", color=T2, fontsize=12)
            ax.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda v, _: f"₹{v/1000:.0f}K")
            )
            ax.legend(facecolor=CARD, edgecolor=BORDER, labelcolor=T2, fontsize=11)
            ax.grid(axis="y", color=BORDER, linewidth=0.7, zorder=0)

        ax.tick_params(colors=T2, labelsize=11)
        for sp in ax.spines.values():
            sp.set_color(BORDER)
        fig.tight_layout(pad=1.5)
        canvas = FigureCanvasTkAgg(fig, master=self.analytics_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)
        plt.close(fig)

    # ══════════════════════════════════════════════════════════════
    #  DEDUCTIONS
    # ══════════════════════════════════════════════════════════════
    def _pg_deductions(self):
        p = self.frames["deductions"]
        page_header(
            p, "Manage Deductions", "Adjust income tax, loan and advance deductions"
        )
        outer = tk.Frame(p, bg=BG)
        outer.pack(fill="both", expand=True, padx=36, pady=22)

        lk = card(outer, width=340)
        lk.pack(side="left", fill="y", padx=(0, 18))
        lk.pack_propagate(False)
        tk.Frame(lk, bg=GOLD, height=4).pack(fill="x")
        li = tk.Frame(lk, bg=CARD)
        li.pack(fill="both", expand=True, padx=24, pady=22)
        tk.Label(
            li, text="Employee Lookup", font=(F, SZ_CH, "bold"), bg=CARD, fg=T1
        ).pack(anchor="w")
        tk.Label(
            li,
            text="Load an employee to edit deductions",
            font=(F, SZ_SMALL),
            bg=CARD,
            fg=T3,
        ).pack(anchor="w", pady=(5, 20))
        tk.Label(
            li, text="Employee ID", font=(F, SZ_LABEL, "bold"), bg=CARD, fg=T2
        ).pack(anchor="w", pady=(0, 7))
        self.ded_id_var = tk.StringVar()
        field_entry(li, self.ded_id_var, width=20).pack(fill="x", ipady=11)
        tk.Frame(li, height=12, bg=CARD).pack()
        action_btn(
            li, "▶   Load Employee", self._load_deductions, bg=INDIGO, padx=0, pady=13
        ).pack(fill="x")

        self.ded_info_frame = tk.Frame(
            li, bg=INPUT, highlightthickness=1, highlightbackground=BORDER
        )
        self.ded_info_frame.pack(fill="x", pady=(18, 0))
        self.ded_info_frame.pack_forget()
        self.ded_name_lbl = tk.Label(
            self.ded_info_frame, text="", font=(F, SZ_BODY + 1, "bold"), bg=INPUT, fg=T1
        )
        self.ded_name_lbl.pack(anchor="w", padx=16, pady=(14, 5))
        self.ded_gross_lbl = tk.Label(
            self.ded_info_frame, text="", font=(F, SZ_SMALL), bg=INPUT, fg=T2
        )
        self.ded_gross_lbl.pack(anchor="w", padx=16)
        self.ded_net_lbl = tk.Label(
            self.ded_info_frame, text="", font=(F, SZ_LABEL, "bold"), bg=INPUT, fg=JADE
        )
        self.ded_net_lbl.pack(anchor="w", padx=16, pady=(3, 14))

        rgt = card(outer)
        rgt.pack(side="right", fill="both", expand=True)
        tk.Frame(rgt, bg=INDIGO, height=4).pack(fill="x")
        rf = tk.Frame(rgt, bg=CARD)
        rf.pack(fill="both", expand=True, padx=30, pady=26)
        tk.Label(
            rf, text="Deduction Settings", font=(F, SZ_CH + 1, "bold"), bg=CARD, fg=T1
        ).pack(anchor="w")
        tk.Label(
            rf,
            text="Override auto-calculated deduction amounts",
            font=(F, SZ_SMALL),
            bg=CARD,
            fg=T3,
        ).pack(anchor="w", pady=(5, 22))

        self.ded_vars = {}
        for key, label, hint, color, icon in [
            (
                "ded_tax",
                "Income Tax (₹)",
                "Auto-calculated at 10% of gross salary",
                INDIGO,
                "⊕",
            ),
            (
                "ded_loan",
                "Loan Deduction (₹)",
                "Monthly EMI or loan repayment amount",
                GOLD,
                "⊘",
            ),
            (
                "ded_advance",
                "Salary Advance (₹)",
                "Amount drawn as advance this month",
                CRIMSON,
                "▼",
            ),
        ]:
            blk = tk.Frame(
                rf, bg=CARD2, highlightthickness=1, highlightbackground=BORDER
            )
            blk.pack(fill="x", pady=9)
            lc = tk.Frame(blk, bg=CARD2)
            lc.pack(side="left", fill="both", expand=True, padx=18, pady=16)
            top = tk.Frame(lc, bg=CARD2)
            top.pack(fill="x")
            tk.Label(top, text=icon, font=(F, 14, "bold"), bg=CARD2, fg=color).pack(
                side="left"
            )
            tk.Label(
                top, text=f"  {label}", font=(F, SZ_LABEL, "bold"), bg=CARD2, fg=T1
            ).pack(side="left")
            tk.Label(lc, text=hint, font=(F, SZ_SMALL), bg=CARD2, fg=T3).pack(
                anchor="w", pady=(4, 0)
            )
            v = tk.StringVar(value="0")
            self.ded_vars[key] = v
            tk.Entry(
                blk,
                textvariable=v,
                bg=INPUT,
                fg=T1,
                insertbackground=INDIGO,
                relief="flat",
                highlightthickness=1,
                highlightcolor=color,
                highlightbackground=BORDER,
                font=(F_MONO, SZ_MONO + 1),
                width=14,
                justify="right",
            ).pack(side="right", padx=18, pady=16, ipady=9)

        hsep(rf, pad=0).pack(fill="x", pady=22)
        ar = tk.Frame(rf, bg=CARD)
        ar.pack(fill="x")
        action_btn(
            ar,
            "✔   Apply Deductions",
            self._apply_deductions,
            bg=JADE,
            fg="#080B12",
            padx=28,
            pady=13,
        ).pack(side="left", padx=(0, 14))
        ghost_btn(ar, "⊘   Clear", self._clear_deductions, pady=13).pack(side="left")

    def _load_deductions(self):
        self.employees = load_data(EMPLOYEE_FILE)
        self.salaries = load_data(SALARY_FILE)
        eid = self.ded_id_var.get().strip().upper()
        emp = next((e for e in self.employees if e["id"] == eid), None)
        sal = next((s for s in self.salaries if s["emp_id"] == eid), None)
        if not emp or not sal:
            messagebox.showerror("Not Found", f"Employee {eid} not found.")
            return
        self.ded_vars["ded_tax"].set(str(sal.get("income_tax", 0)))
        self.ded_vars["ded_loan"].set(str(sal.get("loan", 0)))
        self.ded_vars["ded_advance"].set(str(sal.get("advance", 0)))
        self.ded_name_lbl.config(text=emp["name"])
        self.ded_gross_lbl.config(text=f"Gross  ₹{sal['gross']:,}")
        self.ded_net_lbl.config(text=f"Net Pay  ₹{sal['net']:,}")
        self.ded_info_frame.pack(fill="x", pady=(18, 0))

    def _apply_deductions(self):
        self.salaries = load_data(SALARY_FILE)
        eid = self.ded_id_var.get().strip().upper()
        found = False
        for sal in self.salaries:
            if sal["emp_id"] == eid:
                found = True
                try:
                    sal["income_tax"] = int(self.ded_vars["ded_tax"].get())
                    sal["loan"] = int(self.ded_vars["ded_loan"].get())
                    sal["advance"] = int(self.ded_vars["ded_advance"].get())
                    sal["net"] = (
                        sal["gross"]
                        - sal["income_tax"]
                        - sal["pf"]
                        - sal["loan"]
                        - sal["advance"]
                    )
                except ValueError:
                    messagebox.showerror("Invalid", "All values must be integers.")
                    return
                break
        if not found:
            messagebox.showerror("Not Found", "Load an employee first.")
            return
        save_all(SALARY_FILE, self.salaries)
        messagebox.showinfo("Updated", f"✔  Deductions applied for {eid}")
        self._load_deductions()

    def _clear_deductions(self):
        self.ded_id_var.set("")
        for v in self.ded_vars.values():
            v.set("0")
        self.ded_info_frame.pack_forget()


# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = PayrollApp()
    app.mainloop()
