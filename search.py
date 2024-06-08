import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pymysql
import calendar

def get_db_conn():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='password',
        database='mydb'
    )
    return conn

try:
    conn = get_db_conn()
    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
        sql = """
        SELECT DISTINCT(Completed_Date) AS date
        FROM exercise_plan
        WHERE Status = 'Done'
        AND User_ID = 111306057
        """
        cursor.execute(sql)
        results = cursor.fetchall()
        
        # 创建DataFrame并确保日期格式正确
        data = pd.DataFrame(results)
        data['date'] = pd.to_datetime(data['date'])

        # 设定月份范围（例如2024年6月）
        month_start = '2024-05-01'
        month_end = '2024-06-1'
        
        # 创建一个新的DataFrame来标记有/无健身
        all_dates = pd.date_range(start=month_start, end=month_end, freq='D')
        data_new = pd.DataFrame(all_dates, columns=['日期'])
        data_new['有/無健身'] = data_new['日期'].isin(data['date']).astype(int)

        # 确保按日期排序
        data_new = data_new.sort_values(by='日期')

        # 将日期转换为星期和周数
        data_new['Weekday'] = data_new['日期'].dt.weekday
        data_new['Week'] = data_new['日期'].dt.isocalendar().week

        # 计算每周的开始日期
        data_new['Week_Start'] = data_new['日期'] - pd.to_timedelta(data_new['Weekday'], unit='D')
        week_start_mapping = data_new.drop_duplicates(subset='Week')[['Week', 'Week_Start']].set_index('Week')['Week_Start']

        # 创建透视表
        pivot_table_new = data_new.pivot(index='Week', columns='Weekday', values='有/無健身').fillna(0)

        # 补全缺少的列（如果某个月没有从周一开始或没有到周日结束）
        for col in range(7):
            if col not in pivot_table_new.columns:
                pivot_table_new[col] = 0
        pivot_table_new = pivot_table_new.sort_index(axis=1)

        # 绘制二元日历热图
        fig, ax = plt.subplots(figsize=(10, 6))
        cmap = mcolors.ListedColormap(['lightgray', 'lightgreen'])
        cax = ax.matshow(pivot_table_new, cmap=cmap, aspect='auto', vmin=0, vmax=1)

        # 设置轴标签
        ax.set_xticks(np.arange(7))
        ax.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
        ax.set_yticks(np.arange(len(pivot_table_new.index)))
        ax.set_yticklabels([week_start_mapping[week].strftime('%Y-%m-%d') for week in pivot_table_new.index])

        # 添加色条
        cbar = fig.colorbar(cax, ticks=[0, 1])
        cbar.set_label('Gym Visit')

        # 添加标题
        plt.title('Gym Visit Binary Calendar Heatmap', pad=20)

        # 显示图表
        plt.show()
except Exception as e:
    print(str(e))
finally:
    conn.close()
