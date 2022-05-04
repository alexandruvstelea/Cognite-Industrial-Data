from datetime import datetime, timedelta
from queue import Empty
from statistics import mean
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import json

# DATABASE INFO
dbInf = open('DataIngestion/databaseInfo.json')
db_info = json.load(dbInf)
hostname = db_info['hostname']
database = db_info['databaseName']
username = db_info['username']
pwd = db_info['password']
port_id = db_info['portID']
dbInf.close()

# CREAREA APLICATIEI FLASK SI SETUPul DBului
app = Flask(__name__, template_folder='../FrontEnd/templates',static_folder='../static')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{pwd}@{hostname}:{port_id}/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
asset = db.Table('assets_info', db.metadata, autoload=True, autoload_with=db.engine)
data = db.Table('datapoints_info', db.metadata, autoload=True, autoload_with=db.engine)


@app.route('/home')
def index():
    return render_template('home.html')

# FUNCTIE DE AFISARE A TUTUTOR ASSETurilor DIN DB
@app.route('/assets')
def get_assets():
    results = db.session.query(asset).all()
    output = []
    for asst in results:
        asset_info = {'name': asst.asset_name,'id' : asst.asset_id, 'used': asst.is_used}
        output.append(asset_info)
    return jsonify(output)

# FUNCTIE DE CALCUL A MEDIEI VALORILOR UNUI ASSET IN FUNCTIE DE ID
@app.route('/average/<asset_id>/<int:interval>')
def get_values_average(asset_id,interval):
    start=datetime.now()-timedelta(days=int(interval))
    results = db.session.query(data).filter_by(asset_id = asset_id).all()
    values = []
    for asst in results:
        if (datetime.strptime(str(asst.timestamp), '%Y-%m-%d %H:%M:%S') > start):
            values.append(asst.value)
    if not values:
        return {'average':'No data'}
    else:
        return {'average':mean(values)}

# FUNCTIE DE CALCUL A MAXIMULUI VALORILOR UNUI ASSET IN FUNCTIE DE ID
@app.route('/maximum/<asset_id>/<int:interval>')
def get_values_maximum(asset_id,interval):
    start=datetime.now()-timedelta(days=int(interval))
    results = db.session.query(data).filter_by(asset_id = asset_id).max()
    values = []
    for asst in results:
        if (datetime.strptime(str(asst.timestamp), '%Y-%m-%d %H:%M:%S') > start):
            values.append(asst.value)
    if not values:
        return {'maximum':'No data'}
    else:
        return {'maximum':max(values)}

#FUNCTIE CARE RETURNEAZA DATAPOINTurile UNUI ASSET IN FUNCTIE DE ID
@app.route('/datapoints/<asset_id>')
def get_values(asset_id):
    results = db.session.query(data).filter_by(asset_id=asset_id).all()
    values = []
    for asst in results:
        values.append({'value':asst.value,'timestamp':str(asst.timestamp)})
    return jsonify(values)

if __name__ == '__main__':
    app.run(debug=True)
