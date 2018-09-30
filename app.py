import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from datetime import datetime

# #################################################
# # Database Setup
# #################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

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


# #################################################
# # Flask Routes
# #################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start_date&gt;<br/>"
        f"/api/v1.0/&lt;start_date&gt/&lt;end_date&gt"
    )


@app.route("/api/v1.0/precipitation")
def precip():
    """Return a list of one year of precipitation measurements"""
    # Establish date twelve months before last date in database
    results = session.query(func.max(Measurement.date).label("latestDate"),)
    res = results.one()
    latestD = res.latestDate
    latestDatetime = datetime.strptime(latestD, '%Y-%m-%d')
    twelveMonthsBack = latestDatetime - dt.timedelta(days=365)

    print(latestDatetime)

    # Perform a query to retrieve the data and precipitation

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= twelveMonthsBack).all()

    # Create a dictionary from the date and precipitation data
    precip_dict = {}
    for pobs in results:
        precip_dict[pobs.date] = pobs.prcp
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of one year of the climate measurement stations in the database"""
 
    results = session.query(Measurement.station).all()
    df = pd.DataFrame(results, columns=["Station"])
    df = df.groupby(by="Station").count()
    df = df.reset_index()
    stationList = df['Station'].tolist()
    
    return jsonify(stationList)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of one year of temperature observations"""
    # Establish date twelve months before last date in database
    results = session.query(func.max(Measurement.date).label("latestDate"),)
    res = results.one()
    latestD = res.latestDate
    latestDatetime = datetime.strptime(latestD, '%Y-%m-%d')
    twelveMonthsBack = latestDatetime - dt.timedelta(days=365)

    print(latestDatetime)

    # Perform a query to retrieve the data and precipitation

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= twelveMonthsBack).all()

    # Create a dictionary from the date and precipitation data
    tobs_dict = {}
    for tob in results:
        tobs_dict[tob.date] = tob.tobs
    return jsonify(tobs_dict)


@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temp_stats = list(np.ravel(results))

    return jsonify(temp_stats)

@app.route("/api/v1.0/<start_date>")
def calc_temps_start_only(start_date):
    """TMIN, TAVG, and TMAX for all datese after the start date.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d

        
    Returns:
        TMIN, TAVE, and TMAX
    """

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    temp_stats = list(np.ravel(results))

    return jsonify(temp_stats)

# @app.route("/api/v1.0/passengers")
# def passengers():
#     """Return a list of passenger data including the name, age, and sex of each passenger"""
#     # Query all passengers
#     results = session.query(Passenger).all()

#     # Create a dictionary from the row data and append to a list of all_passengers
#     all_passengers = []
#     for passenger in results:
#         passenger_dict = {}
#         passenger_dict["name"] = passenger.name
#         passenger_dict["age"] = passenger.age
#         passenger_dict["sex"] = passenger.sex
#         all_passengers.append(passenger_dict)

#     return jsonify(all_passengers)


if __name__ == '__main__':
    app.run(debug=True)
