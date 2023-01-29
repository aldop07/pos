import streamlit as st
import mysql.connector
import pandas as pd
import numpy as np


# Koneksi ke database MySQL
cnx = mysql.connector.connect(
    user='sql12593622',
    password='TNebtWsD1w',
    host='sql12.freesqldatabase.com',
    database='sql12593622'
)
cursor = cnx.cursor()
query = 'SELECT id, kas_awal FROM kas'
df = pd.read_sql(query, cnx)
df = df.sort_values(by='id', ascending=False)
st.dataframe(df)
id = st.selectbox("Id Produk", df['id'].tolist())
jumlah_kas = st.number_input("Kas",value=df.loc[df['id'] == id, 'kas_awal'].values[0])

if st.button('Hapus'):
    cursor = cnx.cursor()
    query = 'DELETE FROM kas WHERE id = %s'
    cursor.execute(query, (id,))
    cnx.commit()
    st.success('Produk berhasil dihapus')
    
if st.button('Edit'):
    cursor = cnx.cursor()
    query = "UPDATE kas SET kas_awal = %s WHERE id = %s"
    cursor.execute(query, (jumlah_kas,))
    cnx.commit()
    st.success('Data berhasil diperbarui')
    
