import pymysql
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates")

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

def get_db_conn():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='sw0217',
        database='mydb'
    )

@app.route('/')
def index():
    return render_template('search-homepage.html')

# 健身房搜尋頁面
@app.route('/search/gym')
def gym():
    raw = open("templates\gym.html", "r", encoding="utf-8").read()
    information = '<iframe src="https://www.google.com/maps/embed?pb=!1m16!1m12!1m3!1d115716.86798982904!2d121.51359254367352!3d24.99494630977675!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!2m1!1z5YGl6Lqr5oi_!5e0!3m2!1sen!2stw!4v1716196040209!5m2!1sen!2stw" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
    return raw.replace("<?tag?>", information)

# 器材搜尋頁面
@app.route('/search/equipment')
def equipment():
    Name = request.args.get("branch")
    Equipment = request.args.get("equipment")

    if Name == None or Equipment == None:
        return render_template('search-equipment.html', equipments=[])
    
    try:
        conn = get_db_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        sql = 'SELECT * FROM gym WHERE Name = %s'
        cursor.execute(sql, (Name))
        Gym_ID = [dict(gym) for gym in cursor.fetchall()][0]['Gym_ID']

        print(Gym_ID)

        sql = 'SELECT * FROM equipment WHERE Training_Area = %s AND Gym_ID = %s'
        cursor.execute(sql, (Equipment, Gym_ID))
        equipments = [dict(equipment) for equipment in cursor.fetchall()]

        print("equipments =",equipments)
        if equipments == []:
            return render_template('search-equipment.html', equipments = [{"Name":"無符合條件的器材"}])

        return render_template('search-equipment.html', equipments = equipments)
    except Exception as e:
        return str(e)
    

    

# 教練搜尋頁面
@app.route('/search/coach')
def coach():
    Name = request.args.get("branch")
    Expertise= request.args.get("expertise")

    if Name == None or Expertise == None:
        return render_template('search-coach.html', coaches=[])
    
    try:
        conn = get_db_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        sql = 'SELECT * FROM gym WHERE Name = %s'
        cursor.execute(sql, (Name))
        Gym_ID = [dict(gym) for gym in cursor.fetchall()][0]['Gym_ID']

        print(Gym_ID)

        sql = 'SELECT * FROM coach WHERE Expertise = %s AND Gym_ID = %s'
        cursor.execute(sql, (Expertise, Gym_ID))
        coaches = [dict(coach) for coach in cursor.fetchall()]

        print("coaches =",coaches)
        if coaches == []:
            return render_template('search-coach.html', coaches = [{"Name":"無符合條件的教練"}])

        return render_template('search-coach.html', coaches = coaches)
    except Exception as e:
        return str(e)

# 課程搜尋頁面
@app.route('/search/course')
def course():
    Name = request.args.get("branch")
    Course = request.args.get("course")

    if Name == None or Course == None:
        return render_template('search-course.html', courses=[])
    
    try:
        conn = get_db_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        sql = 'SELECT * FROM gym WHERE Name = %s'
        cursor.execute(sql, (Name))
        Gym_ID = [dict(gym) for gym in cursor.fetchall()][0]['Gym_ID']

        print(Gym_ID)

        sql = 'SELECT * FROM course WHERE Name = %s AND Gym_ID = %s'
        cursor.execute(sql, (Course, Gym_ID))
        courses = [dict(course) for course in cursor.fetchall()]

        print("courses =",courses)

        if courses == []:
            return render_template('search-course.html', courses = [{"Name":"無符合條件的課程"}])

        return render_template('search-course.html', courses = courses)
    except Exception as e:
        return str(e)



if __name__ == '__main__':
    app.run(debug=True)
