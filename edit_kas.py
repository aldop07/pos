import streamlit as st
import mysql.connector
import pandas as pd


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
    query = 'DELETE FROM kas WHERE id = %s'
    cursor = cnx.cursor()
    cursor.execute(query, (id,))
    cnx.commit()
    st.success('Produk berhasil dihapus')
if st.button('edit'):
    cursor = cnx.cursor()
    query = "UPDATE id SET id = %s, kas_awal WHERE id = %s"
    cursor.execute(query, (id, jumlah_kas))
    cnx.commit()
