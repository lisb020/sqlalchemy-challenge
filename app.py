import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Setup flask
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns a list of precipitation data for the last year of data."""
    # Create session link from python to DB
    session = Session(engine)

    # Get the last date
    # Calculate the date 1 year ago from the last data point in the database
    datefirst = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #convert string to datetime format
    date = dt.datetime.strptime(datefirst[0], '%Y-%m-%d')
    #get date 12 months previously
    back = pd.DateOffset(months=12)
    date = date - back
    
    # Query precipitation data for the last year of data
    results = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= str(date)).order_by(Measurement.date)
    
    session.close()

    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value
    precip_dict = {}
    for date, precip in results:
        precip_dict[date] = precip

    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Returns a list of the stations."""
    # Create session link from python to DB
    session = Session(engine)

    # Query for all the stations
    results = session.query(Station.station).all()
    session.close()

    #unravel into list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Returns a list of the temperature observations for the previous year for station ."""
    # Create session link from python to DB
    session = Session(engine)
    
    # Find all stations and order by how active
    stations_desc = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    
    # Get the most active station
    station_id = stations_desc[0][0]
    
    # Calculate the date 1 year ago from the last data point in the database
    datefirst = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #convert string to datetime format
    date = dt.datetime.strptime(datefirst[0], '%Y-%m-%d')
    #get date 12 months previously
    back = pd.DateOffset(months=12)
    date = date - back
    
    # Query the temperature for the last year of the most active station
    temp = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= str(date)).filter(Measurement.station == station_id).order_by(Measurement.date).all()

    session.close()
    
    all_temps = []
    for date, temps in temp:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = temps
        all_temps.append(temp_dict)
    
    return jsonify(all_temps)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80,debug=True)