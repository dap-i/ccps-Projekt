import streamlit as st
from st_files_connection import FilesConnection
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import requests
import seaborn as sns

# Create connection object and retrieve file contents.
# Specify input format is a csv and to cache the result for 600 seconds.
conn = st.experimental_connection('s3', type=FilesConnection)
df = conn.read("basketball-vorhersagen/ProbeWurf.csv", input_format="csv", ttl=600)

#AWS_ACCESS_KEY_ID = 'YOUR_ACCESS_KEY_ID'
#AWS_SECRET_ACCESS_KEY = 'YOUR_SECRET_ACCESS_KEY'
#BUCKET_NAME = 'YOUR_BUCKET_NAME'
#FILE_NAME = 'YOUR_FILE_NAME.csv'


#s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
#CSV datei

#uploaded_file = st.file_uploader("Wähl eine CSVdatei zu hochladen", type="csv")
#if uploaded_file is not None:

#csv_url = 'https://raw.githubusercontent.com/dap-i/ccps-Projekt/5bcf6a37fbea16d4e1f3ccf1604000defde71e97/ProbeWurf.CSV'
#df = pd.read_csv(csv_url)
num_rows = df.shape[0]

st.title("Wurfvorhersage des Basketball")

url = 'https://img95.699pic.com/xsj/19/zz/1o.jpg!/fw/700/watermark/url/L3hzai93YXRlcl9kZXRhaWwyLnBuZw/align/southeast'
response = requests.get(url, stream=True)

app_mode = st.sidebar.selectbox('Wählen Sie die anzuzeigenden Daten aus', ['Einzelwurf','alle Wurfe'])

if app_mode == 'Einzelwurf':
    st.write("Basketball-Aufprallpunkt vorhersagen")
    # data-pd.read_csv
    selected_row = st.selectbox("Wähl welche Wurf anzuzeigen", range(1, num_rows+1))
    selected_row -= 1
    # 显示选择的行数据
    Wurfzahl = df.iloc[selected_row, 0]
    X_p = df.iloc[selected_row, 1]
    Y_p = df.iloc[selected_row, 2]
    Getroffen_wahrscheinlichkeit = df.iloc[selected_row, 4]
    KI_vorschlag = df.iloc[selected_row, 5]
    if Getroffen_wahrscheinlichkeit <= 70:
        Ball = 2
    else:
        Ball = 1

    st.write(pd.DataFrame({
        'Wurfzahl': [Wurfzahl],
        'X-Position': [X_p],
        'Y-Position': [Y_p]
    }))
    # 下载图片
    response = requests.get(url, stream=True)
    background_image = Image.open(response.raw)
    # 转换成 NumPy 数组
    background_array = np.array(background_image)
    # 绘制网格
    fig, ax = plt.subplots(4, 5, figsize=(3,2))
    # 将图像切割成 4x5 网格中的块，并将每个块分配给对应的 Axes 对象
    x_blocks = np.array_split(background_array, 5, axis=1)
    blocks = [np.array_split(block, 4, axis=0) for block in x_blocks]

    for i in range(4):
        for j in range(5):
            ax[i][j].imshow(blocks[j][i])
            ax[i][j].axis('off')
    # 数据坐标
    data_coords = [(X_p-1, Y_p-1)]
    # 更改对应坐标的网格颜色
    for coord in data_coords:
        row, col = coord
    if (row, col) == data_coords[0]:
        ax[row][col].text(0.5, 0.5, 'hit!', fontsize=20, ha='center', va='center',transform=ax[row][col].transAxes, color='red')
        print("r",row,"c",col)
    st.pyplot(fig)
    #getroffenwahrscheinlichkeit
    st.write('Getroffenwahrscheinlichkeit ist :', Getroffen_wahrscheinlichkeit, '%')


    fig, ax = plt.subplots()
    ax.pie([Getroffen_wahrscheinlichkeit, 100 - Getroffen_wahrscheinlichkeit], labels=['Getroffen', 'verfehlt'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)
    #KI vorschlag
    if KI_vorschlag =='LO':
        st.write('Vorschlag für Wurfverbesserung : nach Links und Oben')
    if KI_vorschlag =='LU':
        st.write('Vorschlag für Wurfverbesserung : nach Links und Unter')
    if KI_vorschlag =='RO':
        st.write('Vorschlag für Wurfverbesserung : nach Rechts und Oben')
    if KI_vorschlag =='RU':
        st.write('Vorschlag für Wurfverbesserung : nach Rechts und Unter')
    if KI_vorschlag == 'L':
        st.write('Vorschlag für Wurfverbesserung : nach Links ')
    if KI_vorschlag == 'R':
        st.write('Vorschlag für Wurfverbesserung : nach Rechts ')
    if KI_vorschlag == 'U':
        st.write('Vorschlag für Wurfverbesserung : nach Unter ')
    if KI_vorschlag == 'O':
        st.write('Vorschlag für Wurfverbesserung : nach Oben ')
    #with st.container():
    #    background_Image=Image.open(response.raw)
    #    st.markdown(f'<style>div.stContainer {{background-image: url("{background_Image}");}}</style>',unsafe_allow_html=True)
    #    cols = st.columns(4)
    #   count = 0
    #    for col in cols:
    #        for row in range(5):
                # 创建一个空白按钮作为网格单元格
    #            cell_key = f"{row}-{col.index}-{count}"
    #            count += 1
    #            cell = col.button("", key=cell_key)
    #            # 检查数据坐标是否在该单元格内，并在该单元格内高亮
    #            print("r",row,"c",col._positional_key,"key",cell_key)
    #            if row == data_y and col._positional_key == data_x:
    #                cell = col.button("", key=cell_key, help="highlighted", style={"background-color": "yellow"})
    #                print("counter=", count)

    if Ball == 1:
        st.success("Bingo!ein Tor schießen")
    elif Ball == 2:
        st.info("schade!")

elif app_mode == 'alle Wurfe':
    st.write("Daten von alle Wurfe")
    column_names = ['Wurfzahl', 'X-Position', 'Y-Position', '/', 'Getroffen', 'Vorschlag']  # 根据实际情况自定义列名

    # 设置DataFrame的列名
    df.columns = column_names

    # 显示DataFrame
    st.write(df)

    x_coords = df.iloc[:, 1]
    y_coords = df.iloc[:, 2]
    heatmap_data = pd.crosstab(x_coords, y_coords)
    response = requests.get(url, stream=True)
    background_image = Image.open(response.raw)

    background_array = np.array(background_image)

    # 调整热图的大小以适应背景图片
    fig, ax = plt.subplots(figsize=(heatmap_data.shape[1], heatmap_data.shape[0]))

    # 绘制热图并将背景图片叠加在上面
    sns.heatmap(heatmap_data, cmap='hot', cbar=True, square=True, annot=True, ax=ax)
    heatmap = ax.collections[0]
    heatmap.set_alpha(0.4)

    ax.invert_yaxis()
    plt.gca().set_aspect('equal', adjustable='box')
    extent = [0, background_array.shape[0], 0, background_array.shape[1]]
    ax.imshow(background_array, extent=[1, 5, 1, 4], aspect='auto', alpha=0.4)
    # 设置轴标签和标题
    plt.xlabel('Y Coordinate')
    plt.ylabel('X Coordinate')
    plt.title('Basketball Hit Frequency')

    # 显示热图
    st.pyplot(fig)

