import pyodbc
# Connection parameters
server = 'your_server_name'
database = 'your_database_name'
username = 'your_username'
password = 'your_password'

# Establish connection
connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
connection = pyodbc.connect(connection_string)

# Create cursor
cursor = connection.cursor()

# Execute SQL query
query = "SELECT * FROM your_table"
cursor.execute(query)

# Fetch and process results
for row in cursor:
    print(row)

# Close cursor and connection
cursor.close()
connection.close()
