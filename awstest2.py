import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import requests
import boto3
from io import StringIO
# AWS S3 配置

# csv_url = 'https://raw.githubusercontent.com/dap-i/ccps-Projekt/5bcf6a37fbea16d4e1f3ccf1604000defde71e97/ProbeWurf.CSV'
# df = pd.read_csv(csv_url)
S3_BUCKET = 'basketball-vorhersagen'
S3_FOLDER = "Wurfdaten"
AWS_REGION = 'eu-central-1'
AWS_ACCESS_KEY = 'AKIAXE4YQWX4TRCRAGF3'
AWS_SECRET_KEY = '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'
imageurl = 'https://github.com/dap-i/ccps-Projekt/blob/main/southeast.jpg?raw=true'
response = requests.get(imageurl, stream=True)
# 创建 S3 客户端
s3_client = boto3.client('s3',
                         region_name=AWS_REGION,
                         aws_access_key_id=AWS_ACCESS_KEY,
                         aws_secret_access_key=AWS_SECRET_KEY)

response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_FOLDER)
file_list = [obj["Key"] for obj in response.get("Contents", [])]
app_mode = st.sidebar.selectbox('Wählen Sie die anzuzeigenden Daten aus', ['Einzelwurf','alle Wurfe'])
#if "df" not in st.session_state:
    #st.session_state.df = None
##############################################
if app_mode == 'Einzelwurf':
 st.title("Wurfvorhersage des Basketball")
 selected_file = st.selectbox("Wahl welche Datei", file_list, index=1)
 if selected_file:
    # 构建完整的文件路径

    file_path = f"s3://{S3_BUCKET}/{selected_file}"

    response = s3_client.get_object(Bucket=S3_BUCKET, Key=selected_file)
    file_content = response["Body"].read().decode()
    df = pd.read_csv(StringIO(file_content), header=None)
    st.session_state.df = df

    st.write("Basketball-Aufprallpunkt vorhersagen")
    # data-pd.read_csv

    Troffe = st.session_state.df.iloc[0, 0]
    X_p = 0
    Y_p = 0
    Getroffen_wahrscheinlichkeit = st.session_state.df.iloc[0, 0]*100
    KI_vorschlag = 0
    if len(df) > 0:
        if len(df.columns) > 1:
            X_p = st.session_state.df.iloc[0, 1]
            Y_p = st.session_state.df.iloc[0, 2]
            Getroffen_wahrscheinlichkeit = st.session_state.df.iloc[0, 0]
            KI_vorschlag = st.session_state.df.iloc[0, 4]

    getroffe_text = 'nein'
    if Troffe == 1:
        getroffe_text = 'JA'

    st.write(pd.DataFrame({
        'getroffen/nicht': [getroffe_text],
        'X-Position': [X_p],
        'Y-Position': [Y_p],
        'Getroffen_wahrscheinlichkeit:': [Getroffen_wahrscheinlichkeit]
    }))
    # 下载图片
    response = requests.get(imageurl, stream=True)
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
    st.write('Wahrscheinlichkeit des Treffers :', Getroffen_wahrscheinlichkeit, '%')


    fig, ax = plt.subplots()
    ax.pie([Getroffen_wahrscheinlichkeit, 100 - Getroffen_wahrscheinlichkeit], labels=['Getroffen', 'verfehlt'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)
    #KI vorschlag
    vorschlag_mapping = {
        'LO': 'nach Links und Oben',
        'LU': 'nach Links und Unter',
        'RO': 'nach Rechts und Oben',
        'RU': 'nach Rechts und Unter',
        'L': 'nach Links',
        'R': 'nach Rechts',
        'U': 'nach Unter',
        'O': 'nach Oben',
        0: 'Kein Vorschlag'
    }

    if KI_vorschlag in vorschlag_mapping:
        vorschlag_text = f'Vorschlag für Wurfverbesserung: {vorschlag_mapping[KI_vorschlag]}'
        st.write(vorschlag_text)
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

    if Troffe == 1:
        st.success("Super, getroffen")
    elif Troffe == 0:
        st.info("schade!")
  ###########################################################
elif app_mode == 'alle Wurfe':

    dfs = []  # 用于存储每个文件的 DataFrame
    file_paths = file_list[1:]
    header = ['Getroffen/nicht', 'X-Position', 'Y-Position', 'Getroffen_wahrscheinlichkeit', 'KI-Vorschlag']
    st.write([file_paths])
    for file_path in file_paths:
        # 构建完整的文件路径
        s3_file_path = f"s3://{S3_BUCKET}/{file_path}"

        print("File path:", s3_file_path)

        # 读取文件并将其转换为 DataFrame
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=file_path)
        file_content = response["Body"].read().decode()
        
        # 检查文件内容是否为空字符串
        if file_content.strip():
            df = pd.read_csv(StringIO(file_content), header=None)            
            df['X-Position'] = [0]
            df['Y-Position'] = [0]
            df['Getroffen_wahrscheinlichkeit'] = [0]
            df['KI-Vorschlag'] = [0]
            dfs.append(df)
            st.dataframe(df)
        else:
            print(f"Skipped empty file: {s3_file_path}")

    # 设置 DataFrame 的列名

        #
    if dfs:
        
        combined_df = pd.concat(dfs, ignore_index=True)
        num_columns = 5  # 设置表格的列数
        num_rows = len(combined_df)
        columns_to_add = num_columns - combined_df.shape[1]
        if columns_to_add > 0:
           additional_columns = pd.DataFrame(0, columns=[f"Column{i + 1}" for i in range(columns_to_add)],
                                                  index=combined_df.index)         
           combined_df.columns = header
           combined_df = pd.concat([combined_df, additional_columns], axis=1)
           combined_df.columns = [f"Column{i + 1}" for i in range(num_columns)]
          
           st.write(combined_df)
    else:
            st.write("No valid data found in the selected files.")

    getroffen_count = len(combined_df[combined_df.iloc[:, 0] != 0])

    # 计算总行数
    total_rows = len(combined_df)

    # 计算比例
    ratio = getroffen_count / total_rows

    st.write('Gesamtzahl der Korbtreffer ist', getroffen_count)
    st.write('Treffergenauigkeit ist', ratio*100, '%')


    fig, ax = plt.subplots()
    ax.pie([ratio*100, 100 - ratio*100], labels=['Getroffen', 'verfehlt'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)
    #KI vorschlag

    response = requests.get(imageurl, stream=True)
    background_image = Image.open(response.raw)
    background_array = np.array(background_image)
  
    #x_coords = combined_df.iloc[:, 1]
    #y_coords = combined_df.iloc[:, 2]
    x = np.random.randint(0, 5, size=50)
    y = np.random.randint(0,4, size=50)

    fig, ax = plt.subplots(figsize=(7,4))
    plt.hist2d(x,y, bins=[np.arange(0,6,1),np.arange(0,5,1)], alpha=0.4)
    plt.colorbar()
    ax.imshow(background_array, extent=[0, 7, 0, 4], aspect='auto')
    plt.show()
    # heatmap_data = pd.crosstab(x_coords, y_coords)
    # response = requests.get(imageurl, stream=True)
    # background_image = Image.open(response.raw)

    # background_array = np.array(background_image)

    # # 调整热图的大小以适应背景图片
    

    # # 绘制热图并将背景图片叠加在上面
    # sns.heatmap(heatmap_data, cmap='hot', cbar=True, square=True, annot=True, ax=ax)
    # heatmap = ax.collections[0]
    # heatmap.set_alpha(0.4)

    # ax.invert_yaxis()
    # plt.gca().set_aspect('equal', adjustable='box')
    # extent = [0, background_array.shape[0], 0, background_array.shape[1]]
    # ax.imshow(background_array, extent=[1, 5, 1, 4], aspect='auto', alpha=0.4)
    # # 设置轴标签和标题
    # plt.xlabel('Y Coordinate')
    # plt.ylabel('X Coordinate')
    # plt.title('Basketball Hit Frequency')

    # # 显示热图
    st.pyplot(fig)

