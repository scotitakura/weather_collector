import sqlite3
from sqlite3 import Error
import requests
import time
import json
import datetime
import pytz
from pytz import timezone

d = datetime.datetime
database = r"C:\sqlite\db\weather.db"

central_time_adjustment = 10800
pacific_time_adjustment = 3600
eastern_time_adjustment = 14400

def create_connection(db_file):
    """
    Function connects to a SQLite database.
    
    Parameters
    ----------
    db_file : String
        File path of the database you would like to connect to.
        
    Return
    ------
    Connection obj or None.
    """
    
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
        
    return conn

def create_project(conn, project):
    """
    Insert new values into the weather_table.
    
    Parameters
    ----------
    conn : conn
    project : string, string, datetime, float
        weather_table values as city_name, state_name, datetime, and temperature
        
    Returns
    -------
    None
    """
    
    sql = '''
          INSERT INTO weather_table(city_name, state_name, datetime, temperature)
          VALUES(?,?,?,?)
          '''
    cur = conn.cursor()
    cur.execute(sql, project)
    conn.commit()
    return cur.lastrowid

class City:
    '''
    A class to represent a city.
    
    Attributes
    ----------
    city_name : String
        name of city, not space nor capital sensitive
    state_name : String
        name of state, not space nor capital sensitive
    time_adjustment : int
        timezone adjustment in seconds
    
    Methods
    -------
    add_data()
        Request from an api, write raw data to raw_weather.txt, and insert into weather_table.
    '''
    
    def __init__(self, city_name, state_name, time_adjustment):
        '''
        Constructs all the necessary attributes for the city object.
        
        Parameters
        ----------
        city_name : String
            name of city, not space nor capital sensitive
        state_name : String
            name of state, not space nor capital sensitive
        time_adjustment : int
            timezone adjustment in seconds
        '''
        
        self.city_name = city_name
        self.state_name = state_name
        self.time_adjustment = time_adjustment
        self.url = f"https://api.openweathermap.org/data/2.5/weather?q={self.city_name}&appid=e9d2f749c8d866a3f1aa783791b18cdb&units=imperial"
    
    def add_data(self):
        '''
        Request from an api, write raw data to raw_weather.txt, and insert into weather_table.
        
        Returns
        -------
        None
        '''
        
        try:
            self.request = requests.get(self.url).json()
        except Exception as e:
            print('Error with the API request.')
        else:
            with open('raw_weather.txt', 'a') as f:
                f.write(json.dumps(self.request))

            self.weather_data = (self.request['name'],
                                 self.state_name,
                                 d.fromtimestamp(self.request['dt'] + self.time_adjustment),
                                 self.request['main']['temp'])
            create_project(conn, self.weather_data)

timezones = {
    'central' : pytz.timezone('US/Central'),
    'pacific' : pytz.timezone('US/Pacific'),
    'eastern' : pytz.timezone('US/Eastern')
}

with open('city_data.txt', 'r') as f:
    city_data = f.read().splitlines()
print(city_data)
#print(timezones.get('central'))

cities_list = []
for line in city_data:
    city_name, state_name, timezone_string = line.split(',')
    print(city_name, state_name, timezone_string)
    print(city_name, state_name, timezones.get(timezone_string))
    #cities_list.append(City(city_name, state_name, timezones.get(timezone_string)))
#print(d.now().astimezone(pytz.timezone('US/Central')).timestamp())
#print(d.utcnow().timestamp() - d.now().astimezone(pytz.timezone('US/Eastern')).timestamp())
print(d.timestamp(d.now(tz=pytz.timezone('US/Eastern'))) - d.timestamp(d.now(tz=pytz.utc)))

def collect_data_every_five_minutes():
    while True:
        conn = create_connection(database)
        for city in cities_list:
            try:
                city.add_data()
            except Exception as e:
                print('Error with adding data.')
        time.sleep(300)

#if __name__ == "__main__":
    #collect_data_every_five_minutes()