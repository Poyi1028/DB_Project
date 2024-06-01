import datetime as dt
import matplotlib.pyplot as plt
import numpy as np


def main():
    # 生成日期和數據
    dates, data = generate_data()
    # 創建圖形和軸
    fig, ax = plt.subplots(figsize=(6, 10))
    # 繪製日曆熱圖
    calendar_heatmap(ax, dates, data)
    # 顯示圖形
    plt.show()


def generate_data():
    # 生成100個隨機數據
    num = 100
    data = np.random.randint(0, 20, num)
    # 設定開始日期
    start = dt.datetime(2015, 3, 13)
    # 生成從開始日期起的連續日期列表
    dates = [start + dt.timedelta(days=i) for i in range(num)]
    return dates, data


def calendar_array(dates, data):
    # 將日期轉換為ISO日曆（年、週、日）的週和日
    i, j = zip(*[d.isocalendar()[1:] for d in dates])
    i = np.array(i) - min(i)
    j = np.array(j) - 1
    ni = max(i) + 1

    # 初始化日曆數組，並填入數據
    calendar = np.nan * np.zeros((ni, 7))
    calendar[i, j] = data
    return i, j, calendar


def calendar_heatmap(ax, dates, data):
    # 生成日曆數組
    i, j, calendar = calendar_array(dates, data)
    # 繪製熱圖
    im = ax.imshow(calendar, interpolation='none', cmap='summer')
    # 標註天數
    label_days(ax, dates, i, j, calendar)
    # 標註月份
    label_months(ax, dates, i, j, calendar)
    # 添加顏色條
    ax.figure.colorbar(im)


def label_days(ax, dates, i, j, calendar):
    # 獲取日曆數組的形狀
    ni, nj = calendar.shape
    # 初始化日曆中的每一天
    day_of_month = np.nan * np.zeros((ni, 7))
    day_of_month[i, j] = [d.day for d in dates]

    # 在每一天的位置標註日期
    for (i, j), day in np.ndenumerate(day_of_month):
        if np.isfinite(day):
            ax.text(j, i, int(day), ha='center', va='center')

    # 設定軸標籤
    ax.set(xticks=np.arange(7),
           xticklabels=['M', 'T', 'W', 'R', 'F', 'S', 'S'])
    ax.xaxis.tick_top()


def label_months(ax, dates, i, j, calendar):
    # 定義月份標籤
    month_labels = np.array(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
                             'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    # 獲取日期中的月份
    months = np.array([d.month for d in dates])
    # 獲取唯一的月份
    uniq_months = sorted(set(months))
    # 計算每個月份的平均位置，用於在y軸上標註月份
    yticks = [i[months == m].mean() for m in uniq_months]
    # 對應的月份標籤
    labels = [month_labels[m - 1] for m in uniq_months]
    # 設定y軸標籤
    ax.set(yticks=yticks)
    ax.set_yticklabels(labels, rotation=90)


# 執行主函數
main()
