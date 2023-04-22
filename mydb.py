import mysql.connector
# Initialize MySQL Database
# Create connection
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='Batman123!',
    port='3306'
)
# Create cursor object
cursor = connection.cursor()
# Create Database
cursor.execute("CREATE DATABASE shop_db")

# Close connection
connection.close()

