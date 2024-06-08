from flask import Flask, redirect, request, render_template, session, jsonify, flash, url_for, make_response
import pymysql
from datetime import date, datetime
import pymysql.cursors
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
import io

app = Flask(__name__)
app.secret_key = 'my secret key'

plt.rc('font', family='Microsoft JhengHei')

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

        if password != password2:
            return '密碼不一致'
        # 插入數據到 MySQL
        conn = get_db_conn()
        try:
            with conn.cursor() as cursor:
                sql = 'INSERT INTO user (User_ID, Password, Name, Height, Weight, Gender) VALUES (%s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, (id, password, name, height, weight, gender))
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
    # 確認是否有尚未完成的菜單，有則跳轉到菜單頁面
    try: 
        conn = get_db_conn()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql=("SELECT * FROM exercise_plan WHERE Status = 'Undone' AND User_ID = %s")
            cursor.execute(sql, (int(session['id'])))
            result = cursor.fetchall()
            if result:
                sql = """
                SELECT * FROM (
                    SELECT ep.day, ep.Training_Detail, ep.Training_Area, ep.Weight, ep.`Set`, eq.name as equipment, ep.Status, ep.Plan_ID
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
                    weight = row['Weight']
                    set_value = row['Set']
                    status = row['Status']
                    planid = row['Plan_ID']
                    if day not in selected_plan:
                        selected_plan[day] = []
                    if len(selected_plan[day]) < 4:
                        selected_plan[day].append({
                            "exercise": exercise,
                            "muscle_group": muscle_group,
                            "weight": weight,
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
        area = request.form.get('training_area')
        # 儲存健身菜單天數
        session['days'] = days

        set_value = 3
        if intensity == '中':
            set_value = 4
        elif intensity == '強':
            set_value = 5

        # 獲得使用者的健身目標
        try:
            conn = get_db_conn()
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = 'SELECT Objective FROM user WHERE User_ID = %s'
                cursor.execute(sql, (int(session['id'])))
                result = cursor.fetchone()
                obj = result['Objective']

                # 根據所選部位和健身目標選擇菜單
                if area == '胸肌':
                    if obj == '增肌':
                        from exercise_data import chest_muscle as exercises
                    elif obj == '減脂':
                        from exercise_data import chest_lose as exercises
                elif area == '肩膀':
                    from exercise_data import shoulder_muscle as exercises

                for day in range(1, days + 1):
                    for equipment_id, exercise, muscle_group in exercises[day][:4]:  # 確保每天只插入四個動作
                        # 為有氧動作設定單位
                        if muscle_group == '有氧':
                            if exercise == '跑步機' or exercise == '飛輪':
                                unit = '15 分鐘'
                            elif exercise == '棒式':
                                unit = '10 分鐘'
                            elif exercise == '跳繩':
                                unit = '5 分鐘'
                            else:
                                unit = '3 分鐘'
                        else:
                            unit = '5 公斤'

                        # 查詢過去是否有該器材已完成的健身紀錄
                        # 若有則將單位設成紀錄中的最大值
                        sql = """
                        SELECT CAST(SUBSTRING_INDEX(Weight, ' ', 1) AS UNSIGNED) AS Weight FROM exercise_plan
                        WHERE User_ID = %s AND Status = 'Done' AND Equipment_ID = %s
                        ORDER BY Weight DESC
                        LIMIT 1
                        """
                        cursor.execute(sql, (int(session['id']), equipment_id))
                        results = cursor.fetchone()
                        if results:
                            equipment_weights = results['Weight']
                            if muscle_group == '有氧':
                                unit = str(equipment_weights) + ' 分鐘'
                            else:
                                unit = str(equipment_weights) + ' 公斤'

                        sql = """
                        INSERT INTO exercise_plan (User_ID, Equipment_ID, Object, Training_Area, Weight, `Set`, Training_Detail, day) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                        """
                        cursor.execute(sql, (int(session['id']), equipment_id, obj, muscle_group, unit, set_value, exercise, day))
                conn.commit()
            return redirect(url_for("generate_plan"))
        except Exception as e:
            return str(e)
        finally:
            cursor.close()
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
                SELECT ep.day, ep.Training_Detail, ep.Training_Area, ep.Weight, ep.`Set`, eq.name as equipment, ep.Status, ep.Plan_ID
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
                weight = row['Weight']
                set_value = row['Set']
                status = row['Status']
                planid = row['Plan_ID']
                if day not in selected_plan:
                    selected_plan[day] = []
                if len(selected_plan[day]) < 4:
                    selected_plan[day].append({
                        "exercise": exercise,
                        "muscle_group": muscle_group,
                        "weight": weight,
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
    today = date.today()

    try:
        conn = get_db_conn()
        with conn.cursor() as cursor:
            # 將該 id 的菜單設置為完成
            sql = """
            UPDATE exercise_plan
            SET Status = 'Done', Completed_Date = %s
            WHERE Plan_ID = %s
            """
            cursor.execute(sql, (today, int(plan_id)))
            conn.commit()
    except Exception as e:
        return str(e)
    finally:
        conn.close()

    return jsonify({'success': True}), 200

# 菜單編輯頁面
@app.route('/update_plan', methods=['POST'])
def update_plan():
    data = request.json
    plan_id = data['plan_id']
    weight = data['weight']
    set = data['set']

    try:
        conn = get_db_conn()
        with conn.cursor() as cursor:
            sql = """
            UPDATE exercise_plan
            SET Weight = %s, `Set` = %s
            WHERE Plan_ID = %s
            """
            cursor.execute(sql, (weight, set, plan_id))
            conn.commit()
    except Exception as e:
        return str(e)
    finally:
        conn.close()
    
    return jsonify({'success': True})

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

# 會員專區生成器材報告
@app.route('/member/report')
def report():
    try:
        conn = get_db_conn()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT
                Name,
                (MAX(CAST(Weight AS UNSIGNED)) - MIN(CAST(Weight AS UNSIGNED))) as difference
            FROM exercise_plan AS ep JOIN equipment AS eq
            ON ep.Equipment_ID = eq.Equipment_ID
            AND ep.Equipment_ID < 5100
            WHERE User_ID = %s
            GROUP BY Name
            ORDER BY difference DESC
            LIMIT 3
            """
            cursor.execute(sql, (int(session['id'])))
            results = cursor.fetchall()
            
            name = []
            differences = []

            for row in results:
                name.append(row['Name'])
                differences.append(row['difference'])

            plt.figure(figsize=(8, 5))
            plt.bar(name, differences, color=['red', 'green', 'blue'])

            plt.title('Top 3 進步器材', size=20)
            plt.xlabel('器材名稱', size=15)
            plt.ylabel('進步幅度 (kg)', size=15)

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)

            response = make_response(buf.read())
            response.headers['Content-Type'] = 'image/png'
            response.headers['Content-Disposition'] = 'inline; filename=plot.png'
            return response
    except Exception as e:
        return(str(e))
    finally:
        conn.close()

# 會員專區生成健身熱圖
@app.route('/member/calendar')
def calendar():
    try:
        conn = get_db_conn()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT DISTINCT(Completed_Date) AS date
            FROM exercise_plan
            WHERE Status = 'Done'
            AND User_ID = %s
            """
            cursor.execute(sql, (int(session['id'])))
            results = cursor.fetchall()
            
            # 創建 DataFrame 並確保日期格式正確
            data = pd.DataFrame(results)
            data['date'] = pd.to_datetime(data['date'])

            # 設定月份範圍
            month_start = '2024-05-08'
            month_end = '2024-06-9'
            
            # 創建一個新的 DataFrame 來標記有/無健身
            all_dates = pd.date_range(start=month_start, end=month_end, freq='D')
            data_new = pd.DataFrame(all_dates, columns=['日期'])
            data_new['有/無健身'] = data_new['日期'].isin(data['date']).astype(int)

            # 確保案日期排序
            data_new = data_new.sort_values(by='日期')

            # 將日期轉為時間和週數
            data_new['Weekday'] = data_new['日期'].dt.weekday
            data_new['Week'] = data_new['日期'].dt.isocalendar().week

            # 計算每周的開始日期
            data_new['Week_Start'] = data_new['日期'] - pd.to_timedelta(data_new['Weekday'], unit='D')
            week_start_mapping = data_new.drop_duplicates(subset='Week')[['Week', 'Week_Start']].set_index('Week')['Week_Start']

            # 創建透視表
            pivot_table_new = data_new.pivot(index='Week', columns='Weekday', values='有/無健身').fillna(0)

            # 補全缺少的列（如果某个月沒有從周一開始或從周日結束）
            for col in range(7):
                if col not in pivot_table_new.columns:
                    pivot_table_new[col] = 0
            pivot_table_new = pivot_table_new.sort_index(axis=1)

            # 繪製二元日曆熱圖
            fig, ax = plt.subplots(figsize=(10, 6))
            cmap = mcolors.ListedColormap(['white', 'lightgreen'])
            cax = ax.matshow(pivot_table_new, cmap=cmap, aspect='auto', vmin=0, vmax=1)

            # 設置軸標籤
            ax.set_xticks(np.arange(7))
            ax.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
            ax.set_yticks(np.arange(len(pivot_table_new.index)))
            ax.set_yticklabels([week_start_mapping[week].strftime('%Y-%m-%d') for week in pivot_table_new.index])

            # 添加色條
            cbar = fig.colorbar(cax, ticks=[0, 1])
            cbar.set_label('是否健身', size=15)

            # 添加標題
            plt.title('健身二元日曆圖', pad=20, size=15)

            # 傳送圖表到前端
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)

            response = make_response(buf.read())
            response.headers['Content-Type'] = 'image/png'
            response.headers['Content-Disposition'] = 'inline; filename=plot.png'
            return response
    except Exception as e:
        return(str(e))
    finally:
        conn.close()

# 介紹頁面
@app.route('/intro')
def intro():
    return render_template('introduction.html')

if __name__ == '__main__':
    app.run(debug=True)
