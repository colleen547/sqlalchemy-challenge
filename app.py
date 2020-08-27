# import dependencies 
import pandas as pd
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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )
#########################################################################################
#PRECIPITATION
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation for the prior year"""
    #    Query for the dates and precipitation observations from the last year.
    #       Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    #       Return the json representation of your dictionary.

    # Query precipitation 
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()

    session.close()

    # Convert list of tuples into normal list
    last_year = list(np.ravel(results))

    return jsonify(last_year)

#########################################################################################
#STATIONS
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of station data"""
    # Query all stations
    stations_query = session.query(Station.station).all()

    session.close()
    stations = list(np.ravel(stations_query))
       
    # Return the json representation of the dictionary
    return jsonify(stations)

########################################################################################
#TEMPERATURE OBSERVATIONS
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
    # Query for the dates and temperature observations from the last year.
    # Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
    # Return the json representation of your dictionary.

    session = Session(engine)

    #last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temp = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

    session.close()
    print(temp)

    # Create a list of dicts with `date` and `tobs` as the keys and values
    temp_totals = []
    for result in temp:
        row = {}
        row["date"] = result[0]
        row["tobs"] = result[1]
        temp_totals.append(row)

    return jsonify(temp_totals)

#########################################################################################
#TRIP START
@app.route("/api/v1.0/<start>")
def tripstart(start):

    session = Session(engine)

    # go back one year from start date and go to end of data for Min/Avg/Max temp   
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date - last_year
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    trip = list(np.ravel(trip_data))
    return jsonify(trip)
#########################################################################################
#TRIP END
@app.route("/api/v1.0/<start>/<end>")
def tripend(start,end):

    session = Session(engine)

    # go back one year from start/end date and get Min/Avg/Max temp     
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date - last_year
    end = end_date - last_year
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    trip = list(np.ravel(trip_data))
    return jsonify(trip)


########################################################################################

if __name__ == '__main__':
    app.run()