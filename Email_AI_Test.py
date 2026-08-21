import os, json, base64, cohere
import pickle
import os.path
import textwrap
from unittest import result

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
import sqlite3

conn = sqlite3.connect('emails.db')
conn.execute('''CREATE TABLE IF NOT EXISTS EMAILS (Email_Id PRIMARY KEY,Name TEXT,Gmail TEXT,sDate DATE,Subject TEXT,
                                                   Body TEXT)''' )
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

print("\n" + "═" * 80)
print(f" DISPLAYING TOP {len(top_emails)} EMAILS ".center(60, "═"))
print("═" * 80)

for i, email in enumerate(top_emails, start=1):
  # Clean up sender string (removes long angle-bracketed emails if needed)
  sender = email["sender"].replace("<", "(").replace(">", ")")

  # Truncate and wrap body text nicely
  body_preview = email["body"] + "..." if len(email["body"]) else email["body"]
  wrapped_body = textwrap.fill(body_preview, width=70, subsequent_indent=" " * 15)

  print(f"\n[{i}] SUBJECT  : {email['subject']}")
  print(f"    FROM     : {sender}")
  print(f"    DATE     : {email['date']}")
  print(f"    CATEGORY : {email['category']}")
  print(f"    BODY     : {wrapped_body}")
  print("─" * 80)

print("\nEmail AI assistant")
print("Type 'quit' to exit\n")


def adding_email_db():
    fetched_emails = search_emails('in:anywhere')

    for email in fetched_emails[:5]:

        # can be done in another function might need to addd it to that function instead only at the end tho
        # after everythingwe have is working and going going to improve bugs and whatnot
        sender = email["sender"]
        pos1 = sender.find('<')
        name = sender[:pos1]
        g_mail= sender[pos1:]
        g_mail = g_mail.replace('>','')
        g_mail = g_mail.replace('<','')

        conn.execute(
            """INSERT INTO EMAILS (Email_ID, Name, Gmail, SDate, Subject, Body)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (email["email_id"], name, g_mail, email["date"], email["subject"], email["body"]),
        )

        conn.commit()



adding_email_db()

+