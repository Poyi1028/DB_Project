from flask import Flask, redirect, request, render_template, session
import pymysql
import pymysql.cursors

app = Flask(__name__)
app.secret_key = 'my secret key'

# MySQL 連接
def get_db_conn():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='password',
        database='mydb'
    )
    return conn

# 登入/註冊頁面
@app.route('/')
def index():
    return render_template('index.html')

# 登入成功後至首頁
@app.route('/home', methods=['GET','POST'])
def login():
    if request.method == 'POST':

        # 獲取前端輸入的數據
        id = request.form['login_ID']
        password = request.form['login_ps']

        # 存放使用者資訊供後續頁面使用
        session['id'] = id 

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
                    return render_template('homepage.html')
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
    else:
        return render_template('homepage.html')


# 獲取註冊視窗的資料
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':

        # 獲取前端輸入的數據
        id = request.form['regis_ID']
        password = request.form['regis_ps']
        password2 = request.form['confirm_ps']
        name = request.form['name']
        height = request.form['height']
        weight = request.form['weight']
        gender = request.form['gender']

        # 插入數據到 MySQL
        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                sql = 'INSERT INTO user VALUES (%s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, (id, password, name, height, weight, gender))
                conn.commit()
                if password == password2:
                    return render_template('register.html')
                else:
                    return '密碼不一致'
        except Exception as e:
            return str(e)
        finally:
            cursor.close()

# 紀錄功能主頁面
@app.route('/record')
def record():
    return render_template('record.html')

# 飲食紀錄頁面
@app.route('/record/diet')
def diet_redord():
    return render_template('diet_record.html')

@app.route('/record/diet/search', methods = ['POST'])
def diet_record_search():
    date = request.form['date']
    Date = date.replace('-', '')

    try:
        conn = get_db_conn()
        with conn.cursor() as cursor:
            # 從所選的日期、預存取的 ID 找出飲食紀錄的 relation
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
                return 'No result found'
            
        return render_template('diet_record.html', date = Date, calary = cal, protein = pro,
                               carbon = car, fath = fat, waterh = water)
    except Exception as e:
        return str(e)
    finally:
        cursor.close()

# 健身紀錄頁面
@app.route('/record/workout')
def workout_record():
    return render_template('workout_record.html')

@app.route('/record/workout/search', methods = ['GET', 'POST'])
def workout_record_search():
    if request.method == 'POST':

        date = request.form['date'].replace('-', '')

        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                # 從所選日期和 ID 透過 Join 找出符合的數據
                sql = ("SELECT Equipment_Name, Object, Training_Area, Training_Detail, Weight, `Set` "
                    "FROM exercise_plan as plan LEFT JOIN equipment as e "
                    "ON plan.Equipment_ID = e.Equipment_ID "
                    "WHERE Status = 'Done' "
                    "AND Completed_Date = %s "
                    "AND User_ID = %s")
                cursor.execute(sql, (int(date), int(session['id'])))
                records = cursor.fetchall()
                # 將傳回的tuple轉換成字典
                records = [{'Equipment_Name': r[0], 'Object': r[1], 'Training_Area': r[2],
                            'Training_Detail': r[3], 'Weight': r[4], 'Set': r[5]} for r in records]
        except Exception as e:
            return str(e)
        finally:
            cursor.close()

        return render_template('workout_record.html', records = records)
    else:
        return render_template('workout_record.html')
    
# 菜單主頁面
@app.route('/plan')
def menu():
    return render_template('plan01.html')

# 健身菜單頁面
@app.route('/plan/workout')
def workout_plan():
    return render_template('plan02-exercise.html')

# 健身菜單製作
@app.route('/plan/workout/make')
def workout_make():
    return render_template('plan03-exercise.html')

# 飲食菜單頁面
@app.route('/plan/nutrition')
def nutrition_menu():
    #if request.method == 'POST':

        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                # 先讀取使用者的身高、體重、性別、健身目標、年齡
                sql=('SELECT Height, Weight, Gender, Objective, Age '
                     'FROM user '
                     'WHERE User_ID = %s')
                cursor.execute(sql, int(session['id']))
                results = cursor.fetchone()

                # 獲取資料庫數據
                if results:
                    height, weight, gender, obj, age = results
                    height = float(height)
                    weight = float(weight)
                    age = int(age)
                    # 計算基礎代謝率 BMR
                    if gender == 'male':
                        bmr = 88.632 + (13.397*weight) + (4.799*height) - (5.677*age)
                    elif gender == 'female':
                        bmr = 447.593 + (9.247*weight) + (3.098*height) - (4.33*age)
                    # 套用營養攝取公式
                    if obj == '增肌':
                        protein = round(weight * 1.6, 0)
                        carbs = round(weight * 4, 0)
                        water = round(weight * 35, 0)
                        fat = round(weight * 0.5, 0)
                        cal = round(bmr * 1.725 * 1.1, 0)
                    elif obj == '減脂':
                        protein = round(weight * 1.8, 0)
                        carbs = round(weight * 2, 0)
                        water = round(weight * 35, 0)
                        fat = round(weight * 0.5, 0)
                        cal = round(bmr * 1.55 * 0.9, 0)
                    elif obj == '維持身材':
                        protein = round(weight * 1.2, 0)
                        carbs = round(weight * 3, 0)
                        water = round(weight * 35, 0)
                        fat = round(weight * 0.8, 0)
                        cal = round(bmr * 1.375, 0)
            return render_template('plan02-food.html', protein = protein, carbs = carbs, water = water, fat = fat, cal = cal)
        except Exception  as e:
            return str(e)
        finally:
            cursor.close()

# 搜尋主頁面
@app.route('/search')
def search():
    return render_template('search-homepage.html')

# 健身房搜尋頁面
@app.route('/search/gym')
def gym():
    return render_template('gym.html')

# 器材搜尋頁面
@app.route('/search/equipment')
def equipment():
    return  render_template('search-equipment.html')

# 教練搜尋頁面
@app.route('/search/coach')
def coach():
    return render_template('search-coach.html')

# 課程搜尋頁面
@app.route('/search/course')
def course():
    return render_template('search-course.html')

# 會員專區頁面
@app.route('/member')
def member():
    return render_template('membership.html')

# GYPT頁面
@app.route('/gypt')
def gypt():
    return render_template('ranking-list.html')

if __name__ == '__main__':
    app.run(debug=True)
