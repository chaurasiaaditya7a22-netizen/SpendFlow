import json
import os
from datetime import datetime, date

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

DATA_FILE = "expenses.json"


# ---------- Data helpers ---------- #

def load_data():
    """Load expenses + budgets from JSON. Supports old list-only format."""
    if not os.path.exists(DATA_FILE):
        return [], {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return [], {}

    if isinstance(data, list):  # old format
        return data, {}

    expenses = data.get("expenses", [])
    budgets = data.get("budgets", {})
    return expenses, budgets


def save_data(expenses, budgets):
    data = {"expenses": expenses, "budgets": budgets}
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print("Error saving data:", e)


def get_today_str():
    return date.today().strftime("%d-%m-%Y")


def current_month_key():
    return date.today().strftime("%Y-%m")


def month_from_str(dstr):
    dt = datetime.strptime(dstr, "%d-%m-%Y")
    return dt.year, dt.month


# ---------- Splash Screen ---------- #

class SplashScreen(ctk.CTkToplevel):
    def __init__(self, master, bg="#020617", accent="#f97316"):
        super().__init__(master)
        self.master = master
        self.overrideredirect(True)  # borderless
        self.attributes("-topmost", True)

        # size + center
        w, h = 260, 200
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = int((sw - w) / 2)
        y = int((sh - h) / 2.5)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.configure(fg_color=bg)

        title = ctk.CTkLabel(
            self,
            text="Expense Tracker",
            text_color="white",
            font=("Inter", 18, "bold"),
        )
        title.pack(pady=(30, 6))

        subtitle = ctk.CTkLabel(
            self,
            text="Calm • Futuristic • Smart Budget",
            text_color="#9ca3af",
            font=("Inter", 11),
        )
        subtitle.pack(pady=(0, 18))

        self.progress = ctk.CTkProgressBar(
            self,
            fg_color="#020617",
            progress_color=accent,
            height=8,
            corner_radius=100,
        )
        self.progress.pack(fill="x", padx=30)
        self.progress.set(0)

        self.after(30, self.animate)

    def animate(self):
        value = self.progress.get()
        if value >= 1:
            return
        self.progress.set(value + 0.03)
        self.after(35, self.animate)


# ---------- Main App ---------- #

class ExpenseAppCTk:
    # AMOLED palette
    BG = "#020617"          # deep navy/black
    CARD = "#020617"
    CARD_BORDER = "#1e293b"
    CARD_HIGHLIGHT = "#0b1220"
    TEXT_MAIN = "#e5e7eb"
    TEXT_SUB = "#9ca3af"
    ORANGE = "#f97316"
    ORANGE_HOVER = "#fb923c"
    BLUE = "#38bdf8"
    GREEN = "#22c55e"
    RED = "#ef4444"
    YELLOW = "#eab308"

    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("Futuristic Expense Tracker")
        self.root.geometry("400x780")
        self.root.minsize(360, 640)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.root.configure(fg_color=self.BG)

        self.expenses, self.budgets = load_data()

        # Scrollable main area
        self.main = ctk.CTkScrollableFrame(
            master=self.root,
            fg_color=self.BG,
            border_width=0,
        )
        self.main.pack(fill="both", expand=True, padx=12, pady=12)

        self.build_header(self.main)
        self.build_budget_card(self.main)
        self.build_add_expense_card(self.main)
        self.build_history_section(self.main)

        self.refresh_history()
        self.update_budget_status()

    # ---------- UI sections ---------- #

    def build_header(self, parent):
        container = ctk.CTkFrame(parent, fg_color=self.BG, border_width=0)
        container.pack(fill="x", pady=(0, 8))

        title = ctk.CTkLabel(
            container,
            text="Expense Tracker",
            text_color=self.TEXT_MAIN,
            font=("Inter", 20, "bold"),
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            container,
            text="Dark · Futuristic · Mobile-first",
            text_color=self.TEXT_SUB,
            font=("Inter", 11),
        )
        subtitle.pack(anchor="w")

        today = ctk.CTkLabel(
            container,
            text=f"Today • {get_today_str()}",
            text_color=self.TEXT_SUB,
            font=("Inter", 10),
        )
        today.pack(anchor="w", pady=(4, 0))

    def build_budget_card(self, parent):
        month_text = date.today().strftime("%B %Y")

        self.budget_card = ctk.CTkFrame(
            parent,
            fg_color=self.CARD,
            border_width=1,
            border_color=self.CARD_BORDER,
            corner_radius=18,
        )
        self.budget_card.pack(fill="x", pady=(4, 8))

        # fake glass top highlight line
        top_glass = ctk.CTkFrame(
            self.budget_card,
            fg_color=self.CARD_HIGHLIGHT,
            height=2,
            corner_radius=18,
        )
        top_glass.pack(fill="x", side="top")

        header_row = ctk.CTkFrame(self.budget_card, fg_color="transparent")
        header_row.pack(fill="x", padx=12, pady=(8, 4))

        title = ctk.CTkLabel(
            header_row,
            text=f"Monthly Budget · {month_text}",
            text_color=self.TEXT_MAIN,
            font=("Inter", 14, "bold"),
        )
        title.pack(side="left", anchor="w")

        input_row = ctk.CTkFrame(self.budget_card, fg_color="transparent")
        input_row.pack(fill="x", padx=12, pady=(0, 4))

        col_left = ctk.CTkFrame(input_row, fg_color="transparent")
        col_left.pack(side="left", fill="x", expand=True)

        lbl = ctk.CTkLabel(
            col_left,
            text="Budget (₹)",
            text_color=self.TEXT_SUB,
            font=("Inter", 11),
        )
        lbl.pack(anchor="w")

        self.budget_var = ctk.StringVar()
        mkey = current_month_key()
        if mkey in self.budgets:
            self.budget_var.set(str(self.budgets[mkey]))

        entry = ctk.CTkEntry(
            col_left,
            textvariable=self.budget_var,
            fg_color="#020617",
            text_color=self.TEXT_MAIN,
            border_color=self.CARD_BORDER,
            border_width=1,
            corner_radius=10,
            font=("Inter", 12),
        )
        entry.pack(fill="x", pady=(2, 4), ipady=4)

        btn_save = ctk.CTkButton(
            input_row,
            text="Save",
            command=self.on_set_budget,
            fg_color=self.ORANGE,
            hover_color=self.ORANGE_HOVER,
            text_color="white",
            font=("Inter", 11, "bold"),
            corner_radius=40,
            height=36,
            width=80,
        )
        btn_save.pack(side="right", pady=(18, 4))

        self.budget_status_label = ctk.CTkLabel(
            self.budget_card,
            text="",
            text_color=self.TEXT_SUB,
            font=("Inter", 11, "bold"),
            wraplength=340,
            justify="left",
        )
        self.budget_status_label.pack(anchor="w", padx=12, pady=(4, 2))

        self.advice_label = ctk.CTkLabel(
            self.budget_card,
            text="Set a monthly budget to get smart advice on controlling expenses.",
            text_color=self.TEXT_SUB,
            font=("Inter", 10),
            wraplength=340,
            justify="left",
        )
        self.advice_label.pack(anchor="w", padx=12, pady=(0, 10))

        btn_summary = ctk.CTkButton(
            self.budget_card,
            text="This Month Summary",
            command=self.on_show_month_summary,
            fg_color=self.BLUE,
            hover_color="#38bdf8",
            text_color="white",
            font=("Inter", 11, "bold"),
            corner_radius=40,
            height=38,
        )
        btn_summary.pack(fill="x", padx=12, pady=(0, 10))

    def build_add_expense_card(self, parent):
        self.add_card = ctk.CTkFrame(
            parent,
            fg_color=self.CARD,
            border_width=1,
            border_color=self.CARD_BORDER,
            corner_radius=18,
        )
        self.add_card.pack(fill="x", pady=(0, 8))

        top_glass = ctk.CTkFrame(
            self.add_card,
            fg_color=self.CARD_HIGHLIGHT,
            height=2,
            corner_radius=18,
        )
        top_glass.pack(fill="x", side="top")

        title = ctk.CTkLabel(
            self.add_card,
            text="Add Expense",
            text_color=self.TEXT_MAIN,
            font=("Inter", 14, "bold"),
        )
        title.pack(anchor="w", padx=12, pady=(10, 0))

        desc = ctk.CTkLabel(
            self.add_card,
            text="Track every spend with category, note and date.",
            text_color=self.TEXT_SUB,
            font=("Inter", 10),
            wraplength=340,
            justify="left",
        )
        desc.pack(anchor="w", padx=12, pady=(0, 8))

        self.amount_var = ctk.StringVar()
        self.category_var = ctk.StringVar(value="Food")
        self.note_var = ctk.StringVar()
        self.date_var = ctk.StringVar(value=get_today_str())

        self._build_labeled_entry(self.add_card, "Amount (₹)", self.amount_var)
        self._build_labeled_entry(self.add_card, "Category", self.category_var)
        self._build_labeled_entry(self.add_card, "Note (optional)", self.note_var)
        self._build_labeled_entry(self.add_card, "Date (DD-MM-YYYY)", self.date_var)

        btn_add = ctk.CTkButton(
            self.add_card,
            text="Add Expense",
            command=self.on_add_expense,
            fg_color=self.ORANGE,
            hover_color=self.ORANGE_HOVER,
            text_color="white",
            font=("Inter", 12, "bold"),
            corner_radius=40,
            height=42,
        )
        btn_add.pack(fill="x", padx=12, pady=(8, 6))

        btn_delete = ctk.CTkButton(
            self.add_card,
            text="Delete Last Expense",
            command=self.on_delete_last,
            fg_color="#020617",
            hover_color="#020617",
            text_color=self.TEXT_SUB,
            border_width=1,
            border_color=self.CARD_BORDER,
            font=("Inter", 11, "bold"),
            corner_radius=40,
            height=36,
        )
        btn_delete.pack(fill="x", padx=12, pady=(0, 12))

    def _build_labeled_entry(self, parent, label_text, var):
        wrapper = ctk.CTkFrame(parent, fg_color="transparent")
        wrapper.pack(fill="x", padx=12, pady=(4, 2))

        label = ctk.CTkLabel(
            wrapper,
            text=label_text,
            text_color=self.TEXT_SUB,
            font=("Inter", 10),
        )
        label.pack(anchor="w")

        entry = ctk.CTkEntry(
            wrapper,
            textvariable=var,
            fg_color="#020617",
            text_color=self.TEXT_MAIN,
            border_color=self.CARD_BORDER,
            border_width=1,
            corner_radius=10,
            font=("Inter", 12),
        )
        entry.pack(fill="x", pady=(2, 0), ipady=4)

    def build_history_section(self, parent):
        self.history_card = ctk.CTkFrame(
            parent,
            fg_color=self.CARD,
            border_width=1,
            border_color=self.CARD_BORDER,
            corner_radius=18,
        )
        self.history_card.pack(fill="both", expand=True, pady=(0, 8))

        top_glass = ctk.CTkFrame(
            self.history_card,
            fg_color=self.CARD_HIGHLIGHT,
            height=2,
            corner_radius=18,
        )
        top_glass.pack(fill="x", side="top")

        header = ctk.CTkFrame(self.history_card, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(10, 4))

        title = ctk.CTkLabel(
            header,
            text="History",
            text_color=self.TEXT_MAIN,
            font=("Inter", 14, "bold"),
        )
        title.pack(side="left")

        self.total_label = ctk.CTkLabel(
            header,
            text="Total: ₹0.00",
            text_color=self.TEXT_SUB,
            font=("Inter", 10, "bold"),
        )
        self.total_label.pack(side="right")

        # list container
        self.history_list = ctk.CTkFrame(self.history_card, fg_color="transparent")
        self.history_list.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        hint_row = ctk.CTkFrame(self.history_card, fg_color="transparent")
        hint_row.pack(fill="x", padx=12, pady=(0, 10))

        hint = ctk.CTkLabel(
            hint_row,
            text="Newest expenses appear at the top.",
            text_color=self.TEXT_SUB,
            font=("Inter", 9),
        )
        hint.pack(side="left", anchor="w")

        stats_btn = ctk.CTkButton(
            hint_row,
            text="View Stats",
            command=self.open_stats_window,
            fg_color="#020617",
            hover_color="#020617",
            border_width=1,
            border_color=self.CARD_BORDER,
            text_color=self.BLUE,
            font=("Inter", 10, "bold"),
            corner_radius=40,
            height=30,
            width=100,
        )
        stats_btn.pack(side="right")

    # ---------- Actions ---------- #

    def on_set_budget(self):
        text = self.budget_var.get().strip()
        if not text:
            messagebox.showwarning("Budget", "Please enter an amount for budget.")
            return
        try:
            value = float(text)
            if value <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Budget", "Enter a valid positive number.")
            return

        mkey = current_month_key()
        self.budgets[mkey] = value
        save_data(self.expenses, self.budgets)
        self.update_budget_status()
        messagebox.showinfo("Budget", "Monthly budget saved.")

    def on_add_expense(self):
        amount_str = self.amount_var.get().strip()
        category = self.category_var.get().strip() or "Other"
        note = self.note_var.get().strip()
        date_str = self.date_var.get().strip()

        if not amount_str:
            messagebox.showwarning("Missing amount", "Please enter an amount.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid", "Please enter a valid amount.")
            return

        if not date_str:
            date_str = get_today_str()

        try:
            datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            messagebox.showerror(
                "Invalid date",
                "Use DD-MM-YYYY format (e.g. 28-11-2025).",
            )
            return

        expense = {
            "amount": amount,
            "category": category,
            "note": note,
            "date": date_str,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.expenses.append(expense)
        save_data(self.expenses, self.budgets)

        self.amount_var.set("")
        self.note_var.set("")
        self.date_var.set(get_today_str())

        self.refresh_history()
        self.update_budget_status()
        messagebox.showinfo("Added", "Expense added successfully.")

    def on_delete_last(self):
        if not self.expenses:
            messagebox.showinfo("Delete", "No expenses to delete.")
            return

        last = self.expenses[-1]
        text = (
            "Delete last expense?\n\n"
            f"Date: {last.get('date')}\n"
            f"Amount: ₹{last.get('amount'):.2f}\n"
            f"Category: {last.get('category')}\n"
            f"Note: {last.get('note') or '-'}"
        )
        if messagebox.askyesno("Confirm", text):
            self.expenses.pop()
            save_data(self.expenses, self.budgets)
            self.refresh_history()
            self.update_budget_status()
            messagebox.showinfo("Deleted", "Last expense deleted.")

    def on_show_month_summary(self):
        month_name = date.today().strftime("%B %Y")
        spent, cat_totals = self.current_month_totals()
        budget = self.budgets.get(current_month_key())

        if budget is None:
            msg = (
                f"Total spent in {month_name}: ₹{spent:.2f}\n\n"
                f"No budget set for this month yet."
            )
            messagebox.showinfo("Summary", msg)
            return

        diff = budget - spent
        if abs(diff) < 0.01:
            status = "You are exactly on your budget this month."
        elif diff > 0:
            status = f"Good job! You are under budget by ₹{diff:.2f}."
        else:
            status = f"You overspent this month by ₹{abs(diff):.2f}."

        advice = self.build_advice(diff, cat_totals)

        msg = (
            f"Budget for {month_name}: ₹{budget:.2f}\n"
            f"Spent: ₹{spent:.2f}\n\n"
            f"{status}\n\n"
            f"Advice: {advice}"
        )
        messagebox.showinfo("Month Summary", msg)

    # ---------- Budget helpers ---------- #

    def current_month_totals(self):
        today = date.today()
        y, m = today.year, today.month
        total = 0.0
        per_cat = {}
        for exp in self.expenses:
            try:
                ey, em = month_from_str(exp.get("date", "01-01-2000"))
            except Exception:
                continue
            if ey == y and em == m:
                amt = float(exp.get("amount", 0))
                total += amt
                cat = exp.get("category", "Other")
                per_cat[cat] = per_cat.get(cat, 0) + amt
        return total, per_cat

    def build_advice(self, diff, cat_totals):
        if not cat_totals:
            return "Start logging your expenses so I can analyse where money goes."

        top_cat = max(cat_totals, key=lambda c: cat_totals[c])
        top_val = cat_totals[top_cat]

        if diff < 0:
            return (
                f"Most of your spending is on '{top_cat}' (₹{top_val:.0f}). "
                f"Cut that category first or find cheaper alternatives."
            )
        elif abs(diff) < 0.01:
            return (
                f"You're perfectly on budget. Still, keep an eye on '{top_cat}', "
                f"as it's your highest expense category."
            )
        else:
            return (
                f"Nice! You're under budget. Your biggest spending is '{top_cat}' "
                f"(₹{top_val:.0f}). If you control this, you'll save even more."
            )

    def update_budget_status(self):
        month_name = date.today().strftime("%B %Y")
        spent, cat_totals = self.current_month_totals()
        budget = self.budgets.get(current_month_key())

        if budget is None:
            text = f"No budget set for {month_name}."
            self.budget_status_label.configure(text=text, text_color=self.TEXT_SUB)
            self.advice_label.configure(
                text="Set a budget and add some expenses. I'll tell you where to cut costs."
            )
            return

        diff = budget - spent
        if abs(diff) < 0.01:
            color = self.YELLOW
            text = f"{month_name}: On budget (₹{budget:.2f})."
        elif diff > 0:
            color = self.GREEN
            text = (
                f"{month_name}: Under budget by ₹{diff:.2f} "
                f"(Budget ₹{budget:.2f}, Spent ₹{spent:.2f})."
            )
        else:
            color = self.RED
            text = (
                f"{month_name}: Over budget by ₹{abs(diff):.2f} "
                f"(Budget ₹{budget:.2f}, Spent ₹{spent:.2f})."
            )

        self.budget_status_label.configure(text=text, text_color=color)
        advice = self.build_advice(diff, cat_totals)
        self.advice_label.configure(text=advice)

    # ---------- History rendering ---------- #

    def refresh_history(self):
        for child in self.history_list.winfo_children():
            child.destroy()

        total = 0.0
        for exp in reversed(self.expenses):
            total += float(exp.get("amount", 0))
            self._add_history_card(exp)

        self.total_label.configure(text=f"Total: ₹{total:.2f}")

    def _category_color(self, cat):
        c = cat.lower()
        if "food" in c:
            return "#4ade80"  # green
        if "travel" in c or "fuel" in c:
            return "#38bdf8"  # blue
        if "bill" in c or "rent" in c:
            return "#eab308"  # yellow
        if "entertain" in c or "party" in c:
            return "#a855f7"  # purple
        if "shop" in c:
            return "#f97316"  # orange
        return self.BLUE

    def _add_history_card(self, exp):
        card = ctk.CTkFrame(
            self.history_list,
            fg_color="#020617",
            border_width=1,
            border_color=self.CARD_BORDER,
            corner_radius=14,
        )
        card.pack(fill="x", pady=4)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=8, pady=(4, 0))

        lbl_date = ctk.CTkLabel(
            top_row,
            text=exp.get("date", ""),
            text_color=self.TEXT_SUB,
            font=("Inter", 9),
        )
        lbl_date.pack(side="left")

        lbl_amount = ctk.CTkLabel(
            top_row,
            text=f"₹{float(exp.get('amount', 0)):.2f}",
            text_color=self.ORANGE,
            font=("Inter", 11, "bold"),
        )
        lbl_amount.pack(side="right")

        mid_row = ctk.CTkFrame(card, fg_color="transparent")
        mid_row.pack(fill="x", padx=8, pady=(2, 0))

        cat_color = self._category_color(exp.get("category", "Other"))
        lbl_cat = ctk.CTkLabel(
            mid_row,
            text=exp.get("category", "Other"),
            text_color=cat_color,
            font=("Inter", 10, "bold"),
        )
        lbl_cat.pack(anchor="w")

        note_text = exp.get("note") or ""
        if note_text:
            lbl_note = ctk.CTkLabel(
                card,
                text=note_text,
                text_color=self.TEXT_MAIN,
                font=("Inter", 10),
                wraplength=330,
                justify="left",
            )
            lbl_note.pack(anchor="w", padx=8, pady=(0, 6))

    # ---------- Stats window (graphs) ---------- #

    def open_stats_window(self):
        spent, per_cat = self.current_month_totals()
        month_name = date.today().strftime("%B %Y")

        # FULLSCREEN WINDOW (mobile style)
        win = ctk.CTkToplevel(self.root)
        win.title("Spending Stats")
        win.attributes("-fullscreen", True)
        win.configure(fg_color=self.BG)
        win.grab_set()

        # Header
        header = ctk.CTkFrame(win, fg_color=self.BG)
        header.pack(fill="x", padx=16, pady=(16, 8))

        close_btn = ctk.CTkButton(
            header,
            text="← Back",
            command=win.destroy,
            fg_color="#020617",
            hover_color="#0f172a",
            text_color=self.TEXT_MAIN,
            corner_radius=40,
            height=40,
            width=90
        )
        close_btn.pack(side="left")

        title = ctk.CTkLabel(
            header,
            text=f"Stats · {month_name}",
            text_color=self.TEXT_MAIN,
            font=("Inter", 20, "bold")
        )
        title.pack(side="left", padx=16)

        # Scrollable content
        body = ctk.CTkScrollableFrame(
            win,
            fg_color=self.BG,
            width=380,
            height=700
        )
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        subtitle = ctk.CTkLabel(
            body,
            text="Category-wise breakdown for this month",
            text_color=self.TEXT_SUB,
            font=("Inter", 12)
        )
        subtitle.pack(anchor="w", padx=10, pady=(4, 12))

        if not per_cat:
            msg = ctk.CTkLabel(
                body,
                text="No expenses for this month yet.",
                text_color=self.TEXT_SUB,
                font=("Inter", 13),
            )
            msg.pack(pady=40)
            return

        # Large graph card
        chart_card = ctk.CTkFrame(
            body,
            fg_color="#020617",
            border_width=1,
            border_color=self.CARD_BORDER,
            corner_radius=18
        )
        chart_card.pack(fill="x", padx=10, pady=(0, 14))

        canvas_h = 320
        canvas = tk.Canvas(
            chart_card,
            bg=self.BG,
            highlightthickness=0,
            height=canvas_h
        )
        canvas.pack(fill="x", padx=10, pady=10)

        # Prepare graph data
        categories = list(per_cat.keys())
        values = [per_cat[c] for c in categories]
        max_val = max(values)

        # Graph layout (mobile optimized)
        left_margin = 50
        right_margin = 20
        bottom = canvas_h - 40
        top = 40

        usable_width = 340
        num = len(categories)
        bar_space = usable_width / max(num, 1)
        bar_width = bar_space * 0.45

        # X-axis
        canvas.create_line(
            left_margin,
            bottom,
            left_margin + usable_width,
            bottom,
            fill="#1f2937",
            width=2
        )

        # Draw bars
        for i, cat in enumerate(categories):
            value = values[i]
            height_ratio = value / max_val if max_val else 0

            x_center = left_margin + bar_space * (i + 0.5)
            bar_height = (bottom - top) * height_ratio

            x0 = x_center - bar_width / 2
            x1 = x_center + bar_width / 2
            y1 = bottom
            y0 = bottom - bar_height

            color = self._category_color(cat)

            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=color)

            # Amount on top of bar
            canvas.create_text(
                x_center,
                y0 - 10,
                text=f"₹{value:.0f}",
                fill=self.TEXT_MAIN,
                font=("Inter", 10)
            )

            # Category name below bar
            canvas.create_text(
                x_center,
                bottom + 14,
                text=cat,
                fill=self.TEXT_SUB,
                font=("Inter", 10),
                anchor="n"
            )

        # Total display
        total_label = ctk.CTkLabel(
            chart_card,
            text=f"Total spent this month: ₹{spent:.2f}",
            text_color=self.TEXT_MAIN,
            font=("Inter", 13, "bold")
        )
        total_label.pack(anchor="w", padx=12, pady=(8, 4))

        # Category totals list
        for cat in categories:
            val = per_cat[cat]
            line = ctk.CTkLabel(
                chart_card,
                text=f"{cat}: ₹{val:.2f}",
                text_color=self.TEXT_SUB,
                font=("Inter", 12)
            )
            line.pack(anchor="w", padx=12, pady=(0, 2))


# ---------- main ---------- #

def main():
    root = ctk.CTk()
    root.withdraw()  # hide main while splash shows

    splash = SplashScreen(root)
    # show main app after ~1.5s
    def start_app():
        splash.destroy()
        root.deiconify()
        ExpenseAppCTk(root)

    root.after(1600, start_app)
    root.mainloop()


if __name__ == "__main__":
    main()