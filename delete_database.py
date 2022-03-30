database = r"C:\sqlite\db\weather.db"
conn = create_connection(database)
sql = 'DELETE FROM weather_table'
cur = conn.cursor()
cur.execute(sql)
conn.commit()