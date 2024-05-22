from flask import Flask, redirect, request, render_template, session
import pymysql

app = Flask(__name__)
app.secret_key = 'my secret key'

# MySQL 連接
def get_db_conn():
    conn = pymysql.connect(host='localhost', user='root', password='password', database='mydb')
    return conn

# 首頁
@app.route('/')
def index():
    return render_template('homepage.html')

# 獲取登入視窗的資料
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':

        # 獲取前端輸入的數據
        id = request.form['login_id']
        password = request.form['login_password']
        session['id'] = id # 存放使用者資訊供後續頁面使用

        # 從資料庫比對資料，有資料則登入成功
        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                # 測試 ID 和密碼是否都正確
                sql = 'SELECT * FROM user WHERE User_ID = %s AND Password = %s'
                cursor.execute(sql, (id, password))
                user = cursor.fetchone()
                conn.commit()

                if user is None:
                    return render_template('fail.html')
                else:
                    return render_template('login.html')
                
        except Exception as e:
            return str(e)
        finally:
            cursor.close()


# 獲取註冊視窗的資料
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':

        # 獲取前端輸入的數據
        id = request.form['regis_id']
        password = request.form['regis_password']
        name = request.form['name']

        # 插入數據到 MySQL
        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                sql = 'INSERT INTO user VALUES (%s, %s, %s)'
                cursor.execute(sql, (id, password, name))
                conn.commit()
            return render_template('register.html')
        except Exception as e:
            return str(e)
        finally:
            cursor.close()

# 紀錄功能主頁面
@app.route('/record')
def record():
    return render_template('record.html')

# 飲食紀錄頁面
@app.route('/record.diet')
def diet_redord():
    return render_template('diet_record.html')

@app.route('/record.diet.search', methods = ['POST'])
def diet_record_search():
    date = request.form['date']
    Date = date.replace('-', '')
    try:
        conn = get_db_conn()
        with conn.cursor() as cursor:
            sql = ('SELECT Calaries_Intake, Protein_intake, Carbonhydrate_Intake, Fat_Intake, Water_Intake '
                   'FROM nutrient_supplement_tracking '
                   'WHERE Date = %s AND User_ID = %s')
            cursor.execute(sql, (int(Date), int(session['id'])))
            conn.commit()
            # 獲取查詢結果
            result = cursor.fetchone()
            if result:
                cal, pro, car, fat, water = result
            else:
                return "No data found!"

        return render_template('diet_record.html', date = date, calary = cal, protein = pro, carbon = car, fath = fat, waterh = water)
    except Exception as e:
        return str(e)
    finally:
        cursor.close()

# 健身紀錄頁面
@app.route('/record.workout')
def workout_record():
    return render_template('workout_record.html')

# 菜單主頁面
@app.route('/menu')
def menu():
    return render_template('plan01.html')

# 健身菜單頁面
@app.route('/menu.workout')
def workout_menu():
    return render_template('plan02-exercise.html')

# 飲食菜單頁面
@app.route('/menu.nutrition')
def nutrition_menu():
    return render_template('plan02-food.html')

# 搜尋主頁面
@app.route('/search')
def search():
    return render_template('search.html')

# 健身房搜尋頁面
@app.route('/gym')
def gym():
    raw = open("templates/gym.html", "r", encoding="utf-8").read()
    information = '<iframe src="https://www.google.com/maps/embed?pb=!1m16!1m12!1m3!1d115716.86798982904!2d121.51359254367352!3d24.99494630977675!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!2m1!1z5YGl6Lqr5oi_!5e0!3m2!1sen!2stw!4v1716196040209!5m2!1sen!2stw" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
    return raw.replace("<?tag?>", information)

# 器材搜尋頁面
@app.route('/equipment')
def equipment():
    return  render_template('equipment.html')

# 教練搜尋頁面
@app.route('/coach')
def coach():
    return render_template('coach.html')

# 課程搜尋頁面
@app.route('/course')
def course():
    return render_template('course.html')

if __name__ == '__main__':
    app.run(debug=True)
