try:
    # Error handling if something happens during script initialisation
    from csv import QUOTE_ALL  # Needed to export data to CSV
    from bs4 import BeautifulSoup  # Needed to parse the dynamic webpage of the Ducanator
    from requests import get  # Needed to get the webpage of the Ducanator
    from re import search  # Needed to find the json string to import into pandas
    from pandas import set_option, merge, to_numeric, DataFrame, read_json, read_html, ExcelWriter  # Needed to convert the json string into a usable dataframe object for manipulation
    from traceback import format_exc  # Needed for more friendly error messages.
    from openpyxl import load_workbook
    from numpy import arange
    from json import loads, dumps
    from re import compile
    from time import sleep, time

    set_option('display.max_columns', None)
    set_option('display.max_rows', None)
    set_option('display.expand_frame_repr', False)

except ModuleNotFoundError:
    print('OOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The code monkeys at our headquarters are working VEWY HAWD to fix this!')
    print('You didn\'t install the packages like I told you to. Please run \"pip install bs4 requests pandas\" in a cmd window to install the required packages!')
    print('\033[1;31m' + format_exc())
    exit(1)


def get_items(retry_attempts):
    url_items = 'https://api.warframe.market/v1/items'
    for x in range(0, retry_attempts):
        try:
            item_json = get(url_items).json()
            break
        except Exception:
            print('Item data download failed, retrying... ' + str(retry_attempts - x - 1) + ' attempts left...', end='\r')
    item_json = item_json['payload']['items']
    df_items_get_items = DataFrame(item_json)
    df_items_get_items['item_name'] = df_items_get_items['item_name'].replace(to_replace=r' \(.+\)', value='', regex=True)
    df_items_get_items = df_items_get_items.drop(columns=['thumb'])
    return df_items_get_items


def standing_to_plat_syndicates(url_syndicate_fragment, df_items_local, collapsible_regex, retry_attempts, res_per_syndicate, include_offline, order_type):
    try:
        print('Processing ' + url_syndicate_fragment.replace('_', ' ') + ' Items')
        workbook_name = 'StandingToPlat.xlsx'
        sheet_name_standing_to_plat_data = 'Standing To Plat Data'
        url_syndicate = 'https://warframe.fandom.com/wiki/' + url_syndicate_fragment
        soup = BeautifulSoup(get(url_syndicate).content, "html.parser").find('div', {'id': collapsible_regex}).find_all('span')
        item_list = []
        cost_list = []
        for count1, elem1 in enumerate(soup):
            if count1 % 2 == 0:
                cost_list.append(elem1.text)
            else:
                item_list.append(elem1.text)
        df_syndicate_item = DataFrame(item_list)
        df_cost = DataFrame(cost_list)
        df_concat = df_syndicate_item.join(df_cost, lsuffix='_item', rsuffix='_cost')
        df_concat = df_concat[~df_concat['0_cost'].str.contains('Credits')].reset_index(drop=True)
        df_concat['0_cost'] = df_concat['0_cost'].str.replace(',', '').astype(int)
        df_concat2 = merge(df_items_local, df_concat, left_on='item_name', right_on='0_item')
        list_buy = []
        list_prepandas = []
        for elem1 in df_concat2['url_name']:
            for x in range(0, retry_attempts):
                try:
                    sleep(0.1)
                    temp_json = get('https://api.warframe.market/v1/items/' + elem1 + '/orders').json()
                    break
                except Exception:
                    print('\rOrder data download failed, retrying... ' + str(retry_attempts - x - 1) + ' attempts left...', end='')
            for elem2 in temp_json['payload']['orders']:
                if not include_offline:
                    if elem2['order_type'] == order_type and elem2['user']['status'] == 'ingame':
                        try:
                            if elem2['mod_rank'] == 0:
                                list_buy.append(elem2['platinum'])
                        except:
                            list_buy.append(elem2['platinum'])
                else:
                    if elem2['order_type'] == 'buy':
                        try:
                            if elem2['mod_rank'] == 0:
                                list_buy.append(elem2['platinum'])
                        except Exception:
                            list_buy.append(elem2['platinum'])
            list_buy.sort(reverse=True)
            list_buy = list_buy[:1]
            try:
                list_buy_str = list_buy[0]
            except Exception:
                list_buy_str = 0
            list_prepandas.append([elem1, list_buy_str])
            list_buy = []
        df_plat = merge(DataFrame(list_prepandas), df_concat2, left_on=0, right_on='url_name').drop([0, 'url_name', 'id', '0_item'], axis=1)
        df_plat = df_plat[['item_name', 1, '0_cost']]
        df_plat['plat_per_rep'] = df_plat[1] / df_plat['0_cost']
        df_plat['rep_per_plat'] = round(df_plat['0_cost'] / df_plat[1], 2)
        df_plat = df_plat.sort_values(by='plat_per_rep', ascending=False).reset_index(drop=True).rename({1: 'plat_buy_order', '0_cost': 'rep_cost'}, axis=1)
        df_plat.insert(0, 'syndicate', url_syndicate_fragment.replace('_', ' '), allow_duplicates=True)
        print('')
        if url_syndicate_fragment == 'Cephalon_Simaris':
            return df_plat.head(res_per_syndicate+2)
        else:
            return df_plat.head(res_per_syndicate)
    except Exception:
        # Error handling if something happens during the main script
        print('OOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The code monkeys at our headquarters are working VEWY HAWD to fix this!')
        print('\033[1;31m' + format_exc())
        exit(1)


url_get_retrys = 10
results_per_syndicate = 2
include_offline_orders = True
list_wiki = [
    ['Cephalon_Simaris', 'mw-customcollapsible-Simaris'],
    ['Steel_Meridian', 'mw-customcollapsible-SteelMeridian'],
    ['Arbiters_of_Hexis', 'mw-customcollapsible-ArbitersofHexis'],
    ['Cephalon_Suda', 'mw-customcollapsible-CephalonSuda'],
    ['Red_Veil', 'mw-customcollapsible-RedVeil'],
    ['New_Loka', 'mw-customcollapsible-NewLoka'],
]

if __name__ == "__main__":
    df_items = get_items(url_get_retrys)
    df_all_syndicates_buy = DataFrame()
    df_all_syndicates_sell = DataFrame()
    for count, elem in enumerate(list_wiki):
        df_all_syndicates_buy = df_all_syndicates_buy.append(standing_to_plat_syndicates(elem[0], df_items, elem[1], url_get_retrys, results_per_syndicate, include_offline_orders, 'buy'))
        if count == 0:
            df_simaris_buy = df_all_syndicates_buy
    df_all_syndicates_buy = df_all_syndicates_buy.sort_values(by='plat_per_rep', ascending=False).reset_index(drop=True)
    print(df_simaris_buy)
    print('')
    print(df_all_syndicates_buy)
