import SheetAccess
import SecretKeys
from .UpdateWorkSheets import get_notion_pages, headers


def process_webhook_data(data):
    import re
    import requests
    import string
    from datetime import datetime, timedelta

    today_dt = datetime.now().astimezone()
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    # Extract CURRENCY_FROM from a submitted Google form
    currency_from = re.findall(r'[A-Z]{3}', data[SecretKeys.CURRENCY_FROM])[0]
    # Extract CURRENCY_TO from a submitted Google form
    currency_to = re.findall(r'[A-Z]{3}', data[SecretKeys.CURRENCY_TO])[0]
    # Extract an exchange rate threshold from a submitted Google form
    threshold_rate = float(data[SecretKeys.THRESHOLD_RATE])
    # Extract USER_EMAIL from a submitted Google form
    user_email = data[SecretKeys.USER_EMAIL]

    # Extract a due date of the notification from a submitted Google form
    try:
        notification_date = data[SecretKeys.NOTIFICATION_DATE]
        notification_date = datetime.strptime(notification_date, '%Y-%m-%d')
    except ValueError:
        # Exception - when a user didn't provide a due date
        notification_date = (datetime.now().astimezone() + timedelta(days=365)).date().strftime('%Y-%m-%d')
        notification_date = datetime.strptime(notification_date, '%Y-%m-%d')

    # Check validity of the due date
    if notification_date < datetime(today_dt.year, today_dt.month, today_dt.day):
        notification_date = (datetime.now().astimezone() + timedelta(days=365)).date().strftime('%Y-%m-%d')
        notification_date = datetime.strptime(notification_date, '%Y-%m-%d')

    # Execute next lines of code only when a user provided a valid email address
    if re.fullmatch(email_pattern, user_email):
        print(currency_from, currency_to, threshold_rate, notification_date, user_email)

        # Add new inputs to Notion database
        notion_page_df = get_notion_pages()

        try:
            unique_id = max(notion_page_df['unique_id']) + 1
        except ValueError:
            unique_id = 0

        def create_notion_page(data: dict):
            create_url = "https://api.notion.com/v1/pages"

            payload = {"parent": {"database_id": SecretKeys.NOTION_DATABASE_ID}, "properties": data}

            response = requests.post(create_url, headers=headers, json=payload)
            print(response.json())

            return response

        new_data = {
            "Unique ID": {"title": [{"text": {"content": f'{unique_id}'}}]},
            "Currency From": {'rich_text': [{'text': {'content': f'{currency_from}'}}]},
            "Currency To": {'rich_text': [{'text': {'content': f'{currency_to}'}}]},
            "Email Address": {'rich_text': [{'text': {'content': f'{user_email}'}}]},
            "Threshold": {'rich_text': [{'text': {'content': f'{threshold_rate}'}}]},
            "Notification Due": {'rich_text': [{'text': {'content': f'{notification_date}'}}]}
        }

        create_notion_page(new_data)

        # Retrieve work sheet
        try:
            data_sheet = SheetAccess.gc.open(SecretKeys.EXCHANGE_RATE_SHEET)
        except:
            data_sheet = SheetAccess.gc.create(SecretKeys.EXCHANGE_RATE_SHEET)

        max_rows = 40000
        n_col = 10

        history_cols = ['called_at', '', '', 'rate', 'change']
        history_cols_range = 'A4:{}'.format(string.ascii_uppercase[len(history_cols)] + str(len(history_cols)))

        try:
            data_sheet.worksheet(f'{currency_from}_{currency_to}')
            print('Already exists')

        except:
            work_sheet = data_sheet.add_worksheet(f'{currency_from}_{currency_to}', rows=max_rows, cols=n_col)

            query_cols = ['called_at', f'{currency_from}', f'{currency_to}', 'rate']
            query_cols_range = 'A1:{}'.format(string.ascii_uppercase[len(query_cols)] + str(len(query_cols)))

            work_sheet.batch_update([{
                'range': query_cols_range,
                'values': [query_cols]
            }, {
                'range': history_cols_range,
                'values': [history_cols]
            }])

            time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            work_sheet.update('D2', '=GOOGLEFINANCE("currency:"&B1&C1)', raw=False)
            work_sheet.update('A2', f'{time_now}', raw=False)

            value_list = work_sheet.row_values(2)
            # value_list[0] = datetime.strptime(value_list[0], '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            work_sheet.update('A5:{}5'.format(string.ascii_uppercase[len(value_list)]),
                              [value_list])
