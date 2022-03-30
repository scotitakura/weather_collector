def create_connection(db_file):
    """
    Function connects to a database.
    
    Parameters
    ----------
    db_file : rString
        File path to the name of the database you would like to connect to.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
        
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
    
def main():
    database = r"C:\sqlite\db\weather.db"
    
    sql_create_weather_table = """ CREATE TABLE IF NOT EXISTS weather_table (
                                    id integer PRIMARY KEY,
                                    city_name text NOT NULL,
                                    state_name text,
                                    datetime text,
                                    temperature float 
                                    ); """
    
    conn = create_connection(database)
    
    if conn is not None:
        create_table(conn, sql_create_weather_table)
    else:
        print("Error! Cannot create the database connection!")
            
if __name__ == '__main__':
    main()