from insert_weather_data import create_connection 
import datetime
import os

d = datetime.datetime
database = r"C:\sqlite\db\weather.db"

today = f'{d.now().month}_{d.now().day}'
daily_folder = f'./logs/{today}'
hourly_file = f'{daily_folder}/cities_{today}_{d.now().hour}.log'

def update_project(conn, project):
    """
    Insert new values into the weather_table.
    
    Parameters
    ----------
    conn : conn
    project : float
        weather_table values log_runtime
        
    Returns
    -------
    None
    """
    
    sql = '''
          UPDATE weather_table
          SET Log_Runtime = ?
          WHERE id = ?
          '''
    cur = conn.cursor()
    cur.execute(sql, project)
    conn.commit()
    return cur.lastrowid

for file in os.listdir(f'logs/{today}/'):
    with open(hourly_file, 'r') as f:
        log_data = f.read().splitlines()

    for line in log_data:
        rowid = line.split(': ')[1].split(',')[0]
        log_runtime = line.split('Execution Time: ')[1]
        update_data = (log_runtime, rowid)
        
        conn = create_connection(database)
        update_project(conn, update_data)