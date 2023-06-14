import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import requests

st.title("Wurfvorhersage des Basketball")

url = 'https://img95.699pic.com/xsj/19/zz/1o.jpg!/fw/700/watermark/url/L3hzai93YXRlcl9kZXRhaWwyLnBuZw/align/southeast'

response = requests.get(url, stream=True)

app_mode = st.sidebar.selectbox('Wählen Sie die anzuzeigenden Daten aus', ['Einzelwurf','alle Wurfe'])

if app_mode == 'Einzelwurf':
    st.write("Basketball-Aufprallpunkt vorhersagen")
    # data-pd.read_csv

    st.write(pd.DataFrame({
        'X-Position': [3],
        'Y-Position': [2]
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
    data_coords = [(2, 3)]
    Ball = 2

    # 更改对应坐标的网格颜色
    for coord in data_coords:
        row, col = coord
    if (row, col) == data_coords[0]:
        ax[row][col].text(0.5, 0.5, 'hit!', fontsize=20, ha='center', va='center',transform=ax[row][col].transAxes, color='red')
        print("r",row,"c",col)
    # 将网格显示在 Streamlit
    st.pyplot(fig)


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
    data = np.random.rand(5,6)
    fig, ax = plt.subplots()
    im = ax.imshow(data,alpha=0.3)
    response = requests.get(url, stream=True)
    background_image = Image.open(response.raw)
    background_array = np.array(background_image)

    ax.imshow(background_array, extent=[0.1, 5, 0, 4], alpha=1, zorder=-1)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            text = ax.text(j, i, f'{data[i, j]:.2f}', ha='center', va='center', color='Black')
    st.pyplot(fig)
    # 设置字体大小和边框样式
    Score = 42
    desc1 = "getroffen Anzahl:"

    st.write(f"### {desc1}")
    st.write(f"**{Score}**")
    desc2 = "Record von Wurfversuch:"
    st.write(f"### {desc2}")
    df = pd.DataFrame({'Anzahl der Wurfversuche': [i + 1 for i in range(20)],
                       'X-Position': [0 for _ in range(20)],
                       'Y-Position': [0 for _ in range(20)],
                       'Korb/nicht': ['JA' for _ in range(20)]})

    # 显示表格
    st.table(df)


