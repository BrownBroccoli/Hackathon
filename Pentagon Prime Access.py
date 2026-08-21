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
left.grid(row=0, column=0,rowspan=2, sticky="nsew")
        padx=(15, 8),pady=15)

left.grid_rowconfigure(0, weight=1)
left.grid_columnconfigure(0, weight=1)

#Treeview ("widget used to display information in rows and columns")
tree = ttk.Treeview




