import os
import gspread

wd = os.getcwd()
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
gc = gspread.service_account(filename=f'{wd}/currency-crawler-credentials.json', scopes=scope)
