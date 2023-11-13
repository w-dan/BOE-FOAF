from utils import extract_info_from_xml, download_boe_articles, get_xml_filenames, get_item_info
from datetime import datetime, timedelta
from constants import ITEM_LIST
import os, shutil

if __name__ == "__main__":

    """
        STEP 0
        Setup folders
    """
    folders = ['articles', 'data', 'item_jsons', 'summary_jsons']

    # create if they don't exist
    for folder in folders:
        folder_route = os.path.join("./", folder)
        if not os.path.exists(folder_route):
            os.makedirs(folder_route)
            print(f'[📁] Successfully created {folders} folder')


    """
        STEP 1
        Get dates to retrieve bulletins
    """
    start_date = input("[📅] Enter the start date (YYYYMMDD): ")
    end_date_input = input("[📅] Enter the end date (YYYYMMDD, or press Enter to use today): ")

    start_date = datetime.strptime(start_date, '%Y%m%d')

    if end_date_input:
        end_date = datetime.strptime(end_date_input, '%Y%m%d')
    else:
        end_date = None


    """
        STEP 2
        Download each bulletin into .xml files
    """
    download_boe_articles(start_date, end_date)


    xml_filenames = get_xml_filenames('data')

    for filename in xml_filenames:
        ITEM_LIST.append(extract_info_from_xml(f'data/{filename}.xml', f'jsons/{filename}.json'))


    """
        STEP 3
        Get detailed information for each item in every bulletin
    """
    for i in ITEM_LIST:
        for item in i:
            item_id = item["id"]
            get_item_info(item_id)