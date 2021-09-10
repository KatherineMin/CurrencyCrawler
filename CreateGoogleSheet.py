import gspread

# Set scopes
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Provide
gc = gspread.service_account(filename='credentials.json', scopes=scope)
sheet = gc.create('Currency Exchange Rate')

# Make the sheet visible to your account
sheet.share('msyeon1028@gmail.com', perm_type='user', role='owner')

def create_worksheet(currency_code1, currency_code2, rows=200, cols=20):
    if (rows < 3 | cols < 6) :
        print("Currency sheet requires at least 3 rows and 6 columns!")
    else:
        worksheet = sheet.add_worksheet(title='{}_{}'.format(currency_code1, currency_code2), rows=rows, cols=cols)
        worksheet.batch_update([{
            'range': 'A1:B1',
            'values': [[currency_code1, currency_code2]]
        }, {
            'range': 'A2:F2',
            'values': [['DateTime', 'Rate', 'Changes', '', 'Day', 'Time']]
        }, {
            'range': 'E4:'
        }])
        worksheet.format('A1:F2', {'textFormat': {'bold': True}})
        worksheet.update('A3', 'Latest')
        worksheet.update('B3', '=GOOGLEFINANCE("currency:"&A1&B1)', value_input_option="USER_ENTERED")
