import pymysql
from flask import Flask, jsonify

app = Flask(__name__)

# Route to fetch data
@app.route('/getdata')
def get_data(table):
    # Establish connection
    conn = pymysql.connect(host='localhost', user='root', password='sw0217', database='mydb')
    # Create a cursor
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # Using DictCursor to return data as dictionaries
    try:
        # SQL query
        query = "SELECT * FROM " + table  # Replace 'your_table_name' with the actual table name
        # Execute the query
        cursor.execute(query)
        # Fetch all rows
        rows = cursor.fetchall()
        # Convert query results to a list of dictionaries
        results = [dict(row) for row in rows]

        return jsonify(results)  # Return results as JSON
    except Exception as e:
        return str(e)  # Return error message if something goes wrong
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()


def add_equipment():
    # Retrieve data from form
    Gym_ID = 6000
    Equipment_ID = 6000
    Address = "1 place"
    Name = "1 gym"

    # Establish connection
    conn = pymysql.connect(host='localhost', user='root', password='sw0217', database='mydb')
    cursor = conn.cursor()
    
    try:
        # Insert data into the gym table
        cursor.execute("INSERT INTO gym (Gym_ID, Equipment_ID, Address, Name) VALUES (%s, %s, %s, %s)", (Gym_ID, Equipment_ID, Address, Name))
        conn.commit()  # Commit to save changes
        return "somewhat worked"
    except Exception as e:
        conn.rollback()  # Rollback in case of error
        return str(e)  # Return the error message
    finally:
        cursor.close()
        conn.close()

def add_equipment():
    # Retrieve data from form
    Equipment_ID = 6000
    Training_Area = "back"

    # Establish connection
    conn = pymysql.connect(host='localhost', user='root', password='sw0217', database='mydb')
    cursor = conn.cursor()
    
    try:
        # Insert data into the gym table
        cursor.execute("INSERT INTO equipment_training_area (Equipment_ID, Training_Area) VALUES (%s, %s)", (Equipment_ID, Training_Area))
        conn.commit()  # Commit to save changes
        return "somewhat worked"
    except Exception as e:
        conn.rollback()  # Rollback in case of error
        return str(e)  # Return the error message
    finally:
        cursor.close()
        conn.close()

def add_coach():
    # Retrieve data from form
    Coach_ID = 6000
    Name = "coachA"
    Expertise = "胸"

    # Establish connection
    conn = pymysql.connect(host='localhost', user='root', password='sw0217', database='mydb')
    cursor = conn.cursor()
    
    try:
        # Insert data into the gym table
        cursor.execute("INSERT INTO coach (Coach_ID, Name, Expertise) VALUES (%s, %s, %s)", (Coach_ID, Name, Expertise))
        conn.commit()  # Commit to save changes
        return "somewhat worked"
    except Exception as e:
        conn.rollback()  # Rollback in case of error
        return str(e)  # Return the error message
    finally:
        cursor.close()
        conn.close()

def add_course():
    # Retrieve data from form
    Course_ID = 6000
    Name = "十人十一腳"

    # Establish connection
    conn = pymysql.connect(host='localhost', user='root', password='sw0217', database='mydb')
    cursor = conn.cursor()
    
    try:
        # Insert data into the gym table
        cursor.execute("INSERT INTO course (Course_ID, Name) VALUES (%s, %s)", (Course_ID, Name))
        conn.commit()  # Commit to save changes
        return "somewhat worked"
    except Exception as e:
        conn.rollback()  # Rollback in case of error
        return str(e)  # Return the error message
    finally:
        cursor.close()
        conn.close()

# Run the application if this script is executed
if __name__ == '__main__':
    print(add_course())
