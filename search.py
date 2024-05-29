import pymysql
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# MySQL 連接
def get_data(table, restriction=""):
    # Establish connection
    conn = pymysql.connect(host='localhost', user='root', password='sw0217', database='mydb', charset='utf8mb4')
    # Create a cursor
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # Using DictCursor to return data as dictionaries
    try:
        # SQL query
        query = f"SELECT * FROM {table} {restriction}"  # Replace 'your_table_name' with the actual table name
        
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

@app.route('/')
def index():
    return render_template('search.html')

@app.route('/gym')
def gym():
    raw = open("templates\gym.html", "r", encoding="utf-8").read()
    information = '<iframe src="https://www.google.com/maps/embed?pb=!1m16!1m12!1m3!1d115716.86798982904!2d121.51359254367352!3d24.99494630977675!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!2m1!1z5YGl6Lqr5oi_!5e0!3m2!1sen!2stw!4v1716196040209!5m2!1sen!2stw" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
    return raw.replace("<?tag?>", information)

@app.route('/equipment')
def equipment():
    raw = open("templates\equipment.html", "r", encoding="utf-8").read()
    gymOptions = "\n".join(['<option value="' + gym['Name'] + '">' + gym['Name'] + '</option>' for gym in get_data("gym")])
    print(get_data("equipment_training_area"))
    equipmentOptions = "\n".join(['<option value="' + gym['Training_Area'] + '">' + gym['Training_Area'] + '</option>' for gym in get_data("equipment_training_area")])
    return raw.replace("<?branchOptions?>", gymOptions).replace("<?equipmentOptions?>", equipmentOptions)

@app.route('/coach')
def coach():
    raw = open("templates\coach.html", "r", encoding="utf-8").read()
    gymOptions = "\n".join(['<option value="' + gym['Name'] + '">' + gym['Name'] + '</option>' for gym in get_data("gym")])
    expertiseOptions = "\n".join(['<option value="' + gym['Expertise'] + '">' + gym['Expertise'] + '</option>' for gym in get_data("coach")])
    print(request.args.get("branch"), request.args.get("expertise"))
    
    restriction = f"Where (Gym_ID = '{request.args.get("branch")}' or Gym_ID IS NULL) and Expertise = '{request.args.get("expertise")}'"
    
    print(get_data("coach", restriction) )
    return raw.replace("<?branchOptions?>", gymOptions).replace("<?expertiseOptions?>", expertiseOptions)
    return open("templates\coach.html", "r", encoding="utf-8").read()

@app.route('/course')
def course():
    raw = open("templates\course.html", "r", encoding="utf-8").read()
    gymOptions = "\n".join(['<option value="' + gym['Name'] + '">' + gym['Name'] + '</option>' for gym in get_data("gym")])
    courseOptions = "\n".join(['<option value="' + gym['Name'] + '">' + gym['Name'] + '</option>' for gym in get_data("course")])
    # get_data("caoch", "Gym_ID = +")
    # print(request.args.get("branch"], request.args.get("expertise"])
    return raw.replace("<?branchOptions?>", gymOptions).replace("<?courseOptions?>", courseOptions)
    return open("templates\course.html", "r", encoding="utf-8").read()

# Run the application if this script is executed
if __name__ == '__main__':
    app.run(debug=True)