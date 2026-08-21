# importing the Tkinter resources(widget) to our page
import tkinter as tk
from tkinter import ttk, messagebox

# ============================================================
# 1. COLOURS
# ============================================================

NAVY = "#071A33"
LIGHT_NAVY = "#0D2A4A"
BLUE = "#1597E5"
GREEN = "#20C997"
WHITE = "#FFFFFF"
LIGHT_GREY = "#D8E3F0"
RED = "#E74C3C"
BLACK = "#000000"

# ============================================================
# 2.creating our window
# ============================================================


# creating a windows so that we can put our widget
root = tk.Tk()

# creating the title of our window
root.title("Pentagon prime")

# making our window to be in a full_screen
root.state("zoomed")

# ==============================================================
# 3. creating our main frame
# ==============================================================

main_frame = tk.Frame(
    root,
    bg=NAVY,
)
main_frame.pack(
    fill="both",
    expand=True
)

# ==============================================================
# 3. creating our intro_frame
# ==============================================================
intro_frame = tk.Frame(
    main_frame,
    bg= LIGHT_NAVY
)
intro_frame.pack(
    fill="both",
    expand=True
)

# ============================================================
# project title inside our introduction_frame
# ============================================================

intro_label =tk.Label(
    intro_frame,
    text = "Pentagon Prime",
    font=("Arial", 28, "bold"),
    bg=LIGHT_NAVY,
    fg=WHITE
)
intro_label.pack(
    padx= 30, # 50
    pady= 50, #30
)

# =============================================================
# creating the description frame
# =============================================================

description_frame = tk.Frame(
    intro_frame,
    bg= LIGHT_NAVY,
    padx= 50,
    pady= 30,
)
description_frame.pack(
    padx= 180,
    pady= 10,
    fill="x"
)
# ===============================================================
# writing the introduction text inside our GUI
# ===============================================================

description_label = tk.Label(
    description_frame,
    text =(
        "Welcome to our Pentagon Prime project. In this project, we are "
        "building software that can help businesses and people solve their "
        "problems more quickly and efficiently. Our software focuses on "
        "working with emails by filtering emails and identifying important "
        "information. It can also create summaries of complicated or "
        "time-consuming emails, making it easier for users to understand "
        "the main points without having to read through a long email.\n\n"

        "We created this software to help people in a business environment, "
        "such as administrators, manage their daily responsibilities and "
        "solve problems more efficiently. The software is designed to provide "
        "useful solutions and help users complete their duties more quickly, "
        "saving valuable time in the workplace. Please note that Pentagon "
        "Prime is still a prototype and some features may still be under "
        "development. To proceed to the system, please press the "
        "\"ACCESS\" button below."
    ),
    font=("Arial", 20),
    bg=LIGHT_NAVY,
    fg=WHITE,
    wraplength=1000,
    justify="left"
)
description_label.pack()

# ================================================
# creating the access button function
# ================================================
def access_system():
    print("Access button clicked")

# =================================================
# creating the button
# =================================================

access_button = tk.Button(
    intro_frame,
    text = "Access",
    command = access_system,
    font=("Arial", 20, "bold"),
    fg=WHITE,# BLACK
    bg= GREEN, # WHITE
    activebackground=LIGHT_GREY,
    activeforeground=BLACK,
    width=13,

    height=3,
    cursor="hand2"
)
access_button.pack(pady = (35,20)) #35,20


root.mainloop()





