import tkinter as tk
from tkinter import ttk
from datetime import datetime

# ================= WINDOW =================
root = tk.Tk()
root.title("Pentagon Prime Email Management System")
root.geometry("1200x700")
root.configure(bg="#172033")

# Make window resize
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# ================= LEFT SIDE =================
left = tk.Frame(root, bg="#172033", bd=2, relief="groove")
left.grid(row=0, column=0, rowspan=2, sticky="nsew",
          padx=(15, 8), pady=15)

left.grid_rowconfigure(0, weight=1)
left.grid_columnconfigure(0, weight=1)

# Treeview
tree = ttk.Treeview(
    left,
    columns=("Email", "Person", "Category", "Subject", "Date"),
    show="headings"
)

for col in ("Email", "Person", "Category", "Subject", "Date"):
    tree.heading(col, text=col)

tree.column("Email", width=150)
tree.column("Person", width=100)
tree.column("Category", width=100)
tree.column("Subject", width=150)
tree.column("Date", width=100)

tree.grid(row=0, column=0, sticky="nsew")

# Scrollbar
scroll = ttk.Scrollbar(left, orient="vertical", command=tree.yview)
scroll.grid(row=0, column=1, sticky="ns")
tree.configure(yscrollcommand=scroll.set)

# ================= SAMPLE DATA =================
emails = [
    ("phakeme@gmail.com", "Phakeme", "Data", "Database Assignment", "2026-08-20"),
    ("mary@gmail.com", "Mary", "Person", "Meeting Request", "2026-08-20"),
    ("finance@gmail.com", "Finance", "Financial", "Monthly Report", "2026-08-19"),
    ("social@gmail.com", "Social Media", "Social", "New Message", "2026-08-18"),
    ("promo@gmail.com", "Company", "Promotion", "Special Offer", "2026-08-17")
]

for email in emails:
    tree.insert("", "end", values=email)

# ================= RIGHT SIDE =================
right = tk.Frame(root, bg="#172033")
right.grid(row=0, column=1, sticky="nsew",
           padx=(8, 15), pady=15)

right.grid_columnconfigure(0, weight=1)
right.grid_rowconfigure(1, weight=1)

# Input
input_frame = tk.Frame(right, bg="#172033")
input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
input_frame.grid_columnconfigure(0, weight=1)

input_box = tk.Entry(input_frame, font=("Arial", 12))
input_box.grid(row=0, column=0, sticky="ew", ipady=12, padx=(0, 10))
input_box.insert(0, "Input / Interact with Chat Bot")

# Search / Run
def search_run():
    question = input_box.get()
    output.insert("end", f"You: {question}\n")
    output.insert("end", "Bot: Request received.\n\n")
    output.see("end")

search = ttk.Button(
    input_frame,
    text="Search / Run",
    command=search_run
)
search.grid(row=0, column=1, ipadx=10, ipady=5)

# ================= CHAT BOT OUTPUT =================
output_frame = tk.Frame(right, bd=2, relief="groove")
output_frame.grid(row=1, column=0, sticky="nsew")

output_frame.grid_rowconfigure(0, weight=1)
output_frame.grid_columnconfigure(0, weight=1)

output = tk.Text(
    output_frame,
    wrap="word",
    font=("Arial", 11)
)
output.grid(row=0, column=0, sticky="nsew")

output_scroll = ttk.Scrollbar(
    output_frame,
    orient="vertical",
    command=output.yview
)
output_scroll.grid(row=0, column=1, sticky="ns")
output.configure(yscrollcommand=output_scroll.set)

output.insert("end", "Chat Bot Output\n\n")

# ================= BOTTOM =================
bottom = tk.Frame(root, bg="#172033")
bottom.grid(row=1, column=1, sticky="ew",
            padx=(8, 15), pady=(0, 15))

# Run / Date
def run_date():
    output.insert(
        "end",
        f"Run Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    )

run_button = ttk.Button(
    bottom,
    text="Run / Date",
    command=run_date
)
run_button.grid(row=0, column=0, padx=(0, 15), ipady=5)

# Combo Box
categories = ["Data", "Person", "Financial", "Social", "Promotion"]

combo = ttk.Combobox(
    bottom,
    values=categories,
    state="readonly"
)
combo.set("Select Category")
combo.grid(row=0, column=1, sticky="ew", ipady=5)

bottom.grid_columnconfigure(1, weight=1)

# ================= SELECT EMAIL =================
def selected_email(event):
    selected = tree.selection()

    if selected:
        values = tree.item(selected[0])["values"]

        output.insert(
            "end",
            f"\nSelected Email\n"
            f"Email: {values[0]}\n"
            f"Person: {values[1]}\n"
            f"Category: {values[2]}\n"
            f"Subject: {values[3]}\n"
            f"Date: {values[4]}\n\n"
        )

tree.bind("<<TreeviewSelect>>", selected_email)

root.mainloop()