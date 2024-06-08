from flask import Flask, send_file, make_response
import matplotlib.pyplot as plt
import pymysql
import pymysql.cursors
import io

app = Flask(__name__)
plt.rc('font', family='Microsoft JhengHei')

def get_db_conn():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='password',
        database='mydb'
    )
    return conn

def create_plot():
    try:
        conn = get_db_conn()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT
                Name,
                (MAX(CAST(Weight AS UNSIGNED)) - MIN(CAST(Weight AS UNSIGNED))) as difference
            FROM exercise_plan AS ep JOIN equipment AS eq
            ON ep.Equipment_ID = eq.Equipment_ID
            WHERE User_ID = 111306057
            GROUP BY Name
            ORDER BY difference DESC
            LIMIT 3
            """
            cursor.execute(sql)
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
            return buf
    except Exception as e:
        print(str(e))
    finally:
        conn.close()

@app.route('/')
def plot():
    buf = create_plot()
    buf = create_plot()
    response = make_response(buf.read())
    response.headers['Content-Type'] = 'image/png'
    response.headers['Content-Disposition'] = 'inline; filename=plot.png'
    return response

if __name__ == '__main__':
    app.run(debug=True)
