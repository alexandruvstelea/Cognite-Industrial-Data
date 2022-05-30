from datetime import datetime, timedelta
from queue import Empty
from statistics import mean
from turtle import title
from flask import Flask, jsonify, session, redirect, request
from flask_sqlalchemy import SQLAlchemy
import json
from sqlalchemy import null
from flask_cors import CORS

# DATABASE INFO
dbInf = open('Backend/databaseInfo.json')
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
    return {'home':'home'}

# FUNCTIE DE AFISARE A TUTUTOR ASSETurilor DIN DB
@app.route('/assets', methods=['GET'])
def assets():
    results = db.session.query(asset).all()
    output = []
    for asst in results:
        asset_info = {'name': asst.asset_name,'id' : asst.asset_id, 'used': asst.is_used}
        output.append(asset_info)
    return jsonify(output)


#FUNCTIE CARE RETURNEAZA DATAPOINTurile UNUI ASSET IN FUNCTIE DE ID
@app.route('/datapoints', methods=['GET'])
def datapoints():
    asset_id = request.args.get('id')
    results = db.session.query(data).filter_by(asset_id=asset_id).all()
    values = []
    valuesWithTime = []
    range = request.args.get('range')
    choice = request.args.get('choice')
    try:
        range = int(range)
    except:
        return {"wrong range":"wrong range"}
    if choice in ['average','maximum','minimum','all']:
        start = datetime.now() - timedelta(days = range)
        for asst in results:
            if (datetime.strptime(str(asst.timestamp), '%Y-%m-%d %H:%M:%S') > start):
                values.append(asst.value)
                valuesWithTime.append([asst.timestamp,asst.value])
        if values:
            match choice:
                case "average":
                    return {"value": mean(values)}
                case "maximum":
                    return {"value": max(values)}
                case "minimum":
                    return {"value": min(values)}
                case "all":
                    return {"value": valuesWithTime}
        else:
            return {f"value":f"no data starting from {start}"}
    else:
        return {"value":"wrong choice"}

if __name__ == '__main__':
    CORS(app)
    app.run(debug=True)