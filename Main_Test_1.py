
from operator import truediv
import os, json, base64, cohere
import pickle
import os.path
from unittest import result

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
import sqlite3
import cohere
import tkinter as tk
from tkinter import ttk
from datetime import datetime

co = cohere.Client('HCYnZ0Csxn4dTZdQB0WV2q4K0NJ9uzgzJa4EJd4G')


def chat_memory():
    with open('memory.txt', 'w') as memory: # every time the program runs a new file will be created and if a file already
    #exists it will be wiped clean to make room for new memory
        memory.write("Hi, You are an Email AI assistant for a business\n"
                     " This text will contain all of your memory on the previous chats between you and the user "
                     "\nGo through this the recent chats before you")
        memory.close()


chat_memory()



def email_search_ai(msg):
    email_words = ["email", "emails", "mail", "gmail", "inbox",
                   "unread", "important"]

    if any(word in msg.lower() for word in email_words):
        query = "in:anywhere"

        if "unread" in msg.lower():
            query = "is:unread"
        elif "important" in msg.lower():
            query = "is:important"

        print("Searching Gmail:", query)
        emails = search_emails(query)
        return emails
    else:
        return msg



def reading_memory():
    with open('memory.txt', 'r') as memory:
        return  memory.read()

def chat(msg):
    chat_mem = reading_memory()
    emails = ''


    response = co.chat(
        model='command-r-plus-08-2024',
        message= (chat_mem + '\n'+ msg # Before getting the user's msg the AI will go through the memory file
                  # first so that the chats are consistent and previous result/msgs sent by the AI can u updated
                  # and changed with easy, Having a memory will also allow the AI to adapt as the chat goes on
                  ))


    with (open('memory.txt', 'a') as memory):
        memory.write(f'\nUser: {msg}\n')
        memory.write(f'AI Assistant: {response.text}\n')
        memory.close()

    return response.text




conn = sqlite3.connect('emails.db')
conn.execute('''CREATE TABLE IF NOT EXISTS EMAILS (Email_Id PRIMARY KEY,Name TEXT,Gmail TEXT,sDate DATE,Subject TEXT,
                                                   Body TEXT,Category TEXT)''' )
print('Databse connected')
conn.commit()



load_dotenv()
co = cohere.Client("HCYnZ0Csxn4dTZdQB0WV2q4K0NJ9uzgzJa4EJd4G")

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)



gmail = get_gmail()
print("Gmail connected!")



def search_emails(query):
    # searches your gmail <>
    results = gmail.users().messages().list(
        userId="me", q=query, maxResults=30
    ).execute()

    emails = []

    import base64
    import html

    def decode_body_data(data_str):
        """Decodes URL-safe base64 string into standard UTF-8 text."""
        # Convert URL-safe base64 back to bytes
        decoded_bytes = base64.urlsafe_b64decode(data_str.encode("UTF-8"))

        # Decode bytes to string, replacing undecodable characters safely
        decoded_text = decoded_bytes.decode("utf-8", errors="replace")

        # Unescape HTML entities (e.g., converts &amp; to & or &#39; to ')
        return html.unescape(decoded_text)

    def extract_email_body(payload):

        if "body" in payload and payload["body"].get("data"):
            return decode_body_data(payload["body"]["data"])

        # If the email is multipart, iterate through parts to find text/plain
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain" and part["body"].get("data"):
                    return decode_body_data(part["body"]["data"])
                # Recursively check sub-parts
                elif "parts" in part:
                    body = extract_email_body(part)
                    if body:
                        return body
        return ""

    # Inside your search_emails function, update the loop body:
    for msg in results.get("messages", []):
        email = (
            gmail.users()
            .messages()
            .get(userId="me", id=msg["id"], format="full")
            .execute()
        )

        headers = {
            h["name"].lower(): h["value"] for h in email["payload"].get("headers", [])
        }
        labels = email.get("labelIds", [])

        categories = [
            label.replace("CATEGORY_", "").capitalize()
            for label in labels
            if label.startswith("CATEGORY_")
        ]
        category_name = categories[0] if categories else "Primary"

        # Extract clean decoded body (fallback to unescaped snippet if empty)
        raw_snippet = email.get("snippet", "")
        clean_snippet = html.unescape(raw_snippet)
        full_body = extract_email_body(email["payload"]) or clean_snippet

        emails.append({
            'email_id' : msg['id'],
            "sender": headers.get("from", ""),
            "subject": headers.get("subject", ""),
            "date": headers.get("date", ""),
            "body": full_body,  # Truncated snippet view
            "category": category_name,
            "all_labels": labels,

        })

    return emails

fetched_emails = search_emails("in:anywhere")

top_emails = fetched_emails[:5]

#print("\n" + "=" * 50)
#print(f" DISPLAYING TOP {len(top_emails)} EMAILS ")
#print("=" * 50)

#for i, email in enumerate(top_emails, start=1):
#    print(f"\n[{i}] SUBJECT: {email['subject']}")
#    print(f"    FROM:    {email['sender']}")
#    print(f"    DATE:    {email['date']}")
#    print(f"    CATEGORY: {email['category']}")
#    print(f"    SNIPPET: {email['body']}")
#    print("-" * 50)

#print("\nEmail AI assistant")
#print("Type 'quit' to exit\n")


def adding_email_db():
    fetched_emails = search_emails('in:anywhere')

    for email in fetched_emails[:5]:

        cat = chat(f'Give this email a one word category ONLY to fall under like social or promotional: \n{email}')

        # can be done in another function might need to addd it to that function instead only at the end tho
        # after everything have is working and going to improve bugs and whatnot
        sender = email["sender"]
        pos1 = sender.find('<')
        name = sender[:pos1]
        g_mail= sender[pos1:]
        g_mail = g_mail.replace('>','')
        g_mail = g_mail.replace('<','')

        conn.execute(
            """INSERT INTO EMAILS (Email_ID, Name, Gmail, SDate, Subject, Body,Category)
               VALUES (?, ?, ?, ?, ?, ?,?)""",
            (email["email_id"], name, g_mail, email["date"], email["subject"], email["body"],cat),
        )

        conn.commit()



# adding_email_db()

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
    columns=("Email ID", "Name", "Gmail", "Date", "Subject"),
    show="headings"
)

for col in ("Email ID", "Name", "Gmail", "Date", "Subject"):
    tree.heading(col, text=col)

tree.column("Email ID", width=150)
tree.column("Name", width=100)
tree.column("Gmail", width=100)
tree.column("Date", width=150)
tree.column("Subject", width=100)

tree.grid(row=0, column=0, sticky="nsew")


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


# This will make it so that the AI can read the email data in a readable for format




# ================= GETTING DATA =================
def displaying_all_emails():
    # Displays the emails on the first run
    emails = conn.execute('''SELECT * FROM EMAILS''')
    for email in emails:
        tree.insert("", "end", values=email)
# Insert data into Treeview
displaying_all_emails()



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
    msg = input_box.get()
    emails = email_search_ai(msg)
    temp_msg = msg
    msg = (f"You are an AI Email Assistant."
           f"User: {msg}\n"
           f"""Emails:{json.dumps(emails)}\n"""
           f"Use The emails above to help the user, and do not reference those emails unless the user asks you to"
           f"\n Display the email info in a clean format")


    output.insert("end", f"You: {temp_msg}\n")
    output.insert("end", f"Bot: {chat(msg)}.\n\n")
    output.see("end")
    input_box.delete(0, "end")



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
def cmb_filter():
    if c_option.get() == 'All emails':
        tree.delete(*tree.get_children())

        displaying_all_emails()
    else:
        tree.delete(*tree.get_children())
        emails = conn.execute(
            "SELECT * FROM EMAILS WHERE Category = ?", (c_option.get(),)
        )

        for email in emails:
            tree.insert("", "end", values=email)






# ================= CATEGORY COMBO BOX =================
categories = [
    'All emails',
    "Security",
    "Billing",
    "Policy",
    "Payment",
    "Delivery"
]
c_option = tk.StringVar()
combo = ttk.Combobox(
    bottom,
    values=categories,
    state="readonly",
    textvariable=c_option

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


# ================= Filter =================
run_button = tk.Button(
    bottom,
    text="Filter",
    command=cmb_filter,

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


# ================= SELECT EMAIL =================
def get_categories(values):
    f_email = conn.execute("SELECT * FROM EMAILS WHERE Email_id = ?", (values[0],)).fetchall()
    return chat(f'Give this email a one word category ONLY to fall under like social or promotional \n{f_email})')



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
        # Get the emails' body
        body = conn.execute("SELECT BODY FROM EMAILS WHERE Email_id = ?",(values[0],)).fetchall()

        new_body = chat(f"summarise this into a short paragraph: \n{body}")

        output.insert(
            "end",
            f"SUBJECT: {values[4]}\n"
            f"FROM: {values[1]}\n"
            f"DATE: {values[3]}\n"
            f"CATEGORY: {get_categories(values)}\n"
            f"BODY: {new_body}\n\n",
            "selected"
        )

        print("─" * 80)

        output.see("end")

# Detect when an email is selected
tree.bind(
    "<<TreeviewSelect>>",
    selected_email
)

# ================= START PROGRAM =================
root.mainloop()
