import gspread
from abc import ABC, abstractmethod
from datetime import datetime
import string

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
gc = gspread.service_account(filename='credentials.json', scopes=scope)
gs_sheet = gc.create('Currency Exchange Rate')
gs_sheet.share('msyeon1028@gmail.com', perm_type='user', role='owner')

col_name = ['DateTime', 'Rate', 'Changes(%)', '', 'Day', 'Time']
col_map = {c:a for c, a in zip(col_name, string.ascii_uppercase[:len(col_name)])}

class GoogleSheet(ABC):
    """
        Activities after creation of google sheet
    """
    def __init__(self, currency_code1, currency_code2):
        self.currency_code1 = currency_code1
        self.currency_code2 = currency_code2
        self.worksheet_title = '{}_{}'.format(currency_code1, currency_code2)
    # def get_currency_code(self):
    #     return self.currency_code1, self.currency_code2
    @abstractmethod
    def get_first_available_row(self, col_index):
        pass

    def new_worksheet(self, rows=200, cols=20):
        if (rows < 3 | cols < 6):
            print("This work sheet requires more than 2 rows and 5 columns!")
        else:
            ws = gs_sheet.add_worksheet(title=self.worksheet_title,
                                        rows=rows, cols=cols)
            ws.batch_update([{
                'range': 'A1:B1',
                'values': [[self.currency_code1, self.currency_code2]]
            }, {
                'range': 'A2:F2',
                'values': [col_name]
            }])
            ws.format('A1:F2', {'textFormat': {'bold': True}})

    def get_worksheet(self):
        working_ws = gs_sheet.worksheet(self.worksheet_title)
        return working_ws

    ## Append rows
    def append_row(self):
        ws = self.get_worksheet()
        col_loc = col_name['Rate'].index + 1
        row_loc = self.get_first_available_row(col_loc)
        update_list = ws.row_values(3)
        range1 = list(col_map.values())[0]; range2=list(col_map.values())[-1];
        ws.update('{}:{}'.format(range1+str(row_loc), range2+str(row_loc)), update_list)

    ## Calculate changes
    def calculate_change(self):
        ws = self.get_worksheet()
        col_loc = col_name['Rate'].index+1
        row_range = self.get_first_available_row(col_loc) - 1
        change_loc = col_map['Changes(%)']
        calculate_list = [['=round((100+({post}-{prior})/{prior}*100),2)'.format(**{'post':change_loc+str(i+1), 'prior':change_loc+str(i)})]
                          for i in range(4, row_range+1, 1)]
        ws.update('{}:{}'.format(change_loc+str(5), change_loc+str(row_range)), calculate_list)
