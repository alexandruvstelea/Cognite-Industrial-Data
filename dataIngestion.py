from datetime import datetime, timedelta
from cognite.client import CogniteClient
import time
import psycopg2
import schedule
import json

#DATABASE INFO AND CONNECTION
dbInf = open('databaseInfo.json')
db_info = json.load(dbInf)
hostname = db_info['hostname']
database = db_info['databaseName']
username = db_info['username']
pwd      = db_info['password']
port_id  = db_info['portID']
dbInf.close()

#AUTENTIFICARE COGNITE
cognInf = open('cogniteClientInfo.json')
client_info = json.load(cognInf)
api_key = client_info['APIKey']
client_name = client_info['clientName']
project_name = client_info['projectName']
cognInf.close()
c = CogniteClient(api_key=api_key, client_name=client_name,project=project_name)


#FUNCTIE DE ADAUGAT ASSET-urile in DB(NUMELE ASSET-ului, ASSET ID-ul SI STAREA DE UTILIZARE)
def update_assets_info(assets_list):
    cursor = None
    connection = None
    try:
        connection = psycopg2.connect(host=hostname,dbname=database,user=username,password=pwd,port=port_id)
        cursor = connection.cursor()
        assets_to_add = []
        for asset in assets_list:
            if int(assets_list[f'{asset}'].get('assetID')) not in get_assets_in_db("all"):
                assets_to_add.append([assets_list[f'{asset}'].get('assetID'),assets_list[f'{asset}'].get('assetName'),assets_list[f'{asset}'].get('isUsed')])
        insert_script = 'INSERT INTO assets_info (asset_id,asset_name,is_used) VALUES (%s,%s,%s)'
        for asset in assets_to_add:
            insert_data = (asset[0],asset[1],asset[2])
            cursor.execute(insert_script,insert_data)
        connection.commit()
    except Exception as error:
        print(error)
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
        print("UPDATED ASSETS INFO")

#FUNCTIE CARE RETURNEAZA O LISTA CU TOATE ID-urile ASSET-urilor DIN TABELA assets_info
def get_assets_in_db(type):
    if type == "only_used_assets":
        script = 'SELECT asset_id FROM assets_info WHERE is_used=true'
    else:
        script = 'SELECT asset_id FROM assets_info'
    cursor = None
    connection = None
    try:
        connection = psycopg2.connect(host=hostname,dbname=database,user=username,password=pwd,port=port_id)
        cursor = connection.cursor()
        cursor.execute(script)
        assets_in_db = [int(id[0]) for id in cursor.fetchall() ]
    except Exception as error:
        print(error)
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
        return assets_in_db

#FUNCTIE DE EXTRAGERE IN FORMAT DE LISTA A VALORILOR DIN COGNITEDB IMPREUNA CU ORA, DATA SI ASSET ID-ul
def get_datapoints_list_format(datapoints_id,asset_id):
    datapoints = c.datapoints.retrieve(id=datapoints_id,start=datetime.now()-timedelta(days=8),end=datetime.now())
    data_list = []
    i=0
    for data in datapoints:
        i+=1
        data_to_dump = []
        data_to_dump.append(time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(data.timestamp/1000)))
        data_to_dump.append(data.value)
        data_to_dump.append(asset_id)
        data_list.append(data_to_dump)
        if i==5:
            break
    print("GOT NEW DATA LIST")
    return data_list



#FUNCTIE DE ADAUGARE A DATELOR IN DB
def transfer_datapoints_to_db(assets_data):
    cursor = None
    connection = None
    try:
        connection = psycopg2.connect(host=hostname,dbname=database,user=username,password=pwd,port=port_id)
        cursor = connection.cursor()
        delete_all_data = 'DELETE FROM datapoints_info'
        reset_auto_increment = 'ALTER SEQUENCE datapoints_info_id_seq RESTART WITH 1'
        insert_script = 'INSERT INTO datapoints_info (timestamp,value,asset_id) VALUES (%s,%s,%s)'
        cursor.execute(delete_all_data)
        cursor.execute(reset_auto_increment)
        for data in assets_data:
            for individual_data in data:
                insert_data = (individual_data[0],individual_data[1],individual_data[2])
                cursor.execute(insert_script,insert_data)
        connection.commit()
    except Exception as error:
        print(error)
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
        print("ADDED NEW DATA TO DB")

#FUNCTIE PRINCIPALA - APELEAZA FUNCTIILE NECESARE PENTRU UPDATE-ul DB-ului
def add_new_datapoints_to_db():
    print("\nStarted script")
    astInf = open('assets.json')
    assets_list = json.load(astInf)
    update_assets_info(assets_list)
    active_assets_id = get_assets_in_db("only_used_assets")
    assets_data = []
    for asset in assets_list:
        if int(assets_list[f'{asset}'].get('assetID')) in active_assets_id:
            assets_data.append(get_datapoints_list_format(int(assets_list[f'{asset}'].get('datapointsID')),int(assets_list[f'{asset}'].get('assetID'))))
    transfer_datapoints_to_db(assets_data)
    print("FINISHED SCRIPT")


#SCHEDULER CARE APELEAZA FUNCTIA PRINCIPALA LA FIECARE 30 DE SECUNDE
schedule.every(30).seconds.do(add_new_datapoints_to_db)
while True:
    schedule.run_pending()
    time.sleep(1)