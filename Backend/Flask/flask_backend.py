from datetime import datetime, timedelta
from operator import itemgetter
from statistics import mean
from turtle import title
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import json
from flask_cors import CORS
import urllib.parse


# DATABASE INFO
dbInf = open('jsonFiles/databaseInfo.json')
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

# FUNCTIE DE AFISARE A TUTUTOR ASSETurilor DIN DB
@app.route('/assets', methods=['GET'])
def assets():
    results = db.session.query(asset).all()
    output = []
    for asst in results:
        asset_info = {'name': asst.asset_name,'id' : asst.asset_id, 'used': asst.is_used}
        output.append(asset_info)
    return jsonify(output)


def interpolation(data,rate):
    valuesWithTime = []
    interpolation_rate = len(data)/rate
    if interpolation_rate < 1:
        interpolation_rate = 1
    values_for_interpolation = []
    i = 0
    for value in data:
        i +=1            
        if i > interpolation_rate:
                valuesWithTime.append([value[1],mean(values_for_interpolation)])
                i = 0
                values_for_interpolation = []
        else:
                values_for_interpolation.append(value[0])
    return sorted(valuesWithTime,key=itemgetter(0))

def date_separator(date_range):
    list  = date_range.split()
    startDate = datetime.strptime(list[0], '%m/%d/%Y')
    endDate = datetime.strptime(list[2], '%m/%d/%Y')
    return startDate,endDate

def getValues(asset_id,choice,start,end,interpolation_rate):
    results = db.session.query(data).filter_by(asset_id=asset_id).all()
    values = []
    valuesWithTime = []
    try:
        if not isinstance(start,datetime) and not isinstance(end,datetime):
            raise ValueError("Not datetime")
    except(ValueError,IndexError):
        return {"value":ValueError}
    if choice in ['average','maximum','minimum','all']:
        for value in results:
            if datetime.strptime(str(value.timestamp), '%Y-%m-%d %H:%M:%S') > start and datetime.strptime(str(value.timestamp), '%Y-%m-%d %H:%M:%S') < end:
                values.append(value.value)
                valuesWithTime.append([value.value,value.timestamp])
        if values:
            match choice:
                case "average":
                    return mean(values)
                case "maximum":
                    return max(values)
                case "minimum":
                    return min(values)
                case "all":
                    return interpolation(valuesWithTime,interpolation_rate)
        else:
            return f"no data starting from {start} to {end}"
    else:
        return "wrong choice"

#FUNCTIE CARE RETURNEAZA DATAPOINTurile UNUI ASSET IN FUNCTIE DE ID
@app.route('/datapoints', methods=['GET'])
def datapoints():
    asset_id = request.args.get('id')
    choice = request.args.get('choice')
    interpolation_rate = int(request.args.get('int_rate'))
    dateRange = urllib.parse.unquote(request.args.get('range'))
    date_list = date_separator(dateRange)
    values = getValues(asset_id,choice,date_list[0],date_list[1],interpolation_rate)
    return {"value":values}
    

if __name__ == '__main__':
    CORS(app)
    app.run(debug=True)