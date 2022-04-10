import sqlite3
from sqlite3 import Error
import requests
import time
import json
import datetime
from time import perf_counter
import logging

d = datetime.datetime
database = r"C:\sqlite\db\weather.db"
file_logger = logging.getLogger(__name__)
file_logger.setLevel(logging.INFO)

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
            conn = create_connection(database)
            create_project(conn, self.weather_data)

timezones = {
    'central' : 10800,
    'pacific' : 3600,
    'eastern' : 14400
}

with open('city_data.txt', 'r') as f:
    city_data = f.read().splitlines()
        
cities_list = []
for line in city_data:
    city_name, state_name, timezone_string = line.split(',')
    cities_list.append(City(city_name, state_name, timezones.get(timezone_string)))

hourly_file = f'cities_{d.now().month}_{d.now().day}_{d.now().hour}.log'
file_handler = logging.FileHandler(hourly_file)
file_logger.addHandler(file_handler)

def collect_data_every_five_minutes():
    global hourly_file
    while True:
        
        if hourly_file != f'cities_{d.now().month}_{d.now().day}_{d.now().hour}.log':
            hourly_file = f'cities_{d.now().month}_{d.now().day}_{d.now().hour}.log'
            file_handler = logging.FileHandler(hourly_file)
            file_logger.addHandler(file_handler)

        for city in cities_list:
            try:
                start_time = perf_counter()
                city.add_data()
                end_time = perf_counter()
                total_time = end_time - start_time
                file_logger.info(f'City: {city.city_name}, State: {city.state_name}, Execution Time: {total_time}')
            except Exception as e:
                file_logger.error(d.now(), e)
        
        time.sleep(300)

if __name__ == "__main__":
    collect_data_every_five_minutes()