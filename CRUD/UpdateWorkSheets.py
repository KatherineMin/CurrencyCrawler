import SheetAccess
import SecretKeys
import pandas as pd
import re
import requests

headers = {
    "Authorization": "Bearer " + SecretKeys.NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_notion_pages():
    url = f"https://api.notion.com/v1/databases/{SecretKeys.NOTION_DATABASE_ID}/query"

    payload = {"page_size": 100}
    response = requests.post(url, json=payload, headers=headers)

    notion_data = response.json()
    # import json
    # with open('db.json', 'w', encoding='utf8') as f:
    #     json.dump(notion_data, f, ensure_ascii=False, indent=4)
    notion_results = notion_data['results']

    page_df = pd.DataFrame(columns=['page_id', 'unique_id', 'currency_from', 'currency_to', 'user_email', 'threshold', 'notification_date', 'last_edited_time'])
    for i, page in enumerate(notion_results):
        page_id = page['id']
        props = page['properties']
        unique_id = props['Unique ID']['title'][0]['text']['content']
        currency_from = props['Currency From']['rich_text'][0]['text']['content']
        currency_to = props['Currency To']['rich_text'][0]['text']['content']
        user_email = props['Email Address']['rich_text'][0]['text']['content']
        threshold = props['Threshold']['rich_text'][0]['text']['content']
        notification_date = props['Notification Due']['rich_text'][0]['text']['content']
        last_edited_time = props['Last edited time']['last_edited_time']

        page_df.loc[i, :] = [page_id, unique_id, currency_from, currency_to, user_email, threshold, notification_date, last_edited_time]

    print(page_df)
    return page_df


def update_values():

    data_sheet = SheetAccess.gc.open(SecretKeys.EXCHANGE_RATE_SHEET)
    worksheet_list = data_sheet.worksheets()
    worksheet_list = [re.findall("'([^']*)'", str(e))[0] for e in worksheet_list]

    def append_row(work_sheet_name):
        from datetime import datetime
        import string

        work_sheet = data_sheet.worksheet(work_sheet_name)
        value_lists = work_sheet.get_all_values()

        rate_idx = value_lists[3].index('rate')
        change_idx = value_lists[3].index('change')

        last_row_values = value_lists[-1]

        new_row_values = value_lists[1]
        new_row_values[0] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_row_values[change_idx] = (float(last_row_values[rate_idx]) + float(new_row_values[rate_idx]) - float(last_row_values[rate_idx])) / float(last_row_values[rate_idx])

        appending_row_idx = len(value_lists)+1
        appending_range = 'A{row_idx}:{alpha}{row_idx}'.format(row_idx=appending_row_idx, alpha=string.ascii_uppercase[len(new_row_values)])

        work_sheet.update(appending_range, [new_row_values])

        return new_row_values[rate_idx]

    update_df = pd.DataFrame(columns=['currency_from', 'currency_to', 'fx_rate'])
    for i, tab_name in enumerate(worksheet_list):
        from_currency, to_currency = tab_name.split('_')
        rate_now = append_row(tab_name)

        update_df.loc[i, :] = [from_currency, to_currency, rate_now]

    return update_df


def email_recipients():

    user_input_df = get_notion_pages()
    update_df = update_values()

    def roundNearest(number):
        n = abs(float(number))
        if n < 1:
            s = f'{n:.99f}'
            index = re.search('[1-9]', s).start()
            return float(s[:index + 2])
        else:
            return round(n, 2)

    merged_df = user_input_df.merge(
        update_df,
        on=['currency_from', 'currency_to'],
        how='left'
    )

    return merged_df[merged_df.apply(lambda row: abs(roundNearest(row['threshold'])-roundNearest(row['fx_rate'])) / roundNearest(row['threshold']) < 0.001, axis=1)]
