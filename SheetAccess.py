import os
from os.path import join, dirname
from dotenv import load_dotenv

import json
import gspread

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# wd = os.getcwd()
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credential_string = os.getenv('GOOGLE_CREDENTIALS')
credential_json = json.loads(credential_string)
gc = gspread.service_account_from_dict(credential_json, scopes=scope) #filename=f'{wd}/currency-crawler-credentials.json'
