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
    from pandas import read_csv, set_option, concat, DataFrame, read_json, read_html, ExcelWriter  # Needed to convert the json string into a usable dataframe object for manipulation
    from traceback import format_exc  # Needed for more friendly error messages.
    from openpyxl import load_workbook
    from numpy import arange
    from os import path
except ModuleNotFoundError:
    print('OOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The code monkeys at our headquarters are working VEWY HAWD to fix this!')
    print('You didn\'t install the packages like I told you to. Please run \"pip install bs4 requests pandas\" in a cmd window to install the required packages!')
    print('\033[1;31m' + format_exc())
    exit(1)

try:
    #User Variables
    workbook_name = 'Prime_Relic_Data.xlsx'
    csv_name = 'Prime-Relic Data.csv'
    sheet_name_day = 'Day'
    sheet_name_hour = 'Hour'
    sheet_name_relic = 'Relic_Data'
    retry_attempts = 10
    # Sets the URL to scrape, because hard-coding is bad
    print('Downloading Ducat Data')
    url_ducats = "https://warframe.market/tools/ducats"
    # Scrapes the given URL
    soup = str(BeautifulSoup(get(url_ducats).content, "html.parser")).replace('\n', '')
    print('Ducat Data Downloaded')
    print('Processing Ducat Data')
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

    print('Ducat Data Processed')
    # Fuck Comments
    print('Downloading Relic Data')
    url_relics = "https://n8k6e2y6.ssl.hwcdn.net/repos/hnfvc0o3jnfvc873njb03enrf56.html"
    relic_data_txt_name = 'RelicData.txt'

    if path.isfile(relic_data_txt_name):
        with open(relic_data_txt_name) as f:
            soup = str(f.readlines())
        print("Loaded Local Relic Data")
    else:
        print("Loading Remote Item Data")

        for x in range(0, retry_attempts):
            try:
                soup = str(BeautifulSoup(get(url_relics).content, "html.parser")).replace('\n', '')
                print('Saving Local Data')
                with open(relic_data_txt_name, 'w') as f:
                    f.write(soup)
                break
            except Exception:
                print('Relic data download failed, retrying... ' + str(retry_attempts - x - 1) + ' attempts left...', end='\r')


    print('Relic Data Downloaded')
    print('Processing Relic Data')
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
    df_relic_class = df_even_more_parsed_relics['Relic_Name'].str.split().str[0]
    df_even_more_parsed_relics.insert(len(df_even_more_parsed_relics.columns), 'Class', df_relic_class, allow_duplicates=True)
    df_even_more_parsed_relics.insert(len(df_even_more_parsed_relics.columns), 'Type', df_even_more_parsed_relics['Relic_Name'].str.upper().str.split().str[1], allow_duplicates=True)
    df_even_more_parsed_relics.insert(len(df_even_more_parsed_relics.columns), 'Refinement', df_even_more_parsed_relics['Relic_Name'].str.split().str[3].replace(to_replace=r'[\(\)]', value=r'', regex=True), allow_duplicates=True)
    dict = {'Exceptional':'','Flawless':'','Radiant':''}
    df_even_more_parsed_relics.insert(len(df_even_more_parsed_relics.columns), 'C1_Raw', df_even_more_parsed_relics['C1'].replace(to_replace=r' \(.+\)',value='',regex=True))
    df_even_more_parsed_relics.insert(len(df_even_more_parsed_relics.columns), 'C2_Raw', df_even_more_parsed_relics['C2'].replace(to_replace=r' \(.+\)',value='',regex=True))
    df_even_more_parsed_relics.insert(len(df_even_more_parsed_relics.columns), 'C3_Raw', df_even_more_parsed_relics['C3'].replace(to_replace=r' \(.+\)',value='',regex=True))
    df_even_more_parsed_relics.insert(len(df_even_more_parsed_relics.columns), 'U1_Raw', df_even_more_parsed_relics['U1'].replace(to_replace=r' \(.+\)',value='',regex=True))
    df_even_more_parsed_relics.insert(len(df_even_more_parsed_relics.columns), 'U2_Raw', df_even_more_parsed_relics['U2'].replace(to_replace=r' \(.+\)',value='',regex=True))
    df_even_more_parsed_relics.insert(len(df_even_more_parsed_relics.columns), 'Rare_Raw', df_even_more_parsed_relics['Rare'].replace(to_replace=r' \(.+\)',value='',regex=True))
    df_even_more_parsed_relics.insert(len(df_even_more_parsed_relics.columns), 'C1_Odds', df_even_more_parsed_relics['C1'].replace(to_replace=r'.+\((.+)\%\)',value=r'\1',regex=True).astype(float))
    df_even_more_parsed_relics.insert(len(df_even_more_parsed_relics.columns), 'C2_Odds', df_even_more_parsed_relics['C2'].replace(to_replace=r'.+\((.+)\%\)',value=r'\1',regex=True).astype(float))
    df_even_more_parsed_relics.insert(len(df_even_more_parsed_relics.columns), 'C3_Odds', df_even_more_parsed_relics['C3'].replace(to_replace=r'.+\((.+)\%\)',value=r'\1',regex=True).astype(float))
    df_even_more_parsed_relics.insert(len(df_even_more_parsed_relics.columns), 'U1_Odds', df_even_more_parsed_relics['U1'].replace(to_replace=r'.+\((.+)\%\)',value=r'\1',regex=True).astype(float))
    df_even_more_parsed_relics.insert(len(df_even_more_parsed_relics.columns), 'U2_Odds', df_even_more_parsed_relics['U2'].replace(to_replace=r'.+\((.+)\%\)',value=r'\1',regex=True).astype(float))
    df_even_more_parsed_relics.insert(len(df_even_more_parsed_relics.columns), 'Rare_Odds', df_even_more_parsed_relics['Rare'].replace(to_replace=r'.+\((.+)\%\)',value=r'\1',regex=True).astype(float))
    df_even_more_parsed_relics = df_even_more_parsed_relics.replace(to_replace=r'Systems Blueprint',value=r'Systems', regex=True)
    df_even_more_parsed_relics = df_even_more_parsed_relics.replace(to_replace=r'Neuroptics Blueprint',value=r'Systems', regex=True)
    df_even_more_parsed_relics = df_even_more_parsed_relics.replace(to_replace=r'Chassis Blueprint',value=r'Systems', regex=True)
    #print(df_even_more_parsed_relics.head(5))
    #df_even_more_parsed_relics['Relic_Name'] = df_even_more_parsed_relics['Relic_Name'].str.split(n=1).str[1]
    #df_axi = df_even_more_parsed_relics[df_even_more_parsed_relics['Relic_Class']=='Axi'].reset_index(drop=True)
    #df_lith = df_even_more_parsed_relics[df_even_more_parsed_relics['Relic_Class']=='Lith'].reset_index(drop=True)
    #df_meso = df_even_more_parsed_relics[df_even_more_parsed_relics['Relic_Class']=='Meso'].reset_index(drop=True)
    #df_neo = df_even_more_parsed_relics[df_even_more_parsed_relics['Relic_Class']=='Neo'].reset_index(drop=True)
    #df_requiem = df_even_more_parsed_relics[df_even_more_parsed_relics['Relic_Class']=='Requiem'].reset_index(drop=True)
    #df_final_export_relic = concat([df_axi,df_lith,df_meso,df_neo,df_requiem], axis=1, ignore_index=True)
    #print(df_even_more_parsed_relics)
    print('Relic Data Processed')

    # Export data
    print('Exporting Worksheet')
    df_even_more_parsed_relics.to_csv(csv_name, index=None, quoting=QUOTE_ALL)
    df_previous_day_merged.to_csv('DayPrices.csv', index=None, quoting=QUOTE_ALL)
    with ExcelWriter(workbook_name, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        df_previous_day_merged.to_excel(writer, sheet_name=sheet_name_day)
        df_previous_hour_merged.to_excel(writer, sheet_name=sheet_name_hour)
        df_even_more_parsed_relics.to_excel(writer, sheet_name=sheet_name_relic)
        #df_final_export_relic.to_excel(writer, sheet_name=sheet_name_relic)
    book = load_workbook(workbook_name)
    sheet = book[sheet_name_day]
    sheet.delete_cols(1,1)
    sheet = book[sheet_name_hour]
    sheet.delete_cols(1,1)
    sheet = book[sheet_name_relic]
    sheet.delete_cols(1,1)
    book.save(workbook_name)
    print('If you see this message, things should have worked correctly. Remove the \"pause\" from the batch script to automatically close this window after use.')

except Exception:
    # Error handling if something happens during the main script
    print('OOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The code monkeys at our headquarters are working VEWY HAWD to fix this!')
    print('\033[1;31m' + format_exc())
    exit(1)
