import pymysql
from flask import Flask, jsonify

app = Flask(__name__)

# Route to fetch data
def get_data(table, restriction=""):
    # Establish connection
    conn = pymysql.connect(host='localhost', user='root', password='sw0217', database='mydb', charset='utf8mb4')
    # Create a cursor
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # Using DictCursor to return data as dictionaries
    try:
        # SQL query
        query = "SELECT * FROM " + table + restriction  # Replace 'your_table_name' with the actual table name
        # Execute the query
        cursor.execute(query)
        # Fetch all rows
        rows = cursor.fetchall()
        # Convert query results to a list of dictionaries
        results = [dict(row) for row in rows]
        return results  # Return results as JSON
    except Exception as e:
        return str(e)  # Return error message if something goes wrong
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

print(get_data("coach", " WHERE Expertise = '腹肌'"))