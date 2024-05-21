import pymysql
from flask import Flask, request, jsonify,render_template

app = Flask(__name__)

# MySQL 連接
def get_data():
    conn = pymysql.connect(host='localhost', user='root', password='sw0217', database='mydb')
    return conn

@app.route('/')
def index():
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
