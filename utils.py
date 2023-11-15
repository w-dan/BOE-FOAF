# API docs: https://boeapi.docs.apiary.io/#reference/documentos-boe/documentolimitoffsetformat/get?console=1
# GitHub API docs: https://github.com/BOE-API/BOE_API


# https://boe.es/diario_boe/xml.php?id=BOE-S-20231101


from constants import SPECIFIC_URL, ONTOLOGY_PATH
import requests
import os
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import json
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF


def download_boe_articles(start_date, end_date=None):
    base_url = "https://boe.es/diario_boe/xml.php?id=BOE-S-"
    current_date = start_date
    one_day = timedelta(days=1)

    # Destination directory for XML files
    destination_dir = "data/raw/"

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    if end_date is None:
        end_date = datetime.now()

    while current_date <= end_date:
        date_str = current_date.strftime("%Y%m%d")
        url = base_url + date_str
        response = requests.get(url)

        if response.status_code == 200:
            xml_data = response.content
            date_str = current_date.strftime("%Y%m%d")
            file_path = os.path.join(destination_dir, f"boe_articles_{date_str}.xml")

            with open(file_path, "wb") as f:
                f.write(xml_data)

            print(f"[✅] Downloaded: {file_path}")
        else:
            print(f"[❌] Error downloading: {url}")

        current_date += one_day


def get_xml_filenames(data_dir):
    xml_files = [
        os.path.splitext(f)[0] for f in os.listdir(data_dir) if f.endswith(".xml")
    ]
    return xml_files


def extract_info_from_xml(xml_file, json_output_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # god forgive me for the following 2 lines:
    if root.tag == "error":
        print(f"[❌] Error: {xml_file}")
        return

    items = []

    sumario_id = (
        root.find(".//sumario_nbo").get("id")
        if root.find(".//sumario_nbo") is not None
        else None
    )

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
                        "sumario_id": sumario_id,
                        "item_id": item_id,
                        "epigrafe": epigrafe_nombre,
                        "departamento": departamento_nombre,
                        "etq": departamento_etq,
                        "seccion": seccion_nombre,
                        "control": item_control,
                    }

                    items.append(item_info)

    summary = {}
    summary["sumario_id"] = sumario_id
    for field in [
        "anno",
        "fecha",
        "fechaInv",
        "fechaAnt",
        "fechaAntAnt",
        "fechaSig",
        "fechaPub",
    ]:
        element = root.find(f".//{field}")
        if element is not None:
            summary[field] = element.text

    with open(f"data/summary_{json_output_file}", "w") as json_file:
        print(f"[✅] Successfully created summary metadata JSON from {xml_file}")
        json.dump(summary, json_file, indent=4)

    with open(f"data/item_{json_output_file}", "a") as json_file:
        print(f"[✅] Successfully created item JSON from {xml_file}")
        json.dump(items, json_file, indent=4)

    return summary, items


def get_item_info(item_id):
    url = f"{SPECIFIC_URL}{item_id}"
    response = requests.get(url)

    print(url)

    if response.status_code == 200:
        xml_content = response.text
        root = ET.fromstring(xml_content)

        data = {
            "item_id": item.text
            if (item := root.find(".//identificador")) is not None
            else None,
            "origen_legislativo": origen_legislativo.text
            if (origen_legislativo := root.find(".//origen_legislativo")) is not None
            else None,
            "fecha_publicacion": fecha_publicacion.text
            if (fecha_publicacion := root.find(".//fecha_publicacion")) is not None
            else None,
            "diario_numero": diario_numero.text
            if (diario_numero := root.find(".//diario_numero")) is not None
            else None,
            "seccion": seccion.text
            if (seccion := root.find(".//seccion")) is not None
            else None,
            "articulos": [],
            "materias": [],
        }

        for texto in root.findall(".//texto/p"):
            if texto.text:
                data["articulos"].append(texto.text)

        data["articulos"] = "\n".join(data["articulos"])

        for materia in root.findall(".//materia"):
            data["materias"].append(materia.text)

        with open(f"data/articles/{item_id}.json", "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        return data
    else:
        return None


def get_ttl_from_ontology(summary_list, items_list, article_list):
    boe = Namespace("http://example.org/boe#")

    g = Graph()
    # g.parse(ONTOLOGY_PATH, format="turtle")

    # Iterar sobre la lista de sumarios y agregar tripletas al grafo
    for summary in summary_list:
        sumario_id = summary.get("sumario_id")

        # Agregar tipo Sumario
        g.add(
            (
                URIRef(f"http://localhost:3333/summary-{sumario_id}"),
                RDF.type,
                boe.Sumario,
            )
        )

        # Agregar propiedades del sumario
        for field, value in summary.items():
            if field != "sumario_id":
                property_uri = getattr(boe, field)
                if isinstance(value, str):
                    g.add(
                        (
                            URIRef(f"http://localhost:3333/summary-{sumario_id}"),
                            property_uri,
                            Literal(value),
                        )
                    )
                elif value:
                    g.add(
                        (
                            URIRef(f"http://localhost:3333/summary-{sumario_id}"),
                            property_uri,
                            URIRef(value),
                        )
                    )

    # Iterar sobre la lista de items y agregar tripletas al grafo
    for item_info in items_list:
        sumario_id = item_info.get("sumario_id")
        item_id = item_info.get("item_id")

        # Agregar tipo Item
        item_uri = URIRef(f"http://localhost:3333/item-{item_id}")
        g.add((item_uri, RDF.type, boe.Item))

        # Agregar relación con el Sumario
        sumario_uri = URIRef(f"http://localhost:3333/summary-{sumario_id}")
        g.add((sumario_uri, boe.contieneItem, item_uri))

        # Agregar propiedades del item
        for field, value in item_info.items():
            if field not in ["sumario_id", "item_id"]:
                property_uri = getattr(boe, field)
                if isinstance(value, str):
                    g.add(
                        (
                            URIRef(
                                f"http://localhost:3333/item-{item_id}"
                            ),
                            property_uri,
                            Literal(value),
                        )
                    )
                elif value:
                    g.add(
                        (
                            URIRef(
                                f"http://localhost:3333/item-{item_id}"
                            ),
                            property_uri,
                            URIRef(value),
                        )
                    )

    # Iterar sobre la lista de artículos y agregar tripletas al grafo
    for data in article_list:
        item_id = data.get("item_id")

        # Agregar tipo Articulo
        g.add(
            (URIRef(f"http://localhost:3333/article-{item_id}"), RDF.type, boe.Articulo)
        )

        # Agregar propiedades del artículo
        for field, value in data.items():
            if field != "item_id" and field != "articulos":
                property_uri = getattr(boe, field)
                if isinstance(value, str):
                    g.add(
                        (
                            URIRef(f"http://localhost:3333/article-{item_id}"),
                            property_uri,
                            Literal(value),
                        )
                    )
                elif value:
                    if "item_id" in data and data["item_id"]:
                        item_id_uri = URIRef(f"http://localhost:3333/item-{data['item_id']}")
                        # Agregar relación contieneItem
                        g.add((item_id_uri, boe.contieneArticulo, URIRef(f"http://localhost:3333/article-{item_id}")))

    # Serializar el grafo a formato Turtle
    ttl_data = g.serialize(format="turtle")

    with open("ontology/boe.ttl", "w", encoding="utf-8") as file:
        file.write(ttl_data)

    return ttl_data
