import tkinter as tk
from tkinter import ttk
from datetime  import datetime

#==================WINDOW=========================
root  = tk.Tk()
root.title("Pentagon Prime Access")
root.geometry("1200x700")
root.configure(bg ="#071A44") # background color

# Now we are the resize of our Window
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

#==================LEFT SIDE OF OUR WINDOW==========
left =tk.Frame(root, bg="#172033", bd=2, relief="groove")
left.grid(row=0, column=0,rowspan=2, sticky="nsew",padx=(15, 8),pady=15)

left.grid_rowconfigure(0, weight=1)
left.grid_columnconfigure(0, weight=1)

#Treeview ("widget used to display information in rows and columns")
tree = ttk.Treeview


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
input_box.grid(row=0, column=1, sticky="ew", ipadx=12, ipady=10)
input_box.insert(0,"input/ Intact with bot") # This is our input box top(right)

#Search/Run
def search_run():
    Email = input_box.get()
    output.insert("end", f"you: {Email}\n")











