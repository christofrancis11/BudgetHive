import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import csv
from datetime import datetime, timedelta
from tkcalendar import Calendar


class BudgetTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Tracker")

        self.expenses = []
        self.incomes = []
        self.reminders = []

        self.remaining_balance = 0.0
        self.saving_goal = 0.0
        self.budget_goal = 0.0
        self.monthly_salary = 0.0

        self.currency_var = tk.StringVar(value="₹")
        self.currency_options = ["₹", "$", "€", "£", "JPY"]

        self.remaining_balance_var = tk.StringVar()
        self.saving_goal_var = tk.StringVar()
        self.budget_goal_var = tk.StringVar()

        # Layout configuration
        self.root.rowconfigure(7, weight=1)
        self.root.columnconfigure((0, 1), weight=1)

        # ----- EXPENSES FRAME -----
        self.expenses_frame = ttk.LabelFrame(root, text="Expenses")
        self.expenses_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.create_expenses_widgets()

        # ----- INCOME FRAME -----
        self.income_frame = ttk.LabelFrame(root, text="Income")
        self.income_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.create_income_widgets()

        # ----- CURRENCY -----
        self.currency_label = ttk.Label(root, text="Currency:")
        self.currency_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.currency_combobox = ttk.Combobox(
            root, textvariable=self.currency_var, values=self.currency_options, state="readonly"
        )
        self.currency_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.currency_combobox.bind("<<ComboboxSelected>>", self.update_currency)

        # ----- REMAINING BALANCE -----
        self.remaining_balance_label = ttk.Label(root, text="Remaining Balance:")
        self.remaining_balance_label.grid(row=2, column=0, padx=5, pady=5)
        self.remaining_balance_entry = ttk.Entry(
            root, textvariable=self.remaining_balance_var, state="readonly"
        )
        self.remaining_balance_entry.grid(row=2, column=1, padx=5, pady=5)

        # ----- GOAL BUTTONS -----
        self.saving_goal_button = ttk.Button(
            root, text="Set Saving Goal", command=self.setup_saving_goal
        )
        self.saving_goal_button.grid(row=3, column=0, padx=5, pady=5)

        self.budget_goal_button = ttk.Button(
            root, text="Set Budget Goal", command=self.setup_budget_goal
        )
        self.budget_goal_button.grid(row=3, column=1, padx=5, pady=5)

        # ----- REMINDER BUTTON -----
        self.reminder_button = ttk.Button(root, text="Set Reminder", command=self.set_reminder)
        self.reminder_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="we")

        # ----- GOAL DISPLAY -----
        self.saving_goal_label = ttk.Label(root, text="Saving Goal:")
        self.saving_goal_label.grid(row=5, column=0, padx=5, pady=5)
        self.saving_goal_entry = ttk.Entry(
            root, textvariable=self.saving_goal_var, state="readonly"
        )
        self.saving_goal_entry.grid(row=5, column=1, padx=5, pady=5)

        self.budget_goal_label = ttk.Label(root, text="Budget Goal:")
        self.budget_goal_label.grid(row=6, column=0, padx=5, pady=5)
        self.budget_goal_entry = ttk.Entry(
            root, textvariable=self.budget_goal_var, state="readonly"
        )
        self.budget_goal_entry.grid(row=6, column=1, padx=5, pady=5)

        # ----- SUMMARY NOTEBOOK -----
        self.summary_notebook = ttk.Notebook(root)
        self.summary_notebook.grid(
            row=7, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )

        self.expenses_summary_tab = ttk.Frame(self.summary_notebook)
        self.income_summary_tab = ttk.Frame(self.summary_notebook)

        self.summary_notebook.add(self.expenses_summary_tab, text="Expenses Summary")
        self.summary_notebook.add(self.income_summary_tab, text="Income Summary")

        # Create separate Treeviews for expenses and incomes
        self.expenses_tree = self.create_summary_table(
            self.expenses_summary_tab, self.expenses, "lightcoral"
        )
        self.income_tree = self.create_summary_table(
            self.income_summary_tab, self.incomes, "lightgreen"
        )

        # ----- BOTTOM BUTTONS -----
        self.generate_csv_button = ttk.Button(
            root, text="Generate CSV", command=self.generate_csv
        )
        self.generate_csv_button.grid(row=8, column=0, padx=5, pady=5, sticky="we")

        self.finish_button = ttk.Button(root, text="Finish", command=self.finish)
        self.finish_button.grid(row=8, column=1, padx=5, pady=5, sticky="we")

        # Load any saved data first
        self.load_data()
        # Update UI with loaded data
        self.update_remaining_balance()
        self.update_summary_tables()
        self.check_reminders()

    # ------------------------------------------------------------------
    # WIDGET CREATORS
    # ------------------------------------------------------------------
    def create_expenses_widgets(self):
        self.expenses_date_label = ttk.Label(self.expenses_frame, text="Date:")
        self.expenses_date_label.grid(row=0, column=0, padx=5, pady=5)
        self.expenses_date_entry = Calendar(
            self.expenses_frame,
            selectmode="day",
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
        )
        self.expenses_date_entry.grid(row=0, column=1, padx=5, pady=5)

        self.expenses_category_label = ttk.Label(self.expenses_frame, text="Category:")
        self.expenses_category_label.grid(row=1, column=0, padx=5, pady=5)
        self.expenses_category_combobox = ttk.Combobox(
            self.expenses_frame,
            values=["Groceries", "Utilities", "Entertainment", "Others"],
            state="readonly",
        )
        self.expenses_category_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.expenses_category_combobox.current(0)

        self.expenses_description_label = ttk.Label(self.expenses_frame, text="Description:")
        self.expenses_description_label.grid(row=2, column=0, padx=5, pady=5)
        self.expenses_description_entry = ttk.Entry(self.expenses_frame)
        self.expenses_description_entry.grid(row=2, column=1, padx=5, pady=5)

        self.expenses_amount_label = ttk.Label(self.expenses_frame, text="Amount:")
        self.expenses_amount_label.grid(row=3, column=0, padx=5, pady=5)
        self.expenses_amount_entry = ttk.Entry(self.expenses_frame)
        self.expenses_amount_entry.grid(row=3, column=1, padx=5, pady=5)

        self.add_expense_button = ttk.Button(
            self.expenses_frame, text="Add Expense", command=self.add_expense
        )
        self.add_expense_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="we")

    def create_income_widgets(self):
        self.income_date_label = ttk.Label(self.income_frame, text="Date:")
        self.income_date_label.grid(row=0, column=0, padx=5, pady=5)
        self.income_date_entry = Calendar(
            self.income_frame,
            selectmode="day",
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
        )
        self.income_date_entry.grid(row=0, column=1, padx=5, pady=5)

        self.income_category_label = ttk.Label(self.income_frame, text="Category:")
        self.income_category_label.grid(row=1, column=0, padx=5, pady=5)
        self.income_category_combobox = ttk.Combobox(
            self.income_frame, values=["Salary", "Bonus", "Others"], state="readonly"
        )
        self.income_category_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.income_category_combobox.current(0)

        self.income_description_label = ttk.Label(self.income_frame, text="Description:")
        self.income_description_label.grid(row=2, column=0, padx=5, pady=5)
        self.income_description_entry = ttk.Entry(self.income_frame)
        self.income_description_entry.grid(row=2, column=1, padx=5, pady=5)

        self.income_amount_label = ttk.Label(self.income_frame, text="Amount:")
        self.income_amount_label.grid(row=3, column=0, padx=5, pady=5)
        self.income_amount_entry = ttk.Entry(self.income_frame)
        self.income_amount_entry.grid(row=3, column=1, padx=5, pady=5)

        self.add_income_button = ttk.Button(
            self.income_frame, text="Add Income", command=self.add_income
        )
        self.add_income_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="we")

    def create_summary_table(self, parent, data, color):
        if color == "lightcoral":
            tag_color = "#ffb3b3"  # Light red
        elif color == "lightgreen":
            tag_color = "#b3ffb3"  # Light green
        else:
            tag_color = "#ffffff"

        columns = ("Date", "Category", "Description", "Amount")
        tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(expand=True, fill="both")

        tree.tag_configure("colored", background=tag_color)

        for row in data:
            tree.insert("", "end", values=row, tags=("colored",))

        return tree

    # ------------------------------------------------------------------
    # CORE LOGIC
    # ------------------------------------------------------------------
    def add_expense(self):
        date = self.expenses_date_entry.get_date()
        category = self.expenses_category_combobox.get()
        description = self.expenses_description_entry.get()

        try:
            amount = float(self.expenses_amount_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid number for expense amount.")
            return

        self.expenses.append((str(date), category, description, amount))
        self.update_summary_tables()
        self.update_remaining_balance()

        # Clear fields
        self.expenses_description_entry.delete(0, tk.END)
        self.expenses_amount_entry.delete(0, tk.END)

    def add_income(self):
        date = self.income_date_entry.get_date()
        category = self.income_category_combobox.get()
        description = self.income_description_entry.get()

        try:
            amount = float(self.income_amount_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid number for income amount.")
            return

        self.incomes.append((str(date), category, description, amount))
        self.update_summary_tables()
        self.update_remaining_balance()

        # Clear fields
        self.income_description_entry.delete(0, tk.END)
        self.income_amount_entry.delete(0, tk.END)

    def update_currency(self, event):
        # For now, just refresh display values with new currency symbol
        self.saving_goal_var.set(f"{self.currency_var.get()} {self.saving_goal:.2f}")
        self.budget_goal_var.set(f"{self.currency_var.get()} {self.budget_goal:.2f}")
        self.update_remaining_balance()

    def update_summary_tables(self):
        # Clear both trees
        for tree in (self.expenses_tree, self.income_tree):
            for row in tree.get_children():
                tree.delete(row)

        # Refill expenses
        for row in self.expenses:
            self.expenses_tree.insert("", "end", values=row, tags=("colored",))

        # Refill incomes
        for row in self.incomes:
            self.income_tree.insert("", "end", values=row, tags=("colored",))

    def setup_saving_goal(self):
        goal = simpledialog.askfloat("Saving Goal", "Enter your saving goal:")
        if goal is not None:
            self.saving_goal = goal
            self.saving_goal_var.set(f"{self.currency_var.get()} {self.saving_goal:.2f}")

    def setup_budget_goal(self):
        goal = simpledialog.askfloat("Budget Goal", "Enter your budget goal:")
        if goal is not None:
            self.budget_goal = goal
            self.budget_goal_var.set(f"{self.currency_var.get()} {self.budget_goal:.2f}")

    def set_reminder(self):
        reminder_date = simpledialog.askstring("Set Reminder", "Enter reminder date (YYYY-MM-DD):")
        reminder_category = simpledialog.askstring("Set Reminder", "Enter reminder category:")
        reminder_description = simpledialog.askstring("Set Reminder", "Enter reminder description:")
        reminder_amount = simpledialog.askfloat("Set Reminder", "Enter reminder amount:")
        reminder_type = simpledialog.askstring("Set Reminder", "Enter reminder type (Expense/Income):")

        if all([reminder_date, reminder_category, reminder_description, reminder_amount, reminder_type]):
            self.reminders.append(
                {
                    "date": reminder_date,
                    "category": reminder_category,
                    "description": reminder_description,
                    "amount": reminder_amount,
                    "type": reminder_type,
                }
            )
            messagebox.showinfo("Reminder Set", "Reminder has been set successfully!")

    def check_reminders(self):
        today = datetime.today().date()
        for reminder in self.reminders:
            try:
                reminder_date = datetime.strptime(reminder["date"], "%Y-%m-%d").date()
            except ValueError:
                continue
            if reminder_date == today or reminder_date == today + timedelta(days=1):
                messagebox.showinfo(
                    "Reminder",
                    f"Reminder for {reminder_date}: {reminder['description']} "
                    f"({reminder['type']} of {self.currency_var.get()} {reminder['amount']}) "
                    f"in {reminder['category']} category",
                )

    def update_remaining_balance(self):
        total_income = sum(income[3] for income in self.incomes)
        total_expenses = sum(expense[3] for expense in self.expenses)
        self.remaining_balance = total_income - total_expenses
        self.remaining_balance_var.set(
            f"{self.currency_var.get()} {self.remaining_balance:.2f}"
        )

    def generate_csv(self):
        with open("budget_tracker.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Type", "Date", "Category", "Description", "Amount"])
            for expense in self.expenses:
                writer.writerow(["Expense"] + list(expense))
            for income in self.incomes:
                writer.writerow(["Income"] + list(income))

        messagebox.showinfo("CSV Generated", "CSV file has been generated successfully!")

    def finish(self):
        self.root.destroy()

    # ------------------------------------------------------------------
    # DATA PERSISTENCE
    # ------------------------------------------------------------------
    def load_data(self):
        try:
            with open("budget_tracker_data.csv", "r") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row["Type"] == "Expense":
                        self.expenses.append(
                            (
                                row["Date"],
                                row["Category"],
                                row["Description"],
                                float(row["Amount"]),
                            )
                        )
                    elif row["Type"] == "Income":
                        self.incomes.append(
                            (
                                row["Date"],
                                row["Category"],
                                row["Description"],
                                float(row["Amount"]),
                            )
                        )
                    elif row["Type"] == "Reminder":
                        self.reminders.append(
                            {
                                "date": row["Date"],
                                "category": row["Category"],
                                "description": row["Description"],
                                "amount": float(row["Amount"]),
                                "type": "Reminder",
                            }
                        )
        except FileNotFoundError:
            pass

    def save_data(self):
        with open("budget_tracker_data.csv", "w", newline="") as csvfile:
            fieldnames = ["Type", "Date", "Category", "Description", "Amount"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for expense in self.expenses:
                writer.writerow(
                    {
                        "Type": "Expense",
                        "Date": expense[0],
                        "Category": expense[1],
                        "Description": expense[2],
                        "Amount": expense[3],
                    }
                )
            for income in self.incomes:
                writer.writerow(
                    {
                        "Type": "Income",
                        "Date": income[0],
                        "Category": income[1],
                        "Description": income[2],
                        "Amount": income[3],
                    }
                )
            for reminder in self.reminders:
                writer.writerow(
                    {
                        "Type": "Reminder",
                        "Date": reminder["date"],
                        "Category": reminder["category"],
                        "Description": reminder["description"],
                        "Amount": reminder["amount"],
                    }
                )

    def on_close(self):
        self.save_data()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetTrackerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
