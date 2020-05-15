#!/bin/env python3

import pickle
import os.path
import sys
from typing import List

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import git
from git import Repo

import os
import traceback

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1Tbf_sJSQ1ya5JGPpfuR4wTA21SNX9IRbSmQ0IOrCh54'
SAMPLE_RANGE_NAME = 'A2:E'


def clone(data: List[str]) -> bool:
    nom = data[0]
    prenom = data[1]
    url = data[2]
    date = data[3]

    path = f"tmp/{nom}-{prenom}/"

    repo = None
    try:
        if os.path.exists(path):
            repo = Repo(path)
            print(f"{nom} {prenom} : pulling")
            repo.remote("origin").pull()
        else:
            # git.Git(path).clone(url)
            print(f"{nom} {prenom} : cloning")
            repo = Repo.clone_from(url, path)
        return os.path.exists(path)
    except git.exc.GitCommandError:
        print("Impossible de cloner/pull le dépôt", file=sys.stderr)
        traceback.print_exc()
        return False


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user remove.sh in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            # print('%s, %s : %s' % (row[0], row[1]))
            # print(f"{row[0]} {row[1]} : {'yes' if row[4] == 'O' else 'no'}")
            row[4] = 'Peut-être ?'
            clone(row)

    sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME,
                          valueInputOption='RAW', body={
            "range": SAMPLE_RANGE_NAME,
            "majorDimension": "ROWS",
            "values": values

        }).execute()


if __name__ == '__main__':
    main()
