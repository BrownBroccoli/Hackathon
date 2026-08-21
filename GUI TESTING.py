# importing the Tkinter resources(widget) to our page
import tkinter as tk
from tkinter import ttk, messagebox


# ============================================================
# 1. COLOURS
# ============================================================

# different that we can use
NAVY = "#071A33"
LIGHT_NAVY = "#0D2A4A"
BLUE = "#1597E5"
GREEN = "#20C997"
WHITE = "#FFFFFF"
LIGHT_GREY = "#D8E3F0"
RED = "#E74C3C"
BLACK = "#000000"


# ============================================================
# 2. CREATING OUR WINDOW
# ============================================================

# creating the window
root = tk.Tk()

root.title("Pentagon Prime")

# Start maximised on Windows
try:
    root.state("zoomed")
except:
    pass


# ============================================================
# 3. CREATING OUR MAIN FRAME
# ============================================================
# creating our main window

main_frame = tk.Frame(
    # putting main_frame inside our window(root())
    root,
    bg=NAVY
)
# packing so that it can show on our screen
main_frame.pack(
    fill="both",
    expand=True
)


# ============================================================
# 4. CREATING THE SCROLLABLE AREA
# ============================================================

# scrolling line on our Gui
# Canvas allows us to create scrolling
canvas = tk.Canvas(
    # inserting on our main frame
    main_frame,
    bg=LIGHT_NAVY,
    # control the thic
    highlightthickness=0
)

canvas.pack(
    side="left",
    fill="both",
    expand=True
)


# ============================================================
# 5. CREATING THE SCROLLBAR
# ============================================================

scrollbar = ttk.Scrollbar(
    main_frame,
    orient="vertical",
    command=canvas.yview
)

scrollbar.pack(
    side="right",
    fill="y"
)


# Connect the scrollbar to the canvas
canvas.configure(
    yscrollcommand=scrollbar.set
)


# ============================================================
# 6. CREATING THE INTRO FRAME INSIDE THE CANVAS
# ============================================================

intro_frame = tk.Frame(
    canvas,
    bg=LIGHT_NAVY
)


# Put the intro frame inside the canvas
canvas_window = canvas.create_window(
    (0, 0),
    window=intro_frame,
    anchor="nw"
)


# ============================================================
# 7. UPDATE SCROLL REGION
# ============================================================

def update_scroll_region(event=None):
    canvas.configure(
        scrollregion=canvas.bbox("all")
    )


intro_frame.bind(
    "<Configure>",
    update_scroll_region
)


# ============================================================
# 8. MAKE THE FRAME FIT THE WIDTH OF THE WINDOW
# ============================================================

def resize_frame(event):
    canvas.itemconfig(
        canvas_window,
        width=event.width
    )


canvas.bind(
    "<Configure>",
    resize_frame
)


# ============================================================
# 9. MOUSE WHEEL SCROLLING
# ============================================================

def mouse_scroll(event):

    # Windows / Linux
    canvas.yview_scroll(
        int(-1 * (event.delta / 120)),
        "units"
    )


canvas.bind_all(
    "<MouseWheel>",
    mouse_scroll
)


# ============================================================
# 10. PROJECT TITLE
# ============================================================

intro_label = tk.Label(
    intro_frame,
    text="Pentagon Prime",
    font=("Arial", 28, "bold"),
    bg=LIGHT_NAVY,
    fg=WHITE
)

intro_label.pack(
    padx=30,
    pady=50
)


# ============================================================
# 11. CREATING THE DESCRIPTION FRAME
# ============================================================

description_frame = tk.Frame(
    intro_frame,
    bg=LIGHT_NAVY
)

description_frame.pack(
    padx=30,
    pady=10,
    fill="x"
)


# ============================================================
# 12. INTRODUCTION TEXT
# ============================================================

description_label = tk.Label(
    description_frame,
    text=(
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
    font=("Arial", 16),
    bg=LIGHT_NAVY,
    fg=WHITE,
    wraplength=900,
    justify="left"
)

description_label.pack(
    fill="x",
    expand=True
)


# ============================================================
# 13. ACCESS BUTTON FUNCTION
# ============================================================

def access_system():
    print("Access button clicked")


# ============================================================
# 14. ACCESS BUTTON
# ============================================================

access_button = tk.Button(
    intro_frame,
    text="ACCESS",
    command=access_system,
    font=("Arial", 16, "bold"),
    fg=BLACK,
    bg=WHITE,
    activebackground=LIGHT_GREY,
    activeforeground=BLACK,
    width=18,
    height=3,
    cursor="hand2"
)

access_button.pack(
    pady=(35, 40)
)


# ============================================================
# 15. START THE PROGRAM
# ============================================================

root.mainloop()





