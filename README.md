# BOE-FOAF

Repository for GESTBD hackathon. The initial idea of this project is to fetch or scrap data from [BOE page](https://www.boe.es/index.php) to create a tool with which you can use for thses things:

1. Analysis of changes and updates in laws and regulations.
2. Identification of legal trends from historical BOE data.
3. Development of tools for the efficient management and search of legal information.

## Workflow

The following workflow represents the usage of this application. It is devided on three main blocks, the first one is the gathering of information, with this we generate the data on json format to use [OpenRefine](https://openrefine.org/) software in order to connect via Ontologies and thus combine with information from other pages like [DBpedia](https://es.dbpedia.org/) in order to gather more information. The last step is to expose this information to a better search for the user.

![Separate Workflows](./docs/workflow.png)

### Gather information

The basic part of this step is the gathering of data from [BOE page](https://www.boe.es/index.php). To fulfill this firstly a connection is created to the web via this [URL](https://boe.es/diario_boe/xml.php?id=BOE-S). Once connected the next step is to download the bulletin which contains information about the resolutions of the *DD/MM/YYYY*. Once the bulletin is downloaded, all the metadata and other information about it is recollected and expressed on several jsons:

- JSON about *"Sumarios"*. *Sumarios* is the information about *bulletins*. The *Sumarios* have the following information:
  - Metadata
  - SumarioID
- JSON about *"Items"*. Each of this *"Items"* has the resolutions of the different tematics.
  - Metadata
  - SummarioID
  - ItemID
- JSON about *"Articulos"*. Contains information about the article which is published.
  - Information about article
  - ItemID

![Data recollection part](./docs/workflow_scrapping.png)

### Ontology

In order to create a knowledge graph where any information can be gathered, about any specific data. [OpenRefine](https://openrefine.org/) helps with this task, even though in this case it is used manually, the process is very simple. Once the json files have been uploaded, the first step is to select the column which we want to gather more information.

%%%%%%%%%%%%%%%%%%%%%%%% TODO %%%%%%%%%%%%%%%%%%%%%%%
% Falta la parte de sincronizar la info con DBPedia %
% Y luego continuar con el export a ttl             %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

![Ontology part](./docs/workflow_ontology.png)

### Elastik

Elastiksearch is a **NoSQL** technology that alows to store, search and analyze data. The way data is inserted is via **indexation**, this engine is made based on Apache. It can be scale out horizontally or vertically.

%% TODO : Cómo se va a indexar

The first step is to connect to ElastikSearch, then index the data so that it can be searched.

![Elastik search part](./docs/workflow_elastik.png)
