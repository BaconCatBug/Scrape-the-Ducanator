try:
    from csv import QUOTE_ALL
    from bs4 import BeautifulSoup
    from requests import get
    from re import search
    from pandas import read_json, set_option
    from traceback import format_exc
except ModuleNotFoundError:
    print('OOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The code monkeys at our headquarters are working VEWY HAWD to fix this!')
    print('You didn\'t install the packages like I told you to. Please run \"pip install bs4 requests pandas\" in a cmd window to install the required packages!')
    print('\033[1;31m' + format_exc())
    exit(1)


# Install python 3, duh!
# Run the command below in a cmd window to install the needed packages, without the #, duh!
# pip install bs4 requests pandas
# Run the python file with the included batch file, DUH!

try:
    set_option('display.max_rows', 500)
    set_option('display.max_columns', 500)
    set_option('display.width', 1000)
    URL = "https://warframe.market/tools/ducats"

    soup = str(BeautifulSoup(get(URL).content, "html.parser")).replace('\n', '')
    items = search('"items": (\[(?:\[??[^\[]*?\]))', soup).group(0)[9:]
    previous_hour = search('"previous_hour": (\[(?:\[??[^\[]*?\]))', soup).group(0)[17:]
    previous_day = search('"previous_day": (\[(?:\[??[^\[]*?\]))', soup).group(0)[16:]

    '''
    with open('items.json', 'w') as f:
        print(items, file=f)
    with open('items_previous_hour.json', 'w') as f:
        print(previous_hour, file=f)
    with open('items_previous_day.json', 'w') as f:
        print(previous_day, file=f)
    '''

    df_items = read_json(items)
    df_items = df_items.drop(columns=['url_name', 'thumb'])
    df_items = df_items.reindex(columns=['id', 'item_name'])

    df_previous_day = read_json(previous_day)
    df_previous_day = df_previous_day.drop(columns=['id', 'plat_worth', 'position_change_month', 'position_change_week', 'position_change_day', 'ducats_per_platinum_wa', 'median', 'wa_price'])
    df_previous_day = df_previous_day.rename(columns={'item': 'id'})
    df_previous_day_merged = df_items.merge(df_previous_day, how='inner', on='id')
    df_previous_day_merged = df_previous_day_merged.drop(columns=['id'])
    df_previous_day_merged = df_previous_day_merged.reindex(columns=['item_name', 'datetime', 'ducats_per_platinum', 'ducats', 'volume'])
    df_previous_day_merged = df_previous_day_merged.sort_values(by='item_name')
    df_previous_day_merged.to_csv('Ducanator - Previous Day.csv', index=None, header=["Item Name", "Datestamp", "Ducats per Platinum", "Ducats", "Trade Volume"], quoting=QUOTE_ALL)

    df_previous_hour = read_json(previous_hour)
    df_previous_hour = df_previous_hour.drop(columns=['id', 'plat_worth', 'position_change_month', 'position_change_week', 'position_change_day', 'ducats_per_platinum_wa', 'median', 'wa_price'])
    df_previous_hour = df_previous_hour.rename(columns={'item': 'id'})
    df_previous_hour_merged = df_items.merge(df_previous_hour, how='inner', on='id')
    df_previous_hour_merged = df_previous_hour_merged.drop(columns=['id'])
    df_previous_hour_merged = df_previous_hour_merged.reindex(columns=['item_name', 'datetime', 'ducats_per_platinum', 'ducats', 'volume'])
    df_previous_hour_merged = df_previous_hour_merged.sort_values(by='item_name')
    df_previous_hour_merged.to_csv('Ducanator - Previous Hour.csv', index=None, header=["Item Name", "Datestamp", "Ducats per Platinum", "Ducats", "Trade Volume"], quoting=QUOTE_ALL)
    print('If you see this message things should have worked correctly. Remove the \"pause\" from the batch script to automatically close this window after use.')
except Exception:
    print('OOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The code monkeys at our headquarters are working VEWY HAWD to fix this!')
    print('\033[1;31m' + format_exc())
    exit(1)