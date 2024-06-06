from flask import Flask, redirect, request, render_template, session, jsonify, flash, url_for
import pymysql
from datetime import date, datetime
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
@app.route('/home', methods=['GET', 'POST'])
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
                cursor.execute(
                    sql, (id, password, name, height, weight, gender))
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

@app.route('/record/diet/search', methods=['POST'])
def diet_record_search():
    date = request.form['date']
    Date = date.replace('-', '')

    try:
        conn = get_db_conn()
        with conn.cursor() as cursor:
            # 從所選的日期、預存取的 ID 找出飲食紀錄的 relation
            sql = ('SELECT Cals, Pro, Carbs, Fat, Water '
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

        return render_template('diet_record.html', date=Date, calary=cal, protein=pro,
                               carbon=car, fath=fat, waterh=water)
    except Exception as e:
        return str(e)
    finally:
        cursor.close()

# 健身紀錄頁面
@app.route('/record/workout')
def workout_record():
    return render_template('workout_record.html')

@app.route('/record/workout/search', methods=['GET', 'POST'])
def workout_record_search():
    if request.method == 'POST':

        date = request.form['date'].replace('-', '')

        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                # 從所選日期和 ID 透過 Join 找出符合的數據
                sql = ("SELECT Name, Object, plan.Training_Area, Training_Detail, Weight, `Set` "
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

        return render_template('workout_record.html', records=records)
    else:
        return render_template('workout_record.html')

# 菜單主頁面
@app.route('/plan')
def menu():
    return render_template('plan01.html')

# 健身菜單頁面
@app.route("/plan/workout", methods=["GET", "POST"])
def workout():
    try: 
        conn = get_db_conn()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql=("SELECT * FROM exercise_plan WHERE Status = 'Undone'")
            cursor.execute(sql)
            result = cursor.fetchall()
            if result:
                sql = """
                SELECT * FROM (
                    SELECT ep.day, ep.Training_Detail, ep.Training_Area, ep.`Set`, eq.name as equipment, ep.Status, ep.Plan_ID
                    FROM exercise_plan ep
                    JOIN equipment eq ON ep.Equipment_ID = eq.equipment_id
                    WHERE ep.day <= %s AND ep.User_ID = %s
                    ORDER BY ep.Plan_ID DESC
                    LIMIT %s
                ) AS subquery
                ORDER BY Plan_ID ASC
                """
                cursor.execute(sql, (int(session['days']), int(session['id']), int(session['days']*4)))
                result = cursor.fetchall()

                selected_plan = {}
                for row in result:
                    day = row['day']
                    exercise = row['equipment']
                    muscle_group = row['Training_Area']
                    set_value = row['Set']
                    status = row['Status']
                    planid = row['Plan_ID']
                    if day not in selected_plan:
                        selected_plan[day] = []
                    if len(selected_plan[day]) < 4:
                        selected_plan[day].append({
                            "exercise": exercise,
                            "muscle_group": muscle_group,
                            "set_value": set_value,
                            "status" : status,
                            "plan_id": planid
                        })

                return render_template("plan03-exercise.html", days=int(session['days']), selected_plan=selected_plan)
    except Exception as e:
        return str(e)
    finally:
        conn.close()

    if request.method == "POST":
        days = int(request.form.get("days"))
        intensity = request.form.get("intensity")
        session['days'] = days
        print(session['days'])
        set_value = 3
        if intensity == '中':
            set_value = 4
        elif intensity == '強':
            set_value = 5

        conn = get_db_conn()
        from exercise_data import exercises_by_day
        try:
            with conn.cursor() as cursor:
                for day in range(1, days + 1):
                    for equipment_id, exercise, muscle_group in exercises_by_day[day][:4]:  # 確保每天只插入四個動作
                        sql = """
                        INSERT INTO exercise_plan (User_ID, Equipment_ID, Object, Training_Area, Weight, `Set`, Training_Detail, day) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                        """
                        cursor.execute(sql, (int(session['id']), equipment_id, '增肌', muscle_group, 5, set_value, exercise, day))
                conn.commit()
                
            return redirect(url_for("generate_plan"))
        except Exception as e:
            return str(e)
        finally:
            conn.close()
    else:
        return render_template("plan02-exercise.html")

# 健身菜單製作
@app.route("/plan/workout/make", methods = ['GET', 'POST'])
def generate_plan():
    days = int(session['days'])
    conn = get_db_conn()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT * FROM (
                SELECT ep.day, ep.Training_Detail, ep.Training_Area, ep.`Set`, eq.name as equipment, ep.Status, ep.Plan_ID
                FROM exercise_plan ep
                JOIN equipment eq ON ep.Equipment_ID = eq.equipment_id
                WHERE ep.day <= %s AND ep.User_ID = %s
                ORDER BY ep.Plan_ID DESC
                LIMIT %s
            ) AS subquery
            ORDER BY Plan_ID ASC
            """
            cursor.execute(sql, (days, int(session['id']), int(session['days']*4)))
            result = cursor.fetchall()

            selected_plan = {}
            for row in result:
                day = row['day']
                exercise = row['equipment']
                muscle_group = row['Training_Area']
                set_value = row['Set']
                status = row['Status']
                planid = row['Plan_ID']
                if day not in selected_plan:
                    selected_plan[day] = []
                if len(selected_plan[day]) < 4:
                    selected_plan[day].append({
                        "exercise": exercise,
                        "muscle_group": muscle_group,
                        "set_value": set_value,
                        "status" : status,
                        "plan_id": planid
                    })

        return render_template("plan03-exercise.html", days=days, selected_plan=selected_plan)
    finally:
        conn.close()

# 菜單確認完成的頁面
@app.route('/update_status', methods=['POST'])
def update_status():
    # 獲取前端傳遞的 Json 檔案 (該健身菜單的 id)
    data = request.json
    plan_id = data['plan_id']

    try:
        conn = get_db_conn()
        with conn.cursor() as cursor:
            # 將該 id 的菜單設置為完成
            sql = """
            UPDATE exercise_plan
            SET Status = 'Done'
            WHERE Plan_ID = %s
            """
            cursor.execute(sql, (int(plan_id)))
            conn.commit()
    except Exception as e:
        return str(e)
    finally:
        conn.close()

    return jsonify({'success': True}), 200

# 飲食菜單頁面
@app.route('/plan/nutrition', methods=['GET', 'POST'])
def nutrition_menu():
    today = date.today()
    nutrient_data = {
        'water': 0.0,
        'protein': 0.0,
        'calories': 0.0,
        'carbohydrate': 0.0,
        'fat': 0.0
    }

    try:
        conn = get_db_conn()
        with conn.cursor() as cursor:
            sql1 = "SELECT Water, Pro, Cals, Carbs, Fat FROM `nutrient_supplement_tracking` WHERE User_ID = %s AND Date = %s"
            cursor.execute(sql1, (int(session['id']), today))
            result = cursor.fetchone()
            # 確認是否有值，有值則覆蓋
            if result:
                result_dict = {
                    'water': result[0],
                    'protein': result[1],
                    'calories': result[2],
                    'carbonhydrate': result[3],
                    'fat': result[4]
                }

                nutrient_data['water'] = float(result_dict['water'])
                nutrient_data['protein'] = float(result_dict['protein'])
                nutrient_data['calories'] = float(result_dict['calories'])
                nutrient_data['carbohydrate'] = float(result_dict['carbonhydrate'])
                nutrient_data['fat'] = float(result_dict['fat'])

            # 先讀取使用者的身高、體重、性別、健身目標、年齡
            sql2 = ('SELECT Height, Weight, Gender, Objective, Age '
                    'FROM user '
                    'WHERE User_ID = %s')
            cursor.execute(sql2, int(session['id']))
            results = cursor.fetchone()

            # 獲取資料庫數據
            if results:
                height, weight, gender, obj, age = results
                height = float(height)
                weight = float(weight)
                age = int(age)
                # 計算基礎代謝率 BMR
                if gender == 'male':
                    bmr = 88.632 + (13.397*weight) + \
                        (4.799*height) - (5.677*age)
                elif gender == 'female':
                    bmr = 447.593 + (9.247*weight) + \
                        (3.098*height) - (4.33*age)
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
        return render_template('plan02-food.html',
                               protein=protein, carbs=carbs, water=water, fat=fat, cal=cal, nutrient_data=nutrient_data)
    except Exception as e:
        return str(e)
    finally:
        cursor.close()

# 營養更新
@app.route('/plan/nutrition/update', methods=['GET', 'POST'])
def nutrition_update():
    today = date.today()
    id = int(session.get('id'))

    try:
        conn = get_db_conn()
        with conn.cursor() as cursor:
            # 確認當天是否有數據
            check_sql = ('SELECT * FROM nutrient_supplement_tracking '
                         'WHERE User_ID = %s AND Date = %s')
            cursor.execute(check_sql, (id, today))
            record = cursor.fetchone()
            if record:
                record_exists = record[0]
            else:
                record_exists = 0
            # 若沒有數據則插入全新數據
            if record_exists == 0:
                insert_sql = ('INSERT INTO nutrient_supplement_tracking (User_ID, Date, Pro, Carbs, Fat, Water, Cals) '
                              'VALUES (%s, %s, 0, 0, 0, 0, 0)')
                cursor.execute(insert_sql, (id, today))
                conn.commit()

            # 確認是否需要插入數據後取得值(只取前綴)
            water = int(request.args.get('water').split()[0])
            pro = int(request.args.get('pro').split()[0])
            cals = int(request.args.get('cals').split()[0])
            carbs = int(request.args.get('carbs').split()[0])
            fat = int(request.args.get('fat').split()[0])
            print(water)
            # 更新紀錄
            update_sql = ('UPDATE nutrient_supplement_tracking '
                          'SET Water = %s, Pro = %s, Cals = %s, Carbs = %s, Fat = %s '
                          'WHERE User_id = %s AND Date = %s')
            cursor.execute(
                update_sql, (water, pro, cals, carbs, fat, id, today))
            conn.commit()
        return render_template('updateSuccess.html')
    except Exception as e:
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
    raw = open("templates\gym.html", "r", encoding="utf-8").read()
    information = '<iframe src="https://www.google.com/maps/embed?pb=!1m16!1m12!1m3!1d115716.86798982904!2d121.51359254367352!3d24.99494630977675!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!2m1!1z5YGl6Lqr5oi_!5e0!3m2!1sen!2stw!4v1716196040209!5m2!1sen!2stw" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
    return raw.replace("<?tag?>", information)

# 器材搜尋頁面
@app.route('/search/equipment')
def equipment():
    Name = request.args.get('branch')
    Equipment = request.args.get('equipment')

    if Name is None or Equipment is None:
        return render_template('search-equipment.html', equipments = [])
    
    try:
        conn = get_db_conn()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 取得健身房數據
            sql = 'SELECT * FROM gym WHERE Name = %s'
            cursor.execute(sql, (Name))
            Gym_ID = [dict(gym) for gym in cursor.fetchall()][0]['Gym_ID']

            # 取得 equipment 數據
            sql = 'SELECT * FROM equipment WHERE Training_Area = %s AND Gym_ID = %s'
            cursor.execute(sql, (Equipment, Gym_ID))
            equipments = [dict(equipment) for equipment in cursor.fetchall()]

            # 若沒有數據
            if equipments == []:
                return render_template('search-equipment.html', equipments = [{'Name':'無符合條件的器材'}])
            
            return render_template('search-equipment.html', equipments = equipments)
    except Exception as e:
        return str(e)
    finally:
        cursor.close()

# 教練搜尋頁面
@app.route('/search/coach')
def coach():
    name = request.args.get("branch")
    expertise= request.args.get("expertise")

    if name is None or expertise is None:
        return render_template('search-coach.html', coaches=[])
    
    try:
        conn = get_db_conn()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 獲取健身房數據
            sql = 'SELECT * FROM gym WHERE Name = %s'
            cursor.execute(sql, (name))
            gym_id = [dict(gym) for gym in cursor.fetchall()][0]['Gym_ID']

            # 獲取教練數據
            sql = 'SELECT * FROM coach WHERE Expertise = %s AND Gym_ID = %s'
            cursor.execute(sql, (expertise, gym_id))
            coaches = [dict(coach) for coach in cursor.fetchall()]

            # 若沒有教練
            if coaches == []:
                return render_template('search-coach.html', coaches = [{"Name":"無符合條件的教練"}])
        
        return render_template('search-coach.html', coaches = coaches)
    except Exception as e:
        return str(e)
    finally:
        cursor.close()

# 課程搜尋頁面
@app.route('/search/course')
def course():
    name = request.args.get("branch")
    course = request.args.get("course")

    if name is None or course is None:
        return render_template('search-course.html', courses=[])
    
    try:
        conn = get_db_conn()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 獲取健身房數據
            sql = 'SELECT * FROM gym WHERE Name = %s'
            cursor.execute(sql, (name))
            gym_id = [dict(gym) for gym in cursor.fetchall()][0]['Gym_ID']

            # 獲取課程數據
            sql = 'SELECT * FROM course WHERE Name = %s AND Gym_ID = %s'
            cursor.execute(sql, (course, gym_id))
            courses = [dict(course) for course in cursor.fetchall()]

            # 若沒有課程
            if courses == []:
                return render_template('search-course.html', courses = [{"Name":"無符合條件的課程"}])

            return render_template('search-course.html', courses = courses)
    except Exception as e:
        return str(e)
    finally:
        cursor.close()

# 會員專區頁面
@app.route('/member', methods=['GET', 'POST'])
def member():
    if request.method == 'POST':
        # 獲取新數據更新資料庫
        name = request.form['name']
        height = request.form['height']
        weight = request.form['weight']
        gender = request.form['gender']
        obj = request.form['obj']
        age = request.form['age']

        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                sql = ('UPDATE user '
                       'SET Name = %s, Height = %s, Weight = %s, Gender = %s, Objective = %s, Age = %s '
                       'WHERE User_ID = %s')
                cursor.execute(sql, (name, float(height), float(
                    weight), gender, obj, int(age), int(session['id'])))
                conn.commit()
                return render_template('memberSuccess.html')
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
    else:
        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                # 從 user 中獲取基本資料
                sql = ('SELECT User_ID, Name, Height, Weight, Gender, Objective, Age '
                       'FROM user '
                       'WHERE User_id = %s')
                cursor.execute(sql, (int(session['id'])))
                results = cursor.fetchone()
                # 轉換資料形式
                if results:
                    id, name, height, weight, gender, obj, age = results
                    id = int(id)
                    height = float(height)
                    weight = float(weight)
                    age = int(age)
                return render_template('member.html', id=id, name=name, height=height, weight=weight, gender=gender, obj=obj, age=age)
        except Exception as e:
            return str(e)
        finally:
            conn.close()

# GYPT 主頁面
@app.route('/gypt')
def gypt():
    try:
        conn = get_db_conn()
        with conn.cursor() as cursor:
            # 獲取所有人的總訓練時長並排名
            sql = ('select name, sum(t) as total '
                    'from('
                    '    select name, s.user_id, timestampdiff(minute, `start`, `finish`) as t '
                    '    from gypt_start as s join gypt_finish as f '
                    '    on s.User_ID = f.User_ID '
                    '    and date(start) = date(finish) '
                    '    and s.ID = f.ID '
                    '    join user on s.user_id = user.User_ID'
                    ') as everyday '
                    'group by name '
                    'order by total desc ')
            cursor.execute(sql)
            # 獲取結果，並將其轉換為字典
            results = cursor.fetchall()
            if results:
                results = [{'Rank': index + 1, 'User': r[0], 'Time': r[1]} for index, r in enumerate(results[:5])]
    except Exception as e:
        return str(e)
    finally:
        cursor.close()
    return render_template('ranking-list.html', results = results)

# GYPT 計時頁面
@app.route('/gypt/timing')
def timing():
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    try:
        conn = get_db_conn()
        with conn.cursor() as cursor:
            # 插入開始的時間戳記
            sql = ('INSERT INTO gypt_start (User_ID, Start)'
                   'VALUES (%s, %s)')
            cursor.execute(sql, (int(session['id']), ts))
            conn.commit()

            # 更新使用者狀態為 ing
            sql = "UPDATE user SET Status = 'ing' WHERE User_ID = %s"
            cursor.execute(sql, (int(session['id'])))
            conn.commit()

            # 檢查有誰正在健身
            sql = "SELECT Name FROM user WHERE Status = 'ing' AND User_ID <> %s"
            cursor.execute(sql, (int(session['id'])))
            results = cursor.fetchall()

            if results:
                results = [{'Rank': index + 1, 'User': r[0]} for index, r in enumerate(results[:5])]
    except Exception as e:
        return str(e)
    finally:
        cursor.close()
    return render_template('timing.html', results=results)

# GYPT 訓練時長結果頁面
@app.route('/gypt/timing/result')
def gypt_result():
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    try:
        conn = get_db_conn()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 將 User Status 更新為 'no'
            sql = "UPDATE user SET Status = 'no' WHERE User_ID = %s"
            cursor.execute(sql, (int(session['id'])))
            conn.commit()

            # 插入結束時間
            sql = ('INSERT INTO gypt_finish (User_ID, Finish)'
                   'VALUES (%s, %s)')
            cursor.execute(sql, (int(session['id']), ts))
            conn.commit()

            # 將最新的一次數據取出
            time_sql = ('SELECT timestampdiff(minute, `start`, `finish`) as t '
                        'FROM gypt_start AS s JOIN gypt_finish AS f '
                        'ON s.User_ID = f.User_ID '
                        'AND date(start) = date(finish) '
                        'AND s.ID = f.ID '
                        'ORDER BY f.ID desc')
            cursor.execute(time_sql)
            # 獲取結果
            result = cursor.fetchone()
            time = result['t'] if result else None
    except Exception as e:
        return str(e)
    finally:
        cursor.close()
    return render_template('timing_result.html', time = time)

# 介紹頁面
@app.route('/intro')
def intro():
    return render_template('introduction.html')

if __name__ == '__main__':
    app.run(debug=True)
