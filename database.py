# importing our database handler
import mysql.connector

# instantiating a connection to the  server
my_server = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
)

# creating the server handler
my_cursor = my_server.cursor()

# saving the name of the database
new_database = "test_project"

# showing the list of databases that we have
my_cursor.execute("SHOW DATABASES")

# check if our database is created already
v = 0
for db in my_cursor:
    for each_db in db:
        if new_database == each_db:
            v += 1


# if it is not created, create it
if v == 0:
    my_cursor.execute("CREATE DATABASE " + new_database)


# instantiating a connection to the database
my_db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database=new_database
)

# creating the handler for our database
my_db_cursor = my_db.cursor()

# list of our tables
list_of_all_our_tables = ['users', 'category', 'sub_category', 'products', 'sales', 'delivery', 'orders', 'payment']

# building SQL for each table in our list of tables
users_table_sql = "(id(INT, AUTO_INCREMENT, PRIMARY KEY)," \
                  "fullname(VARCHAR(100), NOT NULL))"

# To show all the tables in our database
my_db_cursor.execute("SHOW TABLES")

# tables in database
tables_in_database = []

# looping through the list of tables in our database
for tables in my_db_cursor:
    for table in tables:
        tables_in_database.append(table)


# creating that does not exist
for table in list_of_all_our_tables:
    if not table in tables_in_database:

        # create the table
        my_db_cursor.execute("CREATE TABLE " + table)
