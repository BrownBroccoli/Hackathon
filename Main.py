import os, json, base64, cohere

from google.auth.api_key import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
co = cohere.Client("HCYnZ0Csxn4dTZdQB0WV2q4K0NJ9uzgzJa4EJd4G")

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


gmail = get_gmail()
print("Gmail connected!")



def search_emails(query):
    results = gmail.users().messages().list(
        userId="me", q=query, maxResults=30
    ).execute()

    emails = []

    for msg in results.get("messages", []):
        email = gmail.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()

        headers = {
            h["name"].lower(): h["value"]
            for h in email["payload"].get("headers", [])
        }

        emails.append({
            "sender": headers.get("from", ""),
            "subject": headers.get("subject", ""),
            "date": headers.get("date", ""),
            "body": email.get("snippet", "")
        })

    return emails

fetched_emails = search_emails("in:anywhere")

top_emails = fetched_emails[:5]

print("\n" + "=" * 50)
print(f" DISPLAYING TOP {len(top_emails)} EMAILS ")
print("=" * 50)

for i, email in enumerate(top_emails, start=1):
    print(f"\n[{i}] SUBJECT: {email['subject']}")
    print(f"    FROM:    {email['sender']}")
    print(f"    DATE:    {email['date']}")
    print(f"    SNIPPET: {email['body']}")
    print("-" * 50)

print("\nEmail AI assistant")
print("Type 'quit' to exit\n")