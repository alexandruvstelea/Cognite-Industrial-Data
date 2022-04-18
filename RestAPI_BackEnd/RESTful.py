from statistics import mean
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import values
import json

#DATABASE INFO
dbInf = open('DataIngestion/databaseInfo.json')
db_info = json.load(dbInf)
hostname = db_info['hostname']
database = db_info['databaseName']
username = db_info['username']
pwd      = db_info['password']
port_id  = db_info['portID']
dbInf.close()

#CREAREA APLICATIEI FLASK SI SETUPul DBului
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{pwd}@{hostname}:{port_id}/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db  = SQLAlchemy(app)
asset = db.Table('assets_info', db.metadata, autoload = True, autoload_with = db.engine)
data = db.Table('datapoints_info',db.metadata,autoload = True, autoload_with = db.engine)

@app.route('/')
def index():
    return '' 

#FUNCTIE DE AFISARE A TUTUTOR ASSETurilor DIN DB
@app.route('/assets')
def get_assets():
    results = db.session.query(asset).all()
    output = []
    for ass in results:
        asset_name = {'name':ass.asset_name}
        output.append(asset_name)
    return {'assets':output}

#FUNCTIE DE CALCUL A MEDIEI VALORILOR UNUI ASSET IN FUNCTIE DE ID
@app.route('/average/<asset_id>')
def get_values_average(asset_id):
    results = db.session.query(data).filter_by(asset_id = asset_id).all()
    values = []
    for ass in results:
        values.append(ass.value)
    return {'average':mean(values)}