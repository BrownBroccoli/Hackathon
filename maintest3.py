import base64
import html
import json
import os
import os.path
import pickle
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

import cohere
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ================= SETUP & CONFIGURATION =================
load_dotenv()

co = cohere.Client('HCYnZ0Csxn4dTZdQB0WV2q4K0NJ9uzgzJa4EJd4G')

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

chat_history = []
gmail = None
selection_timer = None

# ================= COLOUR PALETTE =================
NAVY = "#071A33"
LIGHT_NAVY = "#0D2A4A"
BLUE = "#1597E5"
GREEN = "#20C997"
WHITE = "#FFFFFF"
LIGHT_GREY = "#D8E3F0"
RED = "#E74C3C"
BLACK = "#000000"

# ================= DATABASE SETUP =================
conn = sqlite3.connect("emails.db", check_same_thread=False)
conn.execute(
    """CREATE TABLE IF NOT EXISTS EMAILS (
        Email_Id TEXT PRIMARY KEY,
        Name TEXT,
        Gmail TEXT,
        sDate TEXT,
        Subject TEXT,
        Body TEXT,
        Category TEXT
    )"""
)

cursor = conn.execute("PRAGMA table_info(EMAILS)")
columns = [col[1] for col in cursor.fetchall()]
if "Category" not in columns:
    conn.execute("ALTER TABLE EMAILS ADD COLUMN Category TEXT")

conn.commit()


# ================= GMAIL AUTH & APIS =================
def get_gmail(force_new=False):
    if force_new and os.path.exists("token.pickle"):
        try:
            os.remove("token.pickle")
        except Exception:
            pass

    creds = None
    if os.path.exists("token.pickle"):
        try:
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


try:
    gmail = get_gmail()
except Exception as e:
    print(f"Gmail Auth Warning: {e}")


def decode_body_data(data_str):
    try:
        decoded_bytes = base64.urlsafe_b64decode(data_str.encode("UTF-8"))
        decoded_text = decoded_bytes.decode("utf-8", errors="replace")
        return html.unescape(decoded_text)
    except Exception:
        return ""


def extract_email_body(payload):
    if "body" in payload and payload["body"].get("data"):
        return decode_body_data(payload["body"]["data"])

    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain" and part["body"].get("data"):
                return decode_body_data(part["body"]["data"])
            elif "parts" in part:
                body = extract_email_body(part)
                if body:
                    return body
    return ""


def parse_sender(sender_str):
    if "<" in sender_str and ">" in sender_str:
        pos1 = sender_str.find("<")
        name = sender_str[:pos1].strip().replace('"', "")
        g_mail = sender_str[pos1:].replace("<", "").replace(">", "").strip()
        return name, g_mail
    return sender_str, sender_str


def clean_search_query(user_text):
    text = user_text.lower()
    for drop_word in [
        "any emails from",
        "emails from",
        "email from",
        "any email from",
        "find emails about",
        "show emails",
        "fetch emails",
    ]:
        text = text.replace(drop_word, "")

    clean_keyword = text.strip()

    category_map = {
        "primary": "category:primary",
        "promotions": "category:promotions",
        "social": "category:social",
        "updates": "category:updates",
        "forums": "category:forums",
        "unread": "is:unread",
        "important": "is:important",
    }

    if clean_keyword in category_map:
        return category_map[clean_keyword]

    if not clean_keyword:
        return "in:anywhere"

    return clean_keyword


def search_emails(query):
    if not gmail:
        return []

    try:
        clean_q = clean_search_query(query)
        results = (
            gmail.users()
            .messages()
            .list(userId="me", q=clean_q, maxResults=30)
            .execute()
        )
        emails = []

        for msg in results.get("messages", []):
            try:
                email = (
                    gmail.users()
                    .messages()
                    .get(userId="me", id=msg["id"], format="full")
                    .execute()
                )
                headers = {
                    h["name"].lower(): h["value"]
                    for h in email["payload"].get("headers", [])
                }
                labels = email.get("labelIds", [])

                categories = [
                    label.replace("CATEGORY_", "").capitalize()
                    for label in labels
                    if label.startswith("CATEGORY_")
                ]
                category_name = categories[0] if categories else "Primary"

                raw_snippet = email.get("snippet", "")
                clean_snippet = html.unescape(raw_snippet)
                full_body = (
                    extract_email_body(email["payload"]) or clean_snippet
                )
                truncated_body = full_body[:2000]

                sender_raw = headers.get("from", "")
                name, g_mail = parse_sender(sender_raw)
                date_str = headers.get("date", "")
                subject_str = headers.get("subject", "")

                emails.append(
                    {
                        "email_id": msg["id"],
                        "sender": sender_raw,
                        "subject": subject_str,
                        "date": date_str,
                        "body": truncated_body,
                        "category": category_name,
                    }
                )

                conn.execute(
                    """INSERT OR REPLACE INTO EMAILS (Email_Id, Name, Gmail, sDate, Subject, Body, Category)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        msg["id"],
                        name,
                        g_mail,
                        date_str,
                        subject_str,
                        truncated_body,
                        category_name,
                    ),
                )
            except Exception as single_msg_err:
                print(f"Skipped email {msg['id']}: {single_msg_err}")
                continue

        conn.commit()
        return emails
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []


# ================= COHERE CHAT ENGINE =================
def run_cohere_chat(prompt, isolated=False):
    global chat_history

    if not co:
        return "[API Error: COHERE_API_KEY is missing from environment file.]"

    try:
        if isolated:
            response = co.chat(
                model="command-r-plus-08-2024",
                message=prompt,
            )
            return response.text

        response = co.chat(
            model="command-r-plus-08-2024",
            message=prompt,
            chat_history=chat_history,
        )

        answer = response.text
        chat_history.append({"role": "USER", "message": prompt})
        chat_history.append({"role": "CHATBOT", "message": answer})
        return answer

    except Exception as e:
        print(f"Cohere API Error: {e}")
        return f"[API Error: Unable to process request. Details: {e}]"


# ================= ROOT APPLICATION =================
root = tk.Tk()
root.title("Pentagon Prime")
root.geometry("1200x700")
root.configure(bg=NAVY)

try:
    root.state("zoomed")
except Exception:
    pass

# Containers
main_intro_container = tk.Frame(root, bg=NAVY)
main_intro_container.pack(fill="both", expand=True)

email_app_frame = tk.Frame(root, bg="#172033")

# ================= PAGE 1: INTRODUCTION SCREEN =================
canvas = tk.Canvas(main_intro_container, bg=LIGHT_NAVY, highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(
    main_intro_container, orient="vertical", command=canvas.yview
)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)

intro_frame = tk.Frame(canvas, bg=LIGHT_NAVY)
canvas_window = canvas.create_window((0, 0), window=intro_frame, anchor="nw")


def update_scroll_region(event=None):
    canvas.configure(scrollregion=canvas.bbox("all"))


intro_frame.bind("<Configure>", update_scroll_region)


def resize_frame(event):
    canvas.itemconfig(canvas_window, width=event.width)


canvas.bind("<Configure>", resize_frame)


def mouse_scroll(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


canvas.bind_all("<MouseWheel>", mouse_scroll)

intro_label = tk.Label(
    intro_frame,
    text="Pentagon Prime",
    font=("Arial", 28, "bold"),
    bg=LIGHT_NAVY,
    fg=WHITE,
)
intro_label.pack(padx=30, pady=50)

description_frame = tk.Frame(intro_frame, bg=LIGHT_NAVY)
description_frame.pack(padx=30, pady=10, fill="x")

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
        '"ACCESS" button below.'
    ),
    font=("Arial", 16),
    bg=LIGHT_NAVY,
    fg=WHITE,
    wraplength=900,
    justify="left",
)
description_label.pack(fill="x", expand=True)


# ================= PAGE 2: EMAIL MANAGEMENT SYSTEM =================
email_app_frame.grid_rowconfigure(0, weight=1)
email_app_frame.grid_columnconfigure(0, weight=1)
email_app_frame.grid_columnconfigure(1, weight=1)

# Left Side Panel - Email Database View
left = tk.Frame(email_app_frame, bg="#172033", bd=2, relief="groove")
left.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(15, 8), pady=15)
left.grid_rowconfigure(0, weight=1)
left.grid_columnconfigure(0, weight=1)

tree = ttk.Treeview(
    left,
    columns=("Email ID", "Name", "Gmail", "Date", "Subject"),
    show="headings",
)
for col in ("Email ID", "Name", "Gmail", "Date", "Subject"):
    tree.heading(col, text=col)

tree.column("Email ID", width=110)
tree.column("Name", width=100)
tree.column("Gmail", width=120)
tree.column("Date", width=140)
tree.column("Subject", width=150)
tree.grid(row=0, column=0, sticky="nsew")

scroll = ttk.Scrollbar(left, orient="vertical", command=tree.yview)
scroll.grid(row=0, column=1, sticky="ns")
tree.configure(yscrollcommand=scroll.set)


def update_treeview(email_list):
    tree.delete(*tree.get_children())
    for item in email_list:
        name, g_mail = parse_sender(item.get("sender", ""))
        tree.insert(
            "",
            "end",
            values=(
                item.get("email_id", ""),
                name,
                g_mail,
                item.get("date", ""),
                item.get("subject", ""),
            ),
        )


def displaying_all_emails():
    tree.delete(*tree.get_children())
    try:
        emails = conn.execute(
            "SELECT Email_Id, Name, Gmail, sDate, Subject FROM EMAILS ORDER BY ROWID DESC LIMIT 30"
        ).fetchall()
        for email in emails:
            tree.insert("", "end", values=email)
    except Exception as e:
        print(f"Database Read Error: {e}")


# Right Side Panel - Chat & Controls
right = tk.Frame(email_app_frame, bg="#172033")
right.grid(row=0, column=1, sticky="nsew", padx=(8, 15), pady=15)
right.grid_columnconfigure(0, weight=1)
right.grid_rowconfigure(1, weight=1)

input_frame = tk.Frame(right, bg="#172033")
input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
input_frame.grid_columnconfigure(0, weight=1)

input_title = tk.Label(
    input_frame,
    text="Input / Interact with Chat Bot",
    bg="#172033",
    fg="white",
    font=("Arial", 12, "bold", "underline"),
)
input_title.grid(row=0, column=0, sticky="w", pady=(0, 5))

input_box = tk.Entry(input_frame, font=("Arial", 12), bg="white", fg="black")
input_box.grid(row=1, column=0, sticky="ew", ipady=8, padx=(0, 10))

output_frame = tk.Frame(right, bg="#172033", bd=2, relief="groove")
output_frame.grid(row=1, column=0, sticky="nsew")
output_frame.grid_rowconfigure(0, weight=1)
output_frame.grid_columnconfigure(0, weight=1)

output = tk.Text(
    output_frame, wrap="word", font=("Arial", 11), bg="white", fg="black"
)
output.grid(row=0, column=0, sticky="nsew")

output_scroll = ttk.Scrollbar(
    output_frame, orient="vertical", command=output.yview
)
output_scroll.grid(row=0, column=1, sticky="ns")
output.configure(yscrollcommand=output_scroll.set)

output.tag_configure(
    "selected",
    background="#172033",
    foreground="white",
    font=("Arial", 11, "bold"),
)


def search_run():
    message = input_box.get().strip()
    if not message:
        return

    email_words = [
        "email",
        "emails",
        "mail",
        "gmail",
        "inbox",
        "unread",
        "important",
        "fetch",
        "find",
        "search",
        "from",
        "primary",
        "promotions",
        "social",
        "updates",
        "forums",
    ]

    if any(word in message.lower() for word in email_words):
        emails = search_emails(message)
        if emails:
            update_treeview(emails)
        else:
            displaying_all_emails()

        prompt = (
            f"You are an AI email assistant.\n\n"
            f"User Question: {message}\n\n"
            f"Emails Found in System:\n{json.dumps(emails)}\n\n"
            f"Provide a concise, helpful answer based on these emails."
        )
    else:
        prompt = message

    bot_reply = run_cohere_chat(prompt, isolated=False)

    output.insert("end", f"You: {message}\n")
    output.insert("end", f"Bot: {bot_reply}\n\n")
    output.see("end")
    input_box.delete(0, "end")


input_box.bind("<Return>", lambda event: search_run())

search_btn = tk.Button(
    input_frame,
    text="Search / Run",
    command=search_run,
    bg="#16823B",
    fg="white",
    activebackground="#0F5F2B",
    activeforeground="white",
    font=("Arial", 10, "bold"),
    relief="raised",
    bd=2,
    padx=10,
    pady=5,
)
search_btn.grid(row=1, column=1, ipadx=10, ipady=5)

# Bottom Controls Panel
bottom = tk.Frame(email_app_frame, bg="#172033")
bottom.grid(row=1, column=1, sticky="ew", padx=(8, 15), pady=(0, 15))
bottom.grid_columnconfigure(1, weight=1)


def cmb_filter():
    selected_cat = c_option.get().lower()

    if selected_cat in ("all emails", "select category"):
        displaying_all_emails()
        return

    emails = search_emails(selected_cat)
    update_treeview(emails)


def switch_account():
    global gmail, chat_history

    confirm = messagebox.askyesno(
        "Switch Account",
        "Are you sure you want to sign in with a different Google account?\n\nThis will clear the local database cache.",
    )
    if not confirm:
        return

    try:
        conn.execute("DELETE FROM EMAILS")
        conn.commit()
    except Exception as e:
        print(f"Error resetting database: {e}")

    chat_history.clear()
    output.delete("1.0", "end")
    tree.delete(*tree.get_children())

    gmail = get_gmail(force_new=True)

    emails = search_emails("in:anywhere")
    update_treeview(emails)

    output.insert(
        "end",
        "Account switched successfully! Loaded emails from new account.\n\n",
    )


categories = [
    "All emails",
    "Primary",
    "Promotions",
    "Social",
    "Updates",
    "Forums",
    "Unread",
    "Important",
]
c_option = tk.StringVar(value="Select Category")
combo = ttk.Combobox(
    bottom, values=categories, state="readonly", textvariable=c_option
)
combo.grid(row=0, column=1, sticky="ew", ipady=5)

run_button = tk.Button(
    bottom,
    text="Filter",
    command=cmb_filter,
    bg="#16823B",
    fg="white",
    activebackground="#0F5F2B",
    activeforeground="white",
    font=("Arial", 10, "bold"),
    relief="raised",
    bd=2,
    padx=10,
    pady=5,
)
run_button.grid(row=0, column=0, padx=(0, 10), ipadx=10, ipady=5)

switch_acc_btn = tk.Button(
    bottom,
    text="Switch Account",
    command=switch_account,
    bg="#2B579A",
    fg="white",
    activebackground="#1E3D6B",
    activeforeground="white",
    font=("Arial", 10, "bold"),
    relief="raised",
    bd=2,
    padx=10,
    pady=5,
)
switch_acc_btn.grid(row=0, column=2, padx=(10, 0), ipadx=10, ipady=5)


def process_email_selection():
    selected = tree.selection()
    if not selected:
        return

    values = tree.item(selected[0])["values"]
    if not values:
        return

    email_id = values[0]

    cursor = conn.execute(
        "SELECT Body, Category FROM EMAILS WHERE Email_Id = ?", (str(email_id),)
    )
    row = cursor.fetchone()

    if row:
        body, category = row[0], row[1]
        summary_prompt = f"Summarize this email in 2 brief sentences:\n{body}"

        summary = run_cohere_chat(summary_prompt, isolated=True)

        output.insert("end", "\nSelected Email Details\n", "selected")
        output.insert(
            "end",
            f"SUBJECT: {values[4]}\n"
            f"FROM: {values[1]} ({values[2]})\n"
            f"DATE: {values[3]}\n"
            f"CATEGORY: {category}\n"
            f"SUMMARY: {summary}\n\n",
        )
        output.see("end")


def selected_email(event):
    global selection_timer
    if selection_timer is not None:
        root.after_cancel(selection_timer)
    selection_timer = root.after(350, process_email_selection)


tree.bind("<<TreeviewSelect>>", selected_email)


# ================= PAGE SWITCHING LOGIC =================
def access_system():
    # Hide introduction page
    main_intro_container.pack_forget()

    # Show email management application page
    email_app_frame.pack(fill="both", expand=True)

    # Initial email search load
    initial_emails = search_emails("in:anywhere")
    update_treeview(initial_emails)


# ACCESS button on the intro screen
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
    cursor="hand2",
)
access_button.pack(pady=(35, 40))

root.mainloop()