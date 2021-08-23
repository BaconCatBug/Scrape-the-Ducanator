# Install python 3, duh!
# Run the command below in a cmd window to install the needed packages, without the #, duh!
# pip install bs4 requests pandas
# Run the python file with the included batch file, DUH!

try:
    # Error handling if something happens during script initialisation
    from csv import QUOTE_ALL  # Needed to export data to CSV
    from bs4 import BeautifulSoup  # Needed to parse the dynamic webpage of the Ducanator
    from requests import get  # Needed to get the webpage of the Ducanator
    from re import search  # Needed to find the json string to import into pandas
    from pandas import read_json  # Needed to convert the json string into a usable dataframe object for manipulation
    from traceback import format_exc  # Needed for more friendly error messages.
except ModuleNotFoundError:
    print('OOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The code monkeys at our headquarters are working VEWY HAWD to fix this!')
    print('You didn\'t install the packages like I told you to. Please run \"pip install bs4 requests pandas\" in a cmd window to install the required packages!')
    print('\033[1;31m' + format_exc())
    exit(1)

try:
    # Sets the URL to scrape, because hard-coding is bad
    URL = "https://warframe.market/tools/ducats"
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
    # Export the previous day data to a fully quoted CSV file
    df_previous_day_merged.to_csv('Ducanator - Previous Day.csv', index=None, header=["Item Name", "Datestamp", "Ducats per Platinum", "Ducats", "Weighted Average Price", "Ducats per Platinum\n(Weighted Average)", "Position Change:\nMonth", "Position Change:\nWeek", "Position Change:\nDay", "Trade Volume"], quoting=QUOTE_ALL)

    # Reads and sanitises the previous hour data into a pandas dataframe
    df_previous_hour = read_json(previous_hour)
    df_previous_hour = df_previous_hour.drop(columns=['id', 'plat_worth', 'median'])
    df_previous_hour = df_previous_hour.rename(columns={'item': 'id'})
    # Merges the item data and previous hour data on the id column, drops the redundant id column, then renames the column names for export
    df_previous_hour_merged = df_items.merge(df_previous_hour, how='inner', on='id')
    df_previous_hour_merged = df_previous_hour_merged.drop(columns=['id'])
    df_previous_hour_merged = df_previous_hour_merged.reindex(columns=['item_name', 'datetime', 'ducats_per_platinum', 'ducats', 'wa_price','ducats_per_platinum_wa', 'position_change_month', 'position_change_week', 'position_change_day', 'volume'])
    df_previous_hour_merged = df_previous_hour_merged.sort_values(by='item_name')
    # Export the previous hour data to a fully quoted CSV file
    df_previous_hour_merged.to_csv('Ducanator - Previous Hour.csv', index=None, header=["Item Name", "Datestamp", "Ducats per Platinum", "Ducats", "Weighted Average Price", "Ducats per Platinum\n(Weighted Average)", "Position Change:\nMonth", "Position Change:\nWeek", "Position Change:\nDay", "Trade Volume"], quoting=QUOTE_ALL)
    print('If you see this message things should have worked correctly. Remove the \"pause\" from the batch script to automatically close this window after use.')

except Exception:
    # Error handling if something happens during the main script
    print('OOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The code monkeys at our headquarters are working VEWY HAWD to fix this!')
    print('\033[1;31m' + format_exc())
    exit(1)
