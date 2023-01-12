import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from mlxtend.frequent_patterns import apriori, association_rules

#   IRFAN NOVALDO HUANG

# Koneksi ke database SQLite
cnx = sqlite3.connect('kasir_kalimantan.db')

# Buat sidebar dan menu dropdown
st.sidebar.header('Menu')
menu = st.sidebar.selectbox('', ['Daftar Produk', 'Tambah Produk', 'Tambah Transaksi', 'Tambah Pengeluaran', 'Laba', 'Riwayat Transaksi','Apriori'])

# Tampilan menu Daftar Produk
if menu == 'Daftar Produk':
    st.header('Daftar Produk')
    query = 'SELECT nama, harga, stok FROM produk'
    df = pd.read_sql(query, cnx)

    # Tampilkan harga dalam bentuk angka dengan tanda titik sebagai pemisah ribuan
    df['harga'] = df['harga'].apply(lambda x: '{:,}'.format(x))

    # Tampilkan stok dalam bentuk angka tanpa desimal
    df['stok'] = df['stok'].apply(lambda x: int(x) if x == x else x)

    # Tampikan stok dalam bentuk dataframe
    st.dataframe(df)

    # Tambahkan form input untuk mengubah stok produk
    st.header('Update Stok Produk')
    list_produk = ['Pilih produk...'] + list(df['nama'])
    produk = st.selectbox('Produk', list_produk)
    stok_produk = st.number_input('Stok Produk',0)
    if st.button('Update'):
            cursor = cnx.cursor()
            query_select = 'SELECT stok FROM produk WHERE nama = ?'
            cursor.execute(query_select, (produk,))
            result = cursor.fetchone()
            stok_lama = result[0]
            stok_baru = stok_lama + stok_produk
            query_update = 'UPDATE produk SET stok = ? WHERE nama = ?'
            cursor.execute(query_update, (stok_baru, produk))
            cnx.commit()
            st.success('Stok produk berhasil diubah')

# Tampilan menu Tambah Produk
elif menu == 'Tambah Produk':
    st.header('Tambah Produk')
    nama_produk = st.text_input('Nama Produk')
    harga_produk = st.number_input('Harga Produk',0)
    harga_pokok = st.number_input('Harga Pokok',0)
    stok_produk = st.number_input('Stok Produk',0)
    if st.button('Simpan'):
        cursor = cnx.cursor()
        query = 'INSERT INTO produk (nama, harga, stok, harga_pokok) VALUES (?, ?, ?, ?)'
        cursor.execute(query, (nama_produk, harga_produk, stok_produk, harga_pokok))
        cnx.commit()
        st.success('Produk berhasil disimpan')

# Tampilan menu Tambah Transaksi
elif menu == 'Tambah Transaksi':
    st.header('Tambah Transaksi')
    
    # Ambil data produk dari database MySQL
    query = 'SELECT * FROM produk'
    df = pd.read_sql(query, cnx)
   
    # Buat list nama produk untuk dipilih dalam form input transaksi
    tanggal = st.date_input('Tanggal')
    list_nama_produk = ['Pilih produk...'] + list(df['nama'])
    nama_produk = st.selectbox('Nama Produk', list_nama_produk)
    jumlah_produk = st.number_input('Jumlah Produk',0)
    if jumlah_produk == 0:
        st.error('Jumlah produk tidak boleh 0')
        
    elif st.button('Simpan'):
    # Buat objek cursor
        cursor = cnx.cursor()
        query = 'SELECT harga, stok FROM produk WHERE nama = ?'
        cursor.execute(query, (nama_produk,))
        result = cursor.fetchone()
        harga_produk = result[0]
        stok_produk = result[1]
        total_harga = harga_produk * jumlah_produk
        if stok_produk >= jumlah_produk:
            
            # Tambahkan transaksi baru ke tabel transaksi
            query = 'INSERT INTO transaksi (tanggal, nama, jumlah, harga, total) VALUES (?, ?, ?, ?, ?)'
            cursor.execute(query, (tanggal, nama_produk, jumlah_produk, harga_produk, total_harga))
           
            # Kurangi stok produk yang dibeli
            query = 'UPDATE produk SET stok = stok - ? WHERE nama = ?'
            cursor.execute(query, (jumlah_produk, nama_produk))
            cnx.commit()
            st.success('Transaksi berhasil disimpan')
        else:
            st.error('Stok produk tidak mencukupi')

# Tampilan menu Tambah Pengeluaran
elif menu == 'Tambah Pengeluaran':
    st.header('Tambah Pengeluaran')
    tanggal = st.date_input('Tanggal')
    nama_pengeluaran = st.text_input('Nama Pengeluaran')
    jumlah_pengeluaran = st.number_input('Jumlah Pengeluaran',0)
    if st.button('Simpan'):
        cursor = cnx.cursor()
        query = 'INSERT INTO pengeluaran (tanggal, nama_pengeluaran, jumlah_pengeluaran) VALUES (?, ?, ?)'
        cursor.execute(query, (tanggal, nama_pengeluaran, jumlah_pengeluaran))
        cnx.commit()
        st.success('Pengeluaran berhasil disimpan')

# Tampilan menu Laba
elif menu == 'Laba':
    st.header('Laba')
    tanggal_awal = st.date_input('Tanggal Awal')
    tanggal_akhir = st.date_input('Tanggal Akhir')
    
    # Hitung total pengeluaran
    query = 'SELECT SUM(jumlah_pengeluaran) FROM pengeluaran WHERE tanggal BETWEEN ? AND ?'
    cursor = cnx.cursor()
    cursor.execute(query, (tanggal_awal, tanggal_akhir))
    result = cursor.fetchone()
    total_pengeluaran = result[0]
    total_pengeluaran_rupiah = 'Rp. {:,}'.format(total_pengeluaran)
    st.write('Total Pengeluaran:', total_pengeluaran_rupiah)

    # Hitung total transaksi
    query = 'SELECT SUM(total) FROM transaksi WHERE tanggal BETWEEN ? AND ?'
    cursor = cnx.cursor()
    cursor.execute(query, (tanggal_awal, tanggal_akhir))
    result = cursor.fetchone()
    total_transaksi = result[0]
    total_transaksi_rupiah = 'Rp. {:,}'.format(total_transaksi)
    st.write('Total transaksi:', total_transaksi_rupiah)
    
    # Hitung pemasukan
    query = 'SELECT SUM(total - harga_pokok * jumlah) FROM transaksi JOIN produk ON transaksi.nama = produk.nama WHERE transaksi.tanggal BETWEEN ? AND ?'
    cursor.execute(query, (tanggal_awal, tanggal_akhir))
    result = cursor.fetchone()
    pemasukan = result[0]
    pemasukan_rupiah = 'Rp. {:,}'.format(pemasukan)
    st.write('Keuntungan:', pemasukan_rupiah)
    
    # Hitung laba
    laba = pemasukan - total_pengeluaran
    laba_rupiah = 'Rp. {:,}'.format(laba)
    st.write('Laba Bersih:', laba_rupiah)

# Tampilan menu Riwayat Transaksi
elif menu == 'Riwayat Transaksi':
    st.header('Riwayat Transaksi')
    query = 'SELECT tanggal, nama, jumlah, harga, total FROM transaksi'
    df = pd.read_sql(query, cnx)
    df = df.sort_values(by='tanggal', ascending=False)
    
    # Tampilkan harga dan total dalam bentuk angka dengan tanda titik sebagai pemisah ribuan
    df['harga'] = df['harga'].apply(lambda x: '{:,}'.format(x))
    df['total'] = df['total'].apply(lambda x: '{:,}'.format(x))
    st.dataframe(df)


    # Buat grafik jumlah penjualan per bulan
    tanggal_mulai = st.date_input('Tanggal Mulai')
    tanggal_akhir = st.date_input('Tanggal Akhir')
    if tanggal_mulai and tanggal_akhir:
        query = "SELECT date(tanggal) as tanggal, SUM(jumlah) as jumlah_penjualan FROM transaksi WHERE tanggal BETWEEN ? AND ? GROUP BY date(tanggal)"
        df = pd.read_sql(query, cnx, params=(tanggal_mulai, tanggal_akhir))
        fig = px.bar(df, x='tanggal', y='jumlah_penjualan')
        st.plotly_chart(fig)

# Tampilan menu Apriori
elif menu == 'Apriori':
    st.header('Apriori')
    
    # Input tanggal awal dan akhir
    tanggal_mulai = st.date_input("Tanggal Mulai")
    tanggal_akhir = st.date_input("Tanggal Akhir")
    
    if tanggal_mulai and tanggal_akhir:
        # Membaca data transaksi dari database SQLite
        query = 'SELECT * FROM transaksi WHERE tanggal BETWEEN ? AND ?'
        df = pd.read_sql(query, cnx, params=(tanggal_mulai, tanggal_akhir))

        # Mengubah tanggal yang ditampilkan  dataframe menjadi objek datatime
        df['tanggal'] = pd.to_datetime(df['tanggal'])

        # Memfilter data transaksi berdasarkan tanggal mulai dan akhir
        df = df[(df['tanggal'] >= pd.to_datetime(tanggal_mulai)) & (df['tanggal'] <= pd.to_datetime(tanggal_akhir))]
        
        # Mengubah data menjadi tabulasi
        tabular = pd.crosstab (df["tanggal"],df["nama"])


        dta = pd.DataFrame(tabular)
        download = dta.to_excel
        if download :
                with open("Tabulasi.xls", "wb") as f: # buka file Tabulasi.xls dalam mode binary write

                    dta.to_excel(f) # menulis dataframe dta ke file excel

                with open("Tabulasi.xls", "rb") as f: #buka file Tabulasi.xls dalam mode binary read

                    excel_file = f.read() #membaca data biner

                st.download_button(label="Download Excel", data=excel_file, file_name="Tabulasi.xls", mime='text/xls')

        # Encoding data
        def hot_encode(x) :
            if (x<=0):
                return 0
            if (x>=1):
                return 1

        # Mengubah data menjadi binominal
        tabular_encode = tabular.applymap(hot_encode)

        # Mendefinisikan nilai minimum support dan minimum confidence
        minimum_support = st.number_input("Nilai minimum support:",0.1)
        if minimum_support <= 0:
            st.warning("Nilai minimum support tidak boleh kosong atau nol.")

        # Membuat model Apriori
        frq_items = apriori(tabular_encode, min_support=minimum_support, use_colnames= True)

        # Mengumpulkan aturan dalam dataframe
        rules = association_rules(frq_items, metric="lift",min_threshold=1)
        rules = rules.sort_values(['confidence','lift'], ascending=[False, False])

        # Menampilkan hasil dari algoritma Apriori
        if st.button("PROSES"):
            st.success('HASIL PERHITUNGAN APRIORI')

            # Mengubah nilai support, confidence, dan lift menjadi persentase
            rules[["antecedent support","consequent support","support","confidence"]] = rules[["antecedent support","consequent support","support","confidence"]].applymap(lambda x: "{:.2f}%".format(x*100))

            # Menampilkan hasil algoritma apriori dalam bentuk dataframe
            st.dataframe(rules.applymap(lambda x: ','.join(x) if type(x) == frozenset else x))