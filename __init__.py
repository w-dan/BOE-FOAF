from utils import (
    extract_info_from_xml,
    download_boe_articles,
    get_xml_filenames,
    get_item_info,
    get_ttl_from_ontology,
)
from datetime import datetime, timedelta
import os, glob

if __name__ == "__main__":
    summary_list = []
    items_list = []
    article_list = []

    """
        STEP 0
        Setup folders
    """
    folders = ["data/articles", "data/raw", "data/item_jsons", "data/summary_jsons"]

    clean = input("[🗑️] Do you want to clean directories previously? (yes|no): ")
    clean = clean == "yes"

    # create if they don't exist
    for folder in folders:
        folder_route = os.path.join("./", folder)
        if not os.path.exists(folder_route):
            os.makedirs(folder_route)
            print(f"[📁] Successfully created {folder} folder")
        if clean:
            files = glob.glob(os.path.join(folder, "*"))
            for f in files:
                os.remove(f)

    """
        STEP 1
        Get dates to retrieve bulletins
    """
    start_date = input("[📅] Enter the start date (YYYYMMDD): ")
    end_date_input = input(
        "[📅] Enter the end date (YYYYMMDD, or press Enter to use today): "
    )

    start_date = datetime.strptime(start_date, "%Y%m%d")

    if end_date_input:
        end_date = datetime.strptime(end_date_input, "%Y%m%d")
    else:
        end_date = None

    """
        STEP 2
        Download each bulletin into .xml files
    """
    download_boe_articles(start_date, end_date)

    xml_filenames = get_xml_filenames("data/raw")

    for filename in xml_filenames:
        summary, items = extract_info_from_xml(
            f"data/raw/{filename}.xml", f"jsons/{filename}.json"
        )
        summary_list.append(summary)
        items_list.extend(items)

    """
        STEP 3
        Get detailed information for each item in every bulletin
    """
    for item in items_list:
        item_id = item["item_id"]
        if article := get_item_info(item_id):
            article_list.append(article)

    """
        STEP 4
        Get ttl from extracted data based on the ontology
    """
    ttl = get_ttl_from_ontology(summary_list, items_list, article_list)
    print(ttl)
