#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 12:58:03 2019

@author: hannah
"""

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

date_query = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
recent_date = date_query[0]
recent_date = dt.datetime.strptime(recent_date,'%Y-%m-%d').date()

past_date = recent_date - dt.timedelta(365)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start     Replace start with date in YYYY-MM-DD format <br/>"
        f"/api/v1.0/start/end     Replace start and end with dates in YYYY-MM-DD format"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return precipitation data"""
    
    session = Session(engine)
    
    precip_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > past_date).order_by(Measurement.date).all()

    precip_list = []
    for precip in precip_results:
        precip_dict = {}
        precip_dict['date'] = precip.date
        precip_dict['prcp'] = precip.prcp
        precip_list.append(precip_dict)

    return jsonify(precip_list)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    
    session = Session(engine)
    
    station_results = session.query(Station.station).all()
    
    all_stations = list(np.ravel(station_results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperature observations for the past year"""
    
    session = Session(engine)
    
    temp_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > past_date).order_by(Measurement.date).all()

    temp_list = []
    for temp in temp_results:
        temp_dict = {}
        temp_dict['date'] = temp.date
        temp_dict['tobs'] = temp.tobs
        temp_list.append(temp_dict)

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def temp_data_start(start):
    """Return `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date."""
    
    session = Session(engine)
    
    start_results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).first()
    
    start_dict = {'Min Temp': start_results[0], 'Avg Temp': start_results[1], 'Max Temp': start_results[2]}
    
    return jsonify(start_dict)

@app.route("/api/v1.0/<start>/<end>")
def temp_data_trip(start, end):
    """Return `TMIN`, `TAVG`, and `TMAX` for all dates bewteen the start and end date."""
    
    session = Session(engine)
    
    trip_results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).first()
    
    trip_dict = {'Min Temp': trip_results[0], 'Avg Temp': trip_results[1], 'Max Temp': trip_results[2]}
    
    return jsonify(trip_dict)

#Shutdown Flask if needed
from flask import request

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'
    
if __name__ == '__main__':
    app.run(debug=True)