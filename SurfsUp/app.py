# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session from Python to the DB
Session = scoped_session(sessionmaker(bind=engine))
session = Session()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    return jsonify({
        "available_routes": [
            "/api/v1.0/precipitation",
            "/api/v1.0/stations",
            "/api/v1.0/tobs",
            "/api/v1.0/<start>",
            "/api/v1.0/<start>/<end>"
        ]
    })

@app.route('/api/v1.0/precipitation')
def precipitation():
    
    # Calculate the date one year from the last date in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - timedelta(days=365)

    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Convert query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations():
    
    # Query all stations
    results = session.query(Station.station).all()
    
    # Convert results to a list
    stations_list = [station[0] for station in results]
    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    
    # Specify the most active station
    most_active_station = 'USC00519281'

    # Calculate the date one year from the last date in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - timedelta(days=365)

    # Query temperature observations for the most active station over the last year
    results = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == most_active_station,
        Measurement.date >= one_year_ago
    ).all()

    # Convert results to list of dictionaries
    tobs_data = [{date: tobs} for date, tobs in results]
    return jsonify(tobs_data)

@app.route('/api/v1.0/<start>')
def start_date(start):
  
    # Query temperature stats from start date to the end of the dataset
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()

    # Convert to dictionary
    temp_data = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    return jsonify(temp_data)

@app.route('/api/v1.0/<start>/<end>')
def start_end_date(start, end):
   
    # Query temperature stats from start date to end date
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert to dictionary
    temp_data = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    return jsonify(temp_data)

if __name__ == '__main__':
    app.run(debug=True)