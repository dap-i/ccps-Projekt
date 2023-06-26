import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import requests
import boto3
from io import StringIO
#Zugriffsschlüssel
S3_BUCKET = 'basketball-vorhersagen'
S3_FOLDER = "Wurfdaten"
AWS_REGION = 'eu-central-1'
AWS_ACCESS_KEY = 'AKIAXE4YQWX4TRCRAGF3'
AWS_SECRET_KEY = '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'
# S3Klient erstellen
s3_client = boto3.client('s3',
                         region_name=AWS_REGION,
                         aws_access_key_id=AWS_ACCESS_KEY,
                         aws_secret_access_key=AWS_SECRET_KEY)
response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_FOLDER)
file_list = [obj["Key"] for obj in response.get("Contents", [])]
imageurl = 'https://github.com/dap-i/ccps-Projekt/blob/main/southeast.jpg?raw=true'
app_mode = st.sidebar.selectbox('Wählen Sie die anzuzeigenden Daten aus', ['Einzelwurf','alle Wurfe'])
#if "df" not in st.session_state:
    #st.session_state.df = None
##############################################
if app_mode == 'Einzelwurf':
 st.title("Wurfvorhersage des Basketball")
 selected_file = st.selectbox("Wahl welche Datei", file_list, index=1)
 if selected_file:
    # Datei-Pfad
    file_path = f"s3://{S3_BUCKET}/{selected_file}"
    response = s3_client.get_object(Bucket=S3_BUCKET, Key=selected_file)
    file_content = response["Body"].read().decode()
    df = pd.read_csv(StringIO(file_content), header=None)
    st.session_state.df = df
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
      
    #Treffenposition
    st.write("Probe-Aufprallposition")
    response = requests.get(imageurl, stream=True)
    background_image = Image.open(response.raw)
    # in Numpy Konvertieren
    background_array = np.array(background_image)
    fig, ax = plt.subplots(4, 5, figsize=(3,2))
    # Schneiden die Grafik in 4x5 und verteilen
    x_blocks = np.array_split(background_array, 5, axis=1)
    blocks = [np.array_split(block, 4, axis=0) for block in x_blocks]
    for i in range(4):
        for j in range(5):
            ax[i][j].imshow(blocks[j][i])
            ax[i][j].axis('off')
    data_coords = [(2, 2)]
    for coord in data_coords:
        row, col = coord
    if (row, col) == data_coords[0]:
        ax[row][col].text(0.5, 0.5, 'hit!', fontsize=20, ha='center', va='center',transform=ax[row][col].transAxes, color='red')
        print("r",row,"c",col)
    st.pyplot(fig)

    st.write("Probe KI-Normalverteilung für Aufprallposition")
    #x_coords = combined_df.iloc[:, 1]
    #y_coords = combined_df.iloc[:, 2]
    x_n = np.random.normal(loc=2, scale=1.0, size=5000)
    y_n = np.random.normal(loc=2, scale=1.0, size=5000)

    fig, ax = plt.subplots(figsize=(8,4))
    plt.hist2d(x_n,y_n, bins=[np.arange(0,6,1),np.arange(0,5,1)], alpha=0.4)
    plt.colorbar()
    ax.imshow(background_array, extent=[0, 5, 0, 4], aspect='auto')
    plt.show()
    st.pyplot(fig)
   
    if Troffe == 1:
        st.success("Super, getroffen")
    elif Troffe == 0:
        st.info("schade!")
  ###########################################################
elif app_mode == 'alle Wurfe':
    # DataFrame für jeder Datei zu speichern
    dfs = []  
    file_paths = file_list[1:]
    st.write([file_paths])
    for file_path in file_paths:
        s3_file_path = f"s3://{S3_BUCKET}/{file_path}"
        print("File path:", s3_file_path)
        # Datei lesen und konvertieren zu DataFrame
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=file_path)
        file_content = response["Body"].read().decode()    
        # prüfung ob die Datei leer ist
        if file_content.strip():
            df = pd.read_csv(StringIO(file_content), header=None)            
            dfs.append(df)         
        else:
            print(f"Skipped empty file: {s3_file_path}")
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        num_columns = 5  
        num_rows = len(combined_df)
        columns_to_add = num_columns - combined_df.shape[1]
        if columns_to_add > 0:
           additional_columns = pd.DataFrame(0, columns=[f"Column{i + 1}" for i in range(columns_to_add)],
                                                  index=combined_df.index)
           combined_df = pd.concat([combined_df, additional_columns], axis=1)
           combined_df.columns = [f"Column{i + 1}" for i in range(num_columns)]
           header = ['Getroffen/nicht', 'X-Position', 'Y-Position', 'Getroffen_wahrscheinlichkeit', 'KI-Vorschlag']
           combined_df.columns = header
           combined_df = combined_df.reindex(range(num_rows), fill_value=0)
           st.dataframe(combined_df)
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
    st.write("Probe-Heatmap für Aufprallposition")
    #x_coords = combined_df.iloc[:, 1]
    #y_coords = combined_df.iloc[:, 2]
    x = np.random.randint(0, 5, size=50)
    y = np.random.randint(0,4, size=50)

    fig, ax = plt.subplots(figsize=(8,4))
    plt.hist2d(x,y, bins=[np.arange(0,6,1),np.arange(0,5,1)], alpha=0.4)
    plt.colorbar()
    ax.imshow(background_array, extent=[0, 5, 0, 4], aspect='auto')
    plt.show()
  
    st.pyplot(fig)

