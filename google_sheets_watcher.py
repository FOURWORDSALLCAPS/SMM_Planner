import gspread
import time

from oauth2client.service_account import ServiceAccountCredentials

if __name__ == '__main__':
    scope = ['https://www.googleapis.com/auth/drive',
             'https://www.googleapis.com/auth/spreadsheets']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)

    client = gspread.authorize(credentials)

    while True:
        sheet = client.open('SMMPlanner').sheet1
        data = sheet.get_all_values()
        headers = data[0]
        rows = data[1:]
        for row in rows:
            row_dict = {}
            for idx, val in enumerate(row):
                header = headers[idx]
                row_dict[header] = val
            if row_dict['Статус\nпубликации'] == 'Да':
                print('Статья опубликована')
            if row_dict['Статус\nпубликации'] == 'Нет':
                print('Статья не опубликована')
        time.sleep(10)
