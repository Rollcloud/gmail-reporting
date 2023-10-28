from __future__ import print_function

import os.path
import re
from datetime import datetime

import numpy as np
import pandas as pd
import termplotlib as tpl
from bashplotlib.histogram import plot_hist
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

MESSAGES_CSV = "messages.csv"


def connect():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

    return service


def labels():
    try:
        service = connect()
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        if not labels:
            print("No labels found.")
            return
        print("Labels:")
        for label in labels:
            label_result = service.users().labels().get(userId="me", id=label["id"]).execute()
            print(f"{label['id']}: {label_result['name']} - {label_result['messagesUnread']}")

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


def getHeader(headers, name):
    for header in headers:
        if header["name"] == name:
            return header["value"]


def load_messages() -> pd.DataFrame:
    try:
        service = connect()
        parameters = dict(userId="me", q="is:unread", maxResults=500)
        results = service.users().messages().list(**parameters).execute()
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return

        message_list = []
        for message in tqdm(messages):
            message_result = service.users().messages().get(userId="me", id=message["id"]).execute()
            received = datetime.fromtimestamp(int(message_result["internalDate"]) // 1000)
            headers = message_result["payload"]["headers"]
            from_ = getHeader(headers, "From")
            try:
                m = re.match(r"(.+) \<(.+)\>", from_)
                from_name, from_address = m.groups()
            except AttributeError:
                from_address = from_.replace("<", "").replace(">", "")
                from_name = None

            subject = getHeader(headers, "Subject")

            message_list.append(
                {
                    "received": received,
                    "from_name": from_name,
                    "from_address": from_address,
                    "subject": subject,
                }
            )

        return pd.DataFrame(message_list)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


def messages() -> pd.DataFrame:
    try:
        df_messages = pd.read_csv(MESSAGES_CSV)
    except FileNotFoundError:
        df_messages = load_messages()
        df_messages.to_csv(MESSAGES_CSV)
    return df_messages


def main():
    # labels()
    df_messages = messages()
    df_address_frequency = df_messages.groupby(["from_address"]).size().sort_values(ascending=False)
    print(df_address_frequency.to_string())

    plot_hist(df_address_frequency, pch="█", binwidth=1, regular=True, xlab=True, showSummary=True)


if __name__ == "__main__":
    main()
