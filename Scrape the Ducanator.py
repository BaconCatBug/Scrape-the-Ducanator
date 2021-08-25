# Install python 3, duh!
# Run the command below in a cmd window to install the needed packages, without the #, duh!
# pip install bs4 requests pandas openpyxl lxml html5lib
# Run the python file with the included batch file, DUH!

try:
    # Error handling if something happens during script initialisation
    from csv import QUOTE_ALL  # Needed to export data to CSV
    from bs4 import BeautifulSoup  # Needed to parse the dynamic webpage of the Ducanator
    from requests import get  # Needed to get the webpage of the Ducanator
    from re import search  # Needed to find the json string to import into pandas
    from pandas import DataFrame, read_json, read_html, ExcelWriter  # Needed to convert the json string into a usable dataframe object for manipulation
    from traceback import format_exc  # Needed for more friendly error messages.
    from openpyxl import load_workbook
    from numpy import arange

except ModuleNotFoundError:
    print('OOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The code monkeys at our headquarters are working VEWY HAWD to fix this!')
    print('You didn\'t install the packages like I told you to. Please run \"pip install bs4 requests pandas\" in a cmd window to install the required packages!')
    print('\033[1;31m' + format_exc())
    exit(1)

try:
    # Sets the URL to scrape, because hard-coding is bad
    URL = "https://warframe.market/tools/ducats"
    sheet_name = 'Prime-Relic_Data.xlsx'
    # Scrapes the given URL
    soup = str(BeautifulSoup(get(URL).content, "html.parser")).replace('\n', '')
    # Finds the needed json string for item data, previous hour data, and previous day data.
    # Slices off the first bit to make a valid json string for pandas later
    items = search('"items": (\[(?:\[??[^\[]*?\]))', soup).group(0)[9:]
    previous_hour = search('"previous_hour": (\[(?:\[??[^\[]*?\]))', soup).group(0)[17:]
    previous_day = search('"previous_day": (\[(?:\[??[^\[]*?\]))', soup).group(0)[16:]

    # Reads and sanitises the item data into a pandas dataframe
    df_items = read_json(items)
    df_items = df_items.drop(columns=['url_name', 'thumb'])
    df_items = df_items.reindex(columns=['id', 'item_name'])

    # Reads and sanitises the previous day data into a pandas dataframe
    df_previous_day = read_json(previous_day)
    df_previous_day = df_previous_day.drop(columns=['id', 'plat_worth', 'median'])
    df_previous_day = df_previous_day.rename(columns={'item': 'id'})
    # Merges the item data and previous day data on the id column, drops the redundant id column, then renames the column names for export
    df_previous_day_merged = df_items.merge(df_previous_day, how='inner', on='id')
    df_previous_day_merged = df_previous_day_merged.drop(columns=['id'])
    df_previous_day_merged = df_previous_day_merged.reindex(columns=['item_name', 'datetime', 'ducats_per_platinum', 'ducats', 'wa_price','ducats_per_platinum_wa', 'position_change_month', 'position_change_week', 'position_change_day', 'volume'])
    df_previous_day_merged = df_previous_day_merged.sort_values(by='item_name')
    df_previous_day_merged['datetime'] = df_previous_day_merged['datetime'].astype(str).str[:-6]

    # Reads and sanitises the previous hour data into a pandas dataframe
    df_previous_hour = read_json(previous_hour)
    df_previous_hour = df_previous_hour.drop(columns=['id', 'plat_worth', 'median'])
    df_previous_hour = df_previous_hour.rename(columns={'item': 'id'})
    # Merges the item data and previous hour data on the id column, drops the redundant id column, then renames the column names for export
    df_previous_hour_merged = df_items.merge(df_previous_hour, how='inner', on='id')
    df_previous_hour_merged = df_previous_hour_merged.drop(columns=['id'])
    df_previous_hour_merged = df_previous_hour_merged.reindex(columns=['item_name', 'datetime', 'ducats_per_platinum', 'ducats', 'wa_price','ducats_per_platinum_wa', 'position_change_month', 'position_change_week', 'position_change_day', 'volume'])
    df_previous_hour_merged = df_previous_hour_merged.sort_values(by='item_name')
    df_previous_hour_merged['datetime'] = df_previous_hour_merged['datetime'].astype(str).str[:-6]
    df_previous_hour_merged = df_previous_hour_merged.reset_index(drop=True)

    # Fuck Comments
    URL = "https://n8k6e2y6.ssl.hwcdn.net/repos/hnfvc0o3jnfvc873njb03enrf56.html"
    # Scrapes the given URL
    soup = str(BeautifulSoup(get(URL).content, "html.parser")).replace('\n', '')
    parsed_relics = search('<h3 id="relicRewards">Relics:</h3><table>.*?</table>', soup).group(0)[34:].replace('th>', 'td>').replace(r'<th colspan="2">', r'<td>').replace('X Kuva', 'x Kuva')
    df_parsed_relics = read_html(parsed_relics, header=None)
    df_parsed_relics = df_parsed_relics[0].replace(to_replace=r'.+\((.+)\%\)', value=r'\1', regex=True)
    df_parsed_relics[1] = df_parsed_relics[1].astype(float)
    df_parsed_relics = df_parsed_relics.dropna(how='all').fillna(999)
    groups = df_parsed_relics.groupby(arange(len(df_parsed_relics.index)) // 7, sort=False).apply(lambda x: x.sort_values(by=1, ascending=False))
    groups[1] = ' (' + groups[1].astype(str) + '%)'
    groups = groups[0] + groups[1]
    groups = groups.replace(to_replace=r'\(999.0\%\)', value=r'', regex=True)
    templist = []
    templist2 = []
    for count, value in enumerate(groups):
        if count % 7 == 0 and count != 0:
            templist2.append(templist)
            templist = []
        templist.append(value)

    df_even_more_parsed_relics = DataFrame(templist2, columns=['Relic_Name', 'C1', 'C2', 'C3', 'U1', 'U2', 'Rare'])

    # Export data
    with ExcelWriter(sheet_name, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        df_previous_day_merged.to_excel(writer, sheet_name="Day")
        df_previous_hour_merged.to_excel(writer, sheet_name="Hour")
        df_even_more_parsed_relics.to_excel(writer, sheet_name="Relics")
    book = load_workbook(sheet_name)
    sheet = book['Day']
    sheet.delete_cols(1,1)
    sheet = book['Hour']
    sheet.delete_cols(1,1)
    sheet = book['Relics']
    sheet.delete_cols(1,1)
    book.save(sheet_name)
    print('If you see this message things should have worked correctly. Remove the \"pause\" from the batch script to automatically close this window after use.')

except Exception:
    # Error handling if something happens during the main script
    print('OOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The code monkeys at our headquarters are working VEWY HAWD to fix this!')
    print('\033[1;31m' + format_exc())
    exit(1)
