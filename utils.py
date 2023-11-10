# API docs: https://boeapi.docs.apiary.io/#reference/documentos-boe/documentolimitoffsetformat/get?console=1
# GitHub API docs: https://github.com/BOE-API/BOE_API


# https://boe.es/diario_boe/xml.php?id=BOE-S-20231101


from constants import BASE_URL, ITEM_LIST, SPECIFIC_URL
import requests
import os
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import json



def download_boe_articles(start_date, end_date=None):
    base_url = 'https://boe.es/diario_boe/xml.php?id=BOE-S-'
    current_date = start_date
    one_day = timedelta(days=1)

    # Destination directory for XML files
    destination_dir = 'data'

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    if end_date is None:
        end_date = datetime.now()

    while current_date <= end_date:
        date_str = current_date.strftime('%Y%m%d')
        url = base_url + date_str
        response = requests.get(url)

        if response.status_code == 200:
            xml_data = response.content
            date_str = current_date.strftime('%Y%m%d')
            file_path = os.path.join(destination_dir, f'boe_articles_{date_str}.xml')

            with open(file_path, 'wb') as f:
                f.write(xml_data)

            print(f'[✅] Downloaded: {file_path}')
        else:
            print(f'[❌] Error downloading: {url}')

        current_date += one_day

def get_xml_filenames(data_dir):
    xml_files = [os.path.splitext(f)[0] for f in os.listdir(data_dir) if f.endswith('.xml')]
    return xml_files


def extract_info_from_xml(xml_file, json_output_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # god forgive me for the following 2 lines:
    if root.tag == 'error':
        return

    result = []

    sumario_id = root.find(".//sumario_nbo").get("id") if root.find(".//sumario_nbo") is not None else None

    for seccion in root.findall(".//seccion"):
        for departamento in seccion.findall(".//departamento"):
            for epigrafe in departamento.findall(".//epigrafe"):
                for item in epigrafe.findall(".//item"):
                    epigrafe_nombre = epigrafe.get("nombre")
                    departamento_nombre = departamento.get("nombre")
                    departamento_etq = departamento.get("etq")
                    seccion_nombre = seccion.get("nombre")
                    item_id = item.get("id")
                    item_control = item.get("control")

                    item_info = {
                        "epigrafe": epigrafe_nombre,
                        "departamento": departamento_nombre,
                        "etq": departamento_etq,
                        "seccion": seccion_nombre,
                        "id": item_id,
                        "control": item_control,
                        'sumario_id': sumario_id
                    }

                    result.append(item_info)

    info_dict = {}
    for field in ["anno", "fecha", "fechaInv", "fechaAnt", "fechaAntAnt", "fechaSig", "fechaPub"]:
        element = root.find(f".//{field}")
        if element is not None:
            info_dict[field] = element.text

    if result:
        info_dict["items"] = result
        ITEM_LIST.append(item_id)

    with open(json_output_file, 'w') as json_file:
        print(f'[✅] Successfully created JSON from {xml_file}')
        json.dump(info_dict, json_file, indent=4)



def get_item_info(item_id):
    url = f"{SPECIFIC_URL}{item_id}"
    response = requests.get(url)

    print(url)

    if response.status_code == 200:
        xml_content = response.text
        root = ET.fromstring(xml_content)

        data = {
            "identificador": root.find(".//identificador").text if root.find(".//identificador") is not None else None,
            "origen_legislativo": root.find(".//origen_legislativo").text if root.find(".//origen_legislativo") is not None else None,
            "fecha_publicacion": root.find(".//fecha_publicacion").text if root.find(".//fecha_publicacion") is not None else None,
            "diario_numero": root.find(".//diario_numero").text if root.find(".//diario_numero") is not None else None,
            "seccion": root.find(".//seccion").text if root.find(".//seccion") is not None else None,
            "articulos": [],
            "materias": []
        }

        for texto in root.findall(".//texto/p"):
            data["articulos"].append(texto.text)

        for materia in root.findall(".//materia"):
            data["materias"].append(materia.text)

        with open(f"{item_id}.json", "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        return data
    else:
        return None
