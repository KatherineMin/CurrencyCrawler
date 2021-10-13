from datetime import datetime
import GoogleSheet
gs_sheet = GoogleSheet.gs_sheet
col_name = GoogleSheet.col_name

class Information(GoogleSheet):
    """
        Functionalities that are related to get data
    """
    def __init__(self):
        working_ws = super().get_worksheet()

    def set_currency_rate(self):
        col_loc = col_name['Rate'].index+1
        row_loc = self.get_first_available_row(col_loc)
        insert_val = '=GOOGLEFINANCE(concat("{}","{}"))'.format(self.currency_code1, self.currency_code2)
        dt_now = datetime.now()
        self.working_ws.update_cell(row_loc, col_name['DateTime'].index+1, dt_now.strftime('%Y-%m-%d %H:%M:%S'))
        self.working_ws.update_cell(row_loc, col_name['Day'].index+1, dt_now.strftime('%A'))
        self.working_ws.update_cell(row_loc, col_name['Time'].index+1, dt_now.strftime('%H:%M:%S'))
        self.working_ws.update_cell(row_loc, col_loc, insert_val)

    # overriding abstract method
    def get_first_available_row(self, col_index):
        value_list = list(filter(None, self.working_ws.col_values(col_index)))
        return len(value_list) + 1
