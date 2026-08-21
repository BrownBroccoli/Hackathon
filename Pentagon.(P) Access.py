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
left = tk.Frame(
    root,
    bg="#172033",
    bd=2,
    relief="groove"
)

left.grid(
    row=0,
    column=0,
    rowspan=2,
    sticky="nsew",
    padx=(15, 8),
    pady=15
)

left.grid_rowconfigure(0, weight=1)
left.grid_columnconfigure(0, weight=1)

# ================= TREEVIEW =================
tree = ttk.Treeview(
    left,
    columns=("Email", "Person", "Category", "Subject", "Date"),
    show="headings"
)

# Headings
tree.heading("Email", text="Email")
tree.heading("Person", text="Person")
tree.heading("Category", text="Category")
tree.heading("Subject", text="Subject")
tree.heading("Date", text="Date")

# Column sizes
tree.column("Email", width=150)
tree.column("Person", width=100)
tree.column("Category", width=100)
tree.column("Subject", width=150)
tree.column("Date", width=100)

tree.grid(
    row=0,
    column=0,
    sticky="nsew"
)

# ================= TREEVIEW SCROLLBAR =================
scroll = ttk.Scrollbar(
    left,
    orient="vertical",
    command=tree.yview
)

scroll.grid(
    row=0,
    column=1,
    sticky="ns"
)

tree.configure(
    yscrollcommand=scroll.set
)

# ================= SAMPLE DATA =================
emails = [
    (
        "phakeme@gmail.com",
        "Phakeme",
        "Data",
        "Database Assignment",
        "2026-08-20"
    ),
    (
        "mary@gmail.com",
        "Mary",
        "Person",
        "Meeting Request",
        "2026-08-20"
    ),
    (
        "finance@gmail.com",
        "Finance",
        "Financial",
        "Monthly Report",
        "2026-08-19"
    ),
    (
        "social@gmail.com",
        "Social Media",
        "Social",
        "New Message",
        "2026-08-18"
    ),
    (
        "promo@gmail.com",
        "Company",
        "Promotion",
        "Special Offer",
        "2026-08-17"
    )
]

# Insert data into Treeview
for email in emails:
    tree.insert(
        "",
        "end",
        values=email
    )

# ================= RIGHT SIDE =================
right = tk.Frame(
    root,
    bg="#172033"
)

right.grid(
    row=0,
    column=1,
    sticky="nsew",
    padx=(8, 15),
    pady=15
)

right.grid_columnconfigure(0, weight=1)
right.grid_rowconfigure(1, weight=1)

# ================= INPUT FRAME =================
input_frame = tk.Frame(
    right,
    bg="#172033"
)

input_frame.grid(
    row=0,
    column=0,
    sticky="ew",
    pady=(0, 10)
)

input_frame.grid_columnconfigure(0, weight=1)

# ================= INPUT TITLE =================
input_title = tk.Label(
    input_frame,
    text="Input / Interact with Chat Bot",
    bg="#172033",
    fg="white",
    font=("Arial", 12, "bold", "underline")
)

input_title.grid(
    row=0,
    column=0,
    sticky="w",
    pady=(0, 5)
)

# ================= INPUT BOX =================
input_box = tk.Entry(
    input_frame,
    font=("Arial", 12),
    bg="white",
    fg="black"
)

# IMPORTANT:
# The input box is intentionally empty.
input_box.grid(
    row=1,
    column=0,
    sticky="ew",
    ipady=12,
    padx=(0, 10)
)

# ================= CHAT BOT OUTPUT =================
output_frame = tk.Frame(
    right,
    bg="#172033",
    bd=2,
    relief="groove"
)

output_frame.grid(
    row=1,
    column=0,
    sticky="nsew"
)

output_frame.grid_rowconfigure(0, weight=1)
output_frame.grid_columnconfigure(0, weight=1)

# ================= OUTPUT BOX =================
output = tk.Text(
    output_frame,
    wrap="word",
    font=("Arial", 11),
    bg="white",
    fg="black"
)

output.grid(
    row=0,
    column=0,
    sticky="nsew"
)

# ================= OUTPUT SCROLLBAR =================
output_scroll = ttk.Scrollbar(
    output_frame,
    orient="vertical",
    command=output.yview
)

output_scroll.grid(
    row=0,
    column=1,
    sticky="ns"
)

output.configure(
    yscrollcommand=output_scroll.set
)

# ================= SELECTED EMAIL STYLE =================
output.tag_configure(
    "selected",
    background="#172033",
    foreground="white",
    font=("Arial", 11, "bold")
)

# ================= SEARCH / RUN FUNCTION =================
def search_run():

    question = input_box.get()

    # Only run if the user typed something
    if question.strip() != "":

        output.insert(
            "end",
            f"You: {question}\n"
        )

        output.insert(
            "end",
            "Bot: Request received.\n\n"
        )

        output.see("end")

# ================= SEARCH / RUN BUTTON =================
search = tk.Button(
    input_frame,
    text="Search / Run",
    command=search_run,

    # Button colours
    bg="#16823B",
    fg="white",

    # Colour when mouse is over/clicking
    activebackground="#0F5F2B",
    activeforeground="white",

    # Make the writing visible
    font=("Arial", 10, "bold"),

    # Button appearance
    relief="raised",
    bd=2,

    # Remove default small padding
    padx=10,
    pady=5
)

search.grid(
    row=1,
    column=1,
    ipadx=10,
    ipady=5
)

# ================= BOTTOM =================
bottom = tk.Frame(
    root,
    bg="#172033"
)

bottom.grid(
    row=1,
    column=1,
    sticky="ew",
    padx=(8, 15),
    pady=(0, 15)
)

# ================= RUN / DATE FUNCTION =================
def run_date():

    output.insert(
        "end",
        f"Run Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    )

    output.see("end")

# ================= RUN / DATE BUTTON =================
run_button = tk.Button(
    bottom,
    text="Run / Date",
    command=run_date,

    # Green background
    bg="#16823B",

    # White writing
    fg="white",

    # Active colours
    activebackground="#0F5F2B",
    activeforeground="white",

    # Bold writing
    font=("Arial", 10, "bold"),

    # Button appearance
    relief="raised",
    bd=2,

    padx=10,
    pady=5
)

run_button.grid(
    row=0,
    column=0,
    padx=(0, 15),
    ipadx=10,
    ipady=5
)

# ================= CATEGORY COMBO BOX =================
categories = [
    "Data",
    "Person",
    "Financial",
    "Social",
    "Promotion"
]

combo = ttk.Combobox(
    bottom,
    values=categories,
    state="readonly"
)

combo.set("Select Category")

combo.grid(
    row=0,
    column=1,
    sticky="ew",
    ipady=5
)

bottom.grid_columnconfigure(
    1,
    weight=1
)

# ================= SELECT EMAIL =================
def selected_email(event):

    selected = tree.selection()

    if selected:

        values = tree.item(
            selected[0]
        )["values"]

        # Space before selected email
        output.insert(
            "end",
            "\n"
        )

        # Navy background + white bold text
        output.insert(
            "end",
            "Selected Email\n",
            "selected"
        )

        output.insert(
            "end",
            f"Email: {values[0]}\n"
            f"Person: {values[1]}\n"
            f"Category: {values[2]}\n"
            f"Subject: {values[3]}\n"
            f"Date: {values[4]}\n\n",
            "selected"
        )

        output.see("end")

# Detect when an email is selected
tree.bind(
    "<<TreeviewSelect>>",
    selected_email
)

# ================= START PROGRAM =================
root.mainloop()