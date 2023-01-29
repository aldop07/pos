import streamlit as st
import sqlite3
import time
import numpy as np
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import plotly.express as px
from mlxtend.frequent_patterns import apriori, association_rules

#   IRFAN NOVALDO HUANG

# Koneksi ke database MySQL
cnx = mysql.connector.connect(
    user='sql12593622',
    password='TNebtWsD1w',
    host='sql12.freesqldatabase.com',
    database='sql12593622'
)

# Buat titit
icon = 'https://e7.pngegg.com/pngimages/263/96/png-clipart-hijab-islam-islamic-background-brown-food-thumbnail.png'
st.set_page_config(page_title="Point Of Sale", page_icon=icon, layout="wide")

st.title('Aplikasi Point Of Sale')
# Buat sidebar dan menu dropdown
st.sidebar.header('Menu') 
menu = st.sidebar.selectbox('', ['Dokumentasi','Daftar Produk', 'Tambah Produk', 'Tambah Transaksi', 'Tambah Pengeluaran', 'Laba', 'Riwayat Transaksi','Data Mining'])
# Tampilan menu Dokumentasi
if menu == 'Dokumentasi':
    st.header('Dokumentasi')
    st.info('Baca jurnal berikut terlebih dahulu')
    st.write('https://ejournal.bsi.ac.id/ejurnal/index.php/khatulistiwa/article/viewFile/8994/4535')
    st.write('http://jim.teknokrat.ac.id/index.php/sisteminformasi/article/download/368/207')
    st.write('https://jurnal.ulb.ac.id/index.php/informatika/article/view/1381')
    
    st.markdown(':red[Penjelasan dan Rumus]')
    st.write('Dalam Apriori, support digunakan untuk mengukur seberapa sering suatu itemset muncul dalam data transaksi. Rumus untuk menentukan support adalah jumlah transaksi yang mengandung itemset tersebut dibagi dengan total jumlah transaksi.')
    st.markdown(':green[support(I) = (jumlah transaksi yang mengandung itemset I) / (total jumlah transaksi])')
    st.write('Di mana I adalah itemset yang ingin ditentukan support-nya.')
    st.write('Jadi, dengan rumus ini kita dapat menentukan support dari suatu item atau itemset dalam data transaksi dengan menghitung berapa banyak transaksi yang mengandung item atau itemset tersebut dan membaginya dengan total jumlah transaksi.')
    st.write('Rumus untuk menentukan support dari itemset yang terdiri dari 2 item adalah:')
    st.markdown(':green[support(I1, I2) = (jumlah transaksi yang mengandung item I1 dan I2) / (total jumlah transaksi])')
    st.write('Di mana I1 dan I2 adalah 2 item yang digabungkan dalam suatu itemset yang ingin ditentukan support-nya.')
    st.write('Confidence adalah ukuran seberapa sering suatu itemset yang didahului oleh suatu item atau itemset lain muncul dalam data transaksi. Rumus untuk menentukan confidence dari suatu aturan asosiasi I1 -> I2 adalah :')
    st.markdown(':green[Confidence(I1 -> I2) = Support (I1, I2) / Support (I1])')
    st.write('Di mana I1 adalah item atau itemset yang didahului, I2 adalah item atau itemset yang diikuti, Support (I1, I2) adalah support dari itemset yang terdiri dari kedua item atau itemset tersebut, dan Support (I1) adalah support dari item atau itemset yang didahului.')
    #pdf_url = "https://ejournal.bsi.ac.id/ejurnal/index.php/khatulistiwa/article/viewFile/8994/4535"
    kas_input_done = False
    if not kas_input_done:
        cursor = cnx.cursor()
        query = "SELECT MAX(id) FROM kas"
        cursor.execute(query)
        last_id = cursor.fetchone()[0]
        if last_id is None:
            id = 1
        else:
            id = last_id + 1
        kas_start = st.number_input('Masukan Kas Awal',0)
        if st.button('Input Kas'):
            cursor = cnx.cursor()
            query = 'INSERT INTO kas (id, kas_awal) VALUES (%s, %s)'
            cursor.execute(query, (id, kas_start))
            cnx.commit()
            st.success('Kas berhasil disimpan')
            kas_input_done = True
    else:
        st.info('Kas sudah pernah diinput')
    #response = requests.get(pdf_url)
    #with open("temp.pdf", "wb") as f:
    #    f.write(response.content)

    #with fitz.open("temp.pdf") as pdf:
    #    for page in pdf:
    #        pix = page.get_pixmap(alpha=False)
    #        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    #        st.image(img, width=600)

elif menu == 'Daftar Produk':
    st.header('Daftar Produk')
    query = 'SELECT id, nama, harga, stok FROM produk'
    df = pd.read_sql(query, cnx)
    
    # Tampilkan harga dalam bentuk angka dengan tanda titik sebagai pemisah ribuan
    df['harga'] = df['harga'].apply(lambda x: '{:,}'.format(x).replace(',', '.'))

    # Tampilkan stok dalam bentuk angka tanpa desimal
    df['stok'] = df['stok'].apply(lambda x: int(x) if x == x else x)
    col1, col2 = st.columns(2)
    # Tampilkan stok dalam bentuk dataframe
    with col1:
        search = st.text_input('Cari produk', key='search')
        if search:
            df = df[df['nama'].str.contains(search, case=False, na=False)]
        st.dataframe(df,width=1500, height=170)

    # Tampilkan menu edit produk apabila di centang
    edit = st.checkbox('Edit/Hapus Produk')
    if edit :
        query = 'SELECT id, harga_pokok, nama, harga, stok FROM produk'
        df = pd.read_sql(query, cnx)
        produk = st.selectbox("Id Produk", df['id'].tolist())
        nama = st.text_input("Nama Baru",value=df.loc[df['id'] == produk, 'nama'].values[0])
        harga_pokok = st.number_input("Harga Pokok Baru",value=df.loc[df['id'] == produk, 'harga_pokok'].values[0])
        harga = st.number_input("Harga Baru",value=df.loc[df['id'] == produk, 'harga'].values[0])
        stok = st.number_input("Stok Baru",value=df.loc[df['id'] == produk, 'stok'].values[0])

        if st.button("Edit"):
            if nama == "" or harga_pokok == 0 or harga == 0 or stok == 0:
                st.error('Data produk tidak berhasil diubah')
            else:
                # Query untuk mengubah data di tabel produk
                cursor = cnx.cursor()
                query = "UPDATE produk SET harga_pokok = %s, nama = %s, harga = %s, stok = %s WHERE id = %s"
                cursor.execute(query, (harga_pokok, nama, harga, stok, produk))
                cnx.commit()
            
                # Tampilkan pesan sukses
                st.success("Data produk berhasil diubah")
        if st.button("Hapus"):
            query = 'DELETE FROM produk WHERE id = %s'
            cursor = cnx.cursor()
            cursor.execute(query, (produk,))
            cnx.commit()
            st.success('Produk berhasil dihapus')
    #Tampilan menu cek hasil update
    cek_update = st.checkbox('Cek/Hapus Update')
    if cek_update:
       query = 'SELECT id, nama_produk, jumlah_update, tanggal FROM update_produk'
       df = pd.read_sql(query, cnx)
       df = df.sort_values(by='tanggal', ascending=False)
       st.dataframe(df,width=1500, height=100)
       produk = st.selectbox("Id Produk", df['id'].tolist())
       if st.button('Hapus'):
            query = 'DELETE FROM update_produk WHERE id = %s'
            cursor = cnx.cursor()
            cursor.execute(query, (produk,))
            cnx.commit()
            st.success('Produk berhasil dihapus')
        
    with col2:
        # Tambahkan form input untuk mengubah stok produk
        query = 'SELECT id, harga_pokok, nama, harga, stok FROM produk'
        df = pd.read_sql(query, cnx)
        tanggal = st.date_input('Tanggal')
        produk = st.selectbox("Pilih Produk ", df['nama'].tolist())
        stok_produk_baru = st.number_input('Stok Produk',0)

        if st.button('Update'):
            if stok_produk_baru < 1:
                st.error('produk tidak dapat di update')
            else:
                cursor = cnx.cursor()
                query_select = 'SELECT stok FROM produk WHERE nama = %s'
                cursor.execute(query_select, (produk,))
                result = cursor.fetchone()
                stok_lama = result[0]
                stok_baru = stok_lama + stok_produk_baru
                query_update = 'UPDATE produk SET stok = %s WHERE nama = %s'
                cursor.execute(query_update, (stok_baru, produk))

                query = 'SELECT harga_pokok, harga FROM produk WHERE nama = %s'
                cursor.execute(query, (produk,))   
                result = cursor.fetchone()
                harga_pokok = result[0]
                harga_jual = result[1]

                query = "SELECT MAX(id) FROM update_produk"
                cursor.execute(query)
                last_id = cursor.fetchone()[0]
                if last_id is None:
                    id = 1
                else:
                    id = last_id + 1

                query = 'INSERT INTO update_produk (id, tanggal, nama_produk, harga_jual, jumlah_update, jumlah_lama, harga_pokok) VALUES (%s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(query, (id, tanggal, produk, harga_jual, stok_produk_baru, stok_lama,harga_pokok))
                cnx.commit()

                st.success('Stok produk berhasil diupdate')

# Tampilan menu Tambah Produk
elif menu == 'Tambah Produk':
    st.header('Tambah Produk')
    col1, col2 = st.columns(2)
    with col1:
        cursor = cnx.cursor()
        query = "SELECT MAX(id) FROM produk"
        cursor.execute(query)
        last_id = cursor.fetchone()[0]
        if last_id is None:
            id = 1
        else:
            id = last_id + 1
        nama_produk = st.text_input('Nama Produk')
        harga_produk = st.number_input('Harga Jual',0)
    with col2:
        harga_pokok = st.number_input('Harga Pokok',0)
        stok_produk = st.number_input('Stok Produk',0)
    if st.button('Simpan'):
        if nama_produk == "" or harga_pokok < 1000 or harga_produk < 1000 or stok_produk == 0 :
            st.warning('Produk tidak berhasil disimpan')
        else:
            cursor = cnx.cursor()
            query = 'INSERT INTO produk (id, nama, harga, stok, harga_pokok) VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(query, (id, nama_produk, harga_produk, stok_produk, harga_pokok))
            cnx.commit()
            st.success('Produk berhasil disimpan')

# Tampilan menu Tambah Transaksi
elif menu == 'Tambah Transaksi':
    st.header('Tambah Transaksi')
    query = 'SELECT nama, harga, stok FROM produk'
    df = pd.read_sql(query, cnx)
    search = st.text_input('Cari produk', key='search')
    if search:
        df = df[df['nama'].str.contains(search, case=False, na=False)]
    df['harga'] = df['harga'].apply(lambda x: '{:,}'.format(x).replace(',', '.'))
    st.dataframe(df,width=1500, height=140)
    # Ambil data produk dari database MySQL
    query = 'SELECT * FROM produk'
    df = pd.read_sql(query, cnx)
    col1, col2, col3 = st.columns(3)
    # Buat list nama produk untuk dipilih dalam form input transaksi
    with col1:
        cursor = cnx.cursor()
        query = "SELECT MAX(id) FROM transaksi"
        cursor.execute(query)
        last_id = cursor.fetchone()[0]
        if last_id is None:
            id = 1
        else:
            id = last_id + 1
        tanggal = st.date_input('Tanggal')
        nama_pelanggan = st.text_input ('Nama Pelanggan')
    with col2:
        nama_produk = st.multiselect("Pilih Produk ", df['nama'].tolist())
        jumlah_produk = []
        total_harga = 0
    with col2 , col3:
        for produk in nama_produk:
            jumlah = st.number_input(f'Jumlah Produk {produk}',min_value=0)
            jumlah_produk.append(jumlah)
    with col1:
        if st.button('Simpan'):
            if nama_pelanggan == "" or sum(jumlah_produk) == 0 or 0 in jumlah_produk:
                st.warning("Periksa Nama Pelanggan dan Jumlah Produk")
            else:
                # Buat objek cursor
                cursor = cnx.cursor()
                transaksi_berhasil = True
                produk_stok_tidak_mencukupi = []
                for i in range(len(nama_produk)):
                    query = 'SELECT harga, harga_pokok, stok FROM produk WHERE nama = %s;'
                    cursor.execute(query, (nama_produk[i],))
                    result = cursor.fetchone()
                    harga_produk = result[0]
                    harga_pokok = result[1]
                    stok_produk = result[2]
                    total_harga = harga_produk * jumlah_produk[i]
                    if stok_produk >= jumlah_produk[i]:
                        # Tambahkan transaksi baru ke tabel transaksi
                        query = 'INSERT INTO transaksi (id, tanggal, nama_pelanggan, nama, jumlah, harga, harga_pokok, total) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
                        cursor.execute(query, (id, tanggal ,nama_pelanggan, nama_produk[i], jumlah_produk[i], harga_produk, harga_pokok, total_harga))
                        # Kurangi stok produk yang dibeli
                        query = 'UPDATE produk SET stok = stok - %s WHERE nama = %s;'
                        cursor.execute(query, (jumlah_produk[i], nama_produk[i]))
                    else:
                        transaksi_berhasil = False
                        produk_stok_tidak_mencukupi.append(nama_produk[i])

                if transaksi_berhasil:
                    cnx.commit()
                    st.balloons()
                    st.success('Transaksi berhasil disimpan')
                else:
                    cnx.rollback()
                    if len(produk_stok_tidak_mencukupi) == 1:
                        st.error(f'Stok produk {produk_stok_tidak_mencukupi[0]} tidak mencukupi')
                    else:
                        st.error(f'Stok produk {", ".join(produk_stok_tidak_mencukupi)} tidak mencukupi')

# Tampilan menu Tambah Pengeluaran
elif menu == 'Tambah Pengeluaran':
    st.header('Tambah Pengeluaran')
    cursor = cnx.cursor()
    query = "SELECT MAX(id) FROM pengeluaran"
    cursor.execute(query)
    last_id = cursor.fetchone()[0]
    if last_id is None:
        id = 1
    else:
        id = last_id + 1
    tanggal = st.date_input('Tanggal')
    ket_pengeluaran = st.text_input('Keterangan Pengeluaran')
    jumlah_pengeluaran = st.number_input('Jumlah Pengeluaran',0)
    if st.button('Simpan'):
        if ket_pengeluaran == "" or jumlah_pengeluaran == 0:
            st.warning("Sebutkan Keterangan Pengeluaran")
        else:
            cursor = cnx.cursor()
            query = 'INSERT INTO pengeluaran (id, tanggal, nama_pengeluaran, jumlah_pengeluaran) VALUES (%s, %s, %s, %s)'
            cursor.execute(query, (id, tanggal, ket_pengeluaran, jumlah_pengeluaran))
            cnx.commit()
            st.success('Pengeluaran berhasil disimpan')
    col1, col2= st.columns(2)
    with col1:
        if st.checkbox('Cek Daftar Pengeluaran'):
            query = 'SELECT id, nama_pengeluaran, jumlah_pengeluaran, tanggal FROM pengeluaran'
            df = pd.read_sql(query, cnx)
            df['jumlah_pengeluaran'] = df['jumlah_pengeluaran'].apply(lambda x: '{:,}'.format(x).replace(',', '.'))
            st.dataframe(df)
    with col2:
        # Tampilan menu edit/hapus produk apabila di centang
        edit = st.checkbox('Edit/Hapus Pengeluaran')
        if edit:
            query = 'SELECT id, nama_pengeluaran, jumlah_pengeluaran, tanggal FROM pengeluaran'
            df = pd.read_sql(query, cnx)
            keterangan_lama = st.selectbox('Id Pengeluaran', df['id'].tolist())
            keterangan_baru = st.text_input("Keterangan Baru",value=df.loc[df['id'] == keterangan_lama, 'nama_pengeluaran'].values[0])
            nominal_baru = st.number_input("Nominal Baru",value=df.loc[df['id'] == keterangan_lama, 'jumlah_pengeluaran'].values[0])
            tanggal_baru = st.date_input("Tanggal Baru", value=pd.to_datetime(df.loc[df['id'] == keterangan_lama, 'tanggal'].values[0]).date())
            
            if st.button("Edit"):
                if keterangan_baru == "" or nominal_baru == 0 or tanggal_baru == 0:
                    st.error('Data tidak berhasil diubah')
                else:
                    cursor = cnx.cursor()
                    query = "UPDATE pengeluaran SET nama_pengeluaran = %s, jumlah_pengeluaran = %s, tanggal = %s WHERE id = %s"
                    cursor.execute(query, (keterangan_baru, nominal_baru, tanggal_baru, keterangan_lama))
                    cnx.commit()
                    
                    st.success("Data berhasil diubah")
            
            tombol_hapus = st.button("Hapus")
            if tombol_hapus:
                query = 'DELETE FROM pengeluaran WHERE id = %s'
                cursor = cnx.cursor()
                cursor.execute(query, (keterangan_lama,))
                cnx.commit()
                st.success('Pengeluaran berhasil dihapus')

# Tampilan menu Laba
elif menu == 'Laba':
    st.header('Laba')
    col1, col2 = st.columns(2)
    with col1:
        tanggal_awal = st.date_input('Tanggal Awal')
    with col2:
        tanggal_akhir = st.date_input('Tanggal Akhir')

    if st.button('CEK LABA'):

            # Hitung total pengeluaran
            query = 'SELECT SUM(jumlah_pengeluaran) FROM pengeluaran WHERE tanggal BETWEEN %s AND %s'
            cursor = cnx.cursor()
            cursor.execute(query, (tanggal_awal, tanggal_akhir))
            result = cursor.fetchone()
            total_pengeluaran = result[0]
            if total_pengeluaran is None:
                total_pengeluaran = 0
            total_pengeluaran_rupiah = 'Rp. {:,}'.format(total_pengeluaran).replace(',', '.')
            

            # Hitung total transaksi
            query = 'SELECT SUM(total) FROM transaksi WHERE tanggal BETWEEN %s AND %s'
            cursor = cnx.cursor()
            cursor.execute(query, (tanggal_awal, tanggal_akhir))
            result = cursor.fetchone()
            total_transaksi = result[0]
            if total_transaksi is None:
                total_transaksi = 0
            total_transaksi_rupiah = 'Rp. {:,}'.format(total_transaksi).replace(',', '.')
            
            
            # Hitung pemasukan
            query = 'SELECT SUM(total - harga_pokok * jumlah) FROM transaksi  WHERE tanggal BETWEEN %s AND %s'
            cursor.execute(query, (tanggal_awal, tanggal_akhir))
            result = cursor.fetchone()
            pemasukan = result[0]
            if pemasukan is None:
                pemasukan = 0
            pemasukan_rupiah = 'Rp. {:,}'.format(pemasukan).replace(',', '.')
            
            
            # Hitung laba
            laba = pemasukan - total_pengeluaran
            laba_rupiah = 'Rp. {:,}'.format(laba).replace(',', '.')
            

            # Hitung modal total saat ini
            query = 'SELECT SUM(harga_pokok * stok) FROM produk;'
            cursor.execute(query)
            result = cursor.fetchone()
            modal_now = result[0]
            if modal_now is None:
                modal_now = 0
            modal_now = 'Rp. {:,}'.format(modal_now).replace(',', '.')
            
            # Hitung jumlah belanja berdasarkan tanggal
            query = 'SELECT SUM(harga_pokok * jumlah_update) FROM update_produk WHERE tanggal BETWEEN %s AND %s'
            cursor.execute(query, (tanggal_awal, tanggal_akhir))
            result = cursor.fetchone()
            belanja = result[0]
            if belanja is None:
                belanja = 0
            belanja_rupiah = 'Rp. {:,}'.format(belanja).replace(',', '.')
            
            # Hitung jumlah semua transaksi
            query = 'SELECT SUM(total) FROM transaksi'
            cursor.execute(query)
            result = cursor.fetchone()
            total_transaksi_semua = result[0]
            if total_transaksi_semua is None:
                total_transaksi_semua = 0

            # Hitung jumlah semua belanja
            query = 'SELECT SUM(harga_pokok * jumlah_update) FROM update_produk'
            cursor.execute(query)
            result = cursor.fetchone()
            total_belanja_semua = result[0]
            if total_belanja_semua is None:
                total_belanja_semua = 0

            # Hitung jumlah semua pengeluaran
            query = 'SELECT SUM(jumlah_pengeluaran) FROM pengeluaran'
            cursor.execute(query)
            result = cursor.fetchone()
            total_pengeluaran_semua = result[0]
            if total_pengeluaran_semua is None:
                total_pengeluaran_semua = 0

            # Sum kas awal
            query = 'SELECT SUM(kas_awal) FROM kas'
            cursor.execute(query)
            result = cursor.fetchone()
            kas_awal = result[0]
            if kas_awal is None:
                kas_awal = 0
            kas_jumlah = kas_awal - (total_belanja_semua + total_pengeluaran_semua)
            kas = total_transaksi_semua + (kas_jumlah)
            kas = 'Rp. {:,}'.format(kas).replace(',', '.')
            
            if total_pengeluaran == 0 or total_transaksi == 0 or pemasukan == 0 or laba == 0 or modal_now == 0:
                st.error('LABA HANYA DAPAT DIHITUNG JIKA ADA PENGELUARAN DAN PEMASUKAN')
            else:
                st.write('Total Pengeluaran:', total_pengeluaran_rupiah)
                st.write('Total transaksi:', total_transaksi_rupiah)
                st.write('Keuntungan:', pemasukan_rupiah)
                st.write('Laba Bersih:', laba_rupiah)
                st.write('Total Belanja :',belanja_rupiah)
                
                st.info('PERHITUNGAN TANPA PARAMETER TANGGAL AWAL -> AKHIR')
                st.write('Total Kas Saat Ini :',kas)
                st.write('Seluruh Modal Saat Ini:', modal_now)

# Tampilan menu Riwayat Transaksi
elif menu == 'Riwayat Transaksi':
    st.header('Riwayat Transaksi')
    col1, col2 = st.columns(2)
    query = 'SELECT  tanggal,nama_pelanggan, nama, jumlah, harga, total FROM transaksi'
    df = pd.read_sql(query, cnx)
    df = df.sort_values(by='tanggal', ascending=False)
    
    # Tampilkan harga dan total dalam bentuk angka dengan tanda titik sebagai pemisah ribuan
    df['harga'] = df['harga'].apply(lambda x: '{:,}'.format(x).replace(',', '.'))
    df['total'] = df['total'].apply(lambda x: '{:,}'.format(x).replace(',', '.'))
    with col1:
        
        st.dataframe(df, width=2000, height=250)
        # Tampilan menu hapus produk apabila di centang
        hapus = st.checkbox('Hapus Transaksi')
        if hapus:
            query = 'SELECT id, tanggal, nama, jumlah, harga, total, nama_pelanggan FROM transaksi'
            df = pd.read_sql(query, cnx)
            id_produk = st.selectbox("Pilih ID Transaksi", df['id'].tolist())
            nama = st.text_input("Nama Pembeli",value=df.loc[df['id'] == id_produk, 'nama_pelanggan'].values[0])
            tombol_hapus = st.button("Hapus")
            if tombol_hapus:
                query = 'DELETE FROM transaksi WHERE id = %s'
                cursor = cnx.cursor()
                cursor.execute(query, (id_produk,))
                cnx.commit()
                st.success('Transaksi berhasil dihapus')
    with col2:
        # Buat grafik jumlah penjualan per bulan
        tanggal_mulai = st.date_input('Tanggal Mulai')
        tanggal_akhir = st.date_input('Tanggal Akhir')
    if st.button('CEK GRAFIK'):

        # Grafik seluruh penjualan
        query = "SELECT DATE(tanggal) as tanggal, SUM(jumlah) as jumlah_penjualan FROM transaksi WHERE tanggal BETWEEN %s AND %s GROUP BY DATE(tanggal)"
        df = pd.read_sql(query, cnx, params=(tanggal_mulai, tanggal_akhir))
        fig = px.bar(df, x='tanggal', y='jumlah_penjualan')
        fig.update_layout(autosize=True)
        st.plotly_chart(fig)

        # Grafik penjualan berdasarkan produk
        query = "SELECT nama, tanggal, SUM(jumlah) as jumlah_penjualan FROM transaksi WHERE tanggal BETWEEN %s AND %s GROUP BY nama, date(tanggal)"
        df = pd.read_sql(query, cnx, params=(tanggal_mulai, tanggal_akhir))
        df = df.pivot(index='tanggal', columns='nama', values='jumlah_penjualan').fillna(0)
        st.line_chart(df)

            
# Tampilan menu Data Mining
elif menu == 'Data Mining':
    st.header('Data Mining')
    # Sub Menu untuk data mining
    sub_menu = st.selectbox('', ['Market Basket Analisys', 'Forecasting'])
    if sub_menu == 'Market Basket Analisys':
        st.header('Market Basket Analisys')
        col1, col2 = st.columns(2)
        # Ambil data produk dari database MySQL
        query = 'SELECT * FROM produk'
        df = pd.read_sql(query, cnx)

        # Input Nama produk
        nama_produk = st.multiselect("Pilih Produk ", df['nama'].tolist())

        # Ceklis jika ingin memilih hanya berdasarkan tanggal
        all = st.checkbox('Pilih hanya berdasarkan tanggal')

        # Input tanggal awal dan akhir
        with col1:
            tanggal_mulai = st.date_input("Tanggal Mulai")
        with col1:
            tanggal_akhir = st.date_input("Tanggal Akhir")

        # Mendefinisikan nilai minimum support dan minimum confidence
        with col2:
            minimum_support = st.number_input("Nilai minimum support:",0.01)
        with col2:
            minimum_confidence = st.number_input("Nilai minimum confidence:",0.01)
        
        # Membaca data transaksi dari database SQLite
        query = 'SELECT tanggal, nama_pelanggan, nama FROM transaksi WHERE tanggal BETWEEN %s AND %s'
        df = pd.read_sql(query, cnx, params=(tanggal_mulai, tanggal_akhir))
        
        # Mengubah tanggal yang ditampilkan  dataframe menjadi objek datatime
        df['tanggal'] = pd.to_datetime(df['tanggal'])

        # Memfilter data transaksi berdasarkan tanggal mulai dan akhir
        df = df[(df['tanggal'] >= pd.to_datetime(tanggal_mulai)) & (df['tanggal'] <= pd.to_datetime(tanggal_akhir))]
        
        # Memfilter data transaksi berdasarkan nama produk
        if all:
            pass # jangan lakukan apapun jika all dicentang
        else:
            df = df[df['nama'].isin(nama_produk)]  # lakukan sesuai nama produk yang akan di filter
        
        # Menggabungkan tanggal dan nama pelanggan yang sama
        df['tanggal_nama_pelanggan'] = df['tanggal'].astype(str) +'-'+ df['nama_pelanggan']

        # Mengubah data menjadi tabulasi
        tabular = pd.crosstab(df['tanggal_nama_pelanggan'],df['nama'])

        # Encoding data
        def hot_encode(x) :
            if (x<=0):
                return 0
            if (x>=1):
                return 1

        # Menampilkan hasil dari algoritma Apriori
        if st.button("PROSES"):

            if df.empty is None:
                st.error('TIDAK DAPAT MELAKUKAN PERHITUNGAN')
            else:
                st.success('HASIL PERHITUNGAN APRIORI')

                # Mengubah data menjadi binominal
                tabular_encode = tabular.applymap(hot_encode)

                # Membuat model Apriori
                frq_items = apriori(tabular_encode, min_support=minimum_support, use_colnames= True)

                # Mengumpulkan aturan dalam dataframe
                rules = association_rules(frq_items, metric="confidence",min_threshold=minimum_confidence)
                rules = rules.sort_values(['confidence','lift'], ascending=[False, False])

                # Mengubah nilai support, confidence, dan lift menjadi persentase
                rules[["antecedent support","consequent support","support","confidence"]] = rules[["antecedent support","consequent support","support","confidence"]].applymap(lambda x: "{:.2f}%".format(x*100))

                # Menampilkan hasil algoritma apriori dalam bentuk dataframe
                st.dataframe(rules.applymap(lambda x: ','.join(x) if type(x) == frozenset else x))

    elif sub_menu == 'Forecasting':
        st.header('Forecasting')
        st.info('BELUM FIX')
        query = "SELECT nama FROM produk"
        df = pd.read_sql(query, cnx)
        nama_item = st.selectbox("Pilih produk ", df['nama'].tolist())
        average = st.number_input('Masukan Jumlah Rentang',min_value=1) 
        if st.button('CEK FORECASTING'):
            query = "SELECT tanggal, jumlah FROM transaksi WHERE nama = %s"
            df = pd.read_sql(query, cnx,params=(nama_item,))
            df.set_index('tanggal', inplace=True)
            df = df.groupby(['tanggal'])['jumlah'].sum().reset_index()
            df['moving_avg'] = df['jumlah'].shift(1).rolling(window=average).mean()
            df = df.sort_values(by='tanggal', ascending=False)
            st.dataframe(df)
