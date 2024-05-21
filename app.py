from flask import Flask, redirect, request, render_template
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
def diet_record():
    return render_template('diet_record.html')

# 健身紀錄頁面
@app.route('/record.workout')
def workout_record():
    return render_template('workout_record.html')

# 菜單頁面
@app.route('/menu')
def menu():
    return render_template('plan01.html')

if __name__ == '__main__':
    app.run(debug=True)
