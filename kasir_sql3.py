import streamlit as st
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from mlxtend.frequent_patterns import apriori, association_rules

#   IRFAN NOVALDO HUANG

# Koneksi ke database SQLite
cnx = sqlite3.connect('kasir.db')

# Buat titit
icon = 'https://th.bing.com/th/id/R.a406cbfb23b4d4937c5c3e323a7cb567?rik=4qO3lF%2ftE0LZTg&riu=http%3a%2f%2f1.bp.blogspot.com%2f-I-do3iLl5rs%2fUsuaG8IcjhI%2fAAAAAAAAAIE%2fXmXj-zTkS9U%2fs1600%2fUnsera.png&ehk=7Q%2f63voOpFTnTFwucAoLvddSl03O7NITAf9NPD3Ge7M%3d&risl=&pid=ImgRaw&r=0'
st.set_page_config(page_title="Point Of Sale", page_icon=icon, layout="wide")

st.title('Aplikasi Point Of Sale')
# Buat sidebar dan menu dropdown
st.sidebar.header('Menu') 
menu = st.sidebar.selectbox('', ['Dokumentasi','Daftar Produk', 'Tambah Produk', 'Tambah Transaksi', 'Tambah Pengeluaran', 'Laba', 'Riwayat Transaksi','Data Mining'])
# Tampilan menu Dokumentasi
if menu == 'Dokumentasi':
    st.header('Dokumentasi')
    st.write('https://ejournal.bsi.ac.id/ejurnal/index.php/khatulistiwa/article/viewFile/8994/4535')
    #pdf_url = "https://ejournal.bsi.ac.id/ejurnal/index.php/khatulistiwa/article/viewFile/8994/4535"

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
    query = 'SELECT nama, harga, stok FROM produk'
    df = pd.read_sql(query, cnx)

    # Tampilkan harga dalam bentuk angka dengan tanda titik sebagai pemisah ribuan
    df['harga'] = df['harga'].apply(lambda x: '{:,}'.format(x).replace(',', '.'))

    # Tampilkan stok dalam bentuk angka tanpa desimal
    df['stok'] = df['stok'].apply(lambda x: int(x) if x == x else x)

    # Tampikan stok dalam bentuk dataframe
    st.dataframe(df)

    # Tambahkan form input untuk mengubah stok produk
    st.header('Update Stok Produk')
    produk = st.selectbox("Pilih Produk ", df['nama'].tolist())
    stok_produk = st.number_input('Stok Produk',0)
    if st.button('Update') and stok_produk >= 1:
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
    else:
        st.warning('Input dengan teliti')

# Tampilan menu Tambah Produk
elif menu == 'Tambah Produk':
    st.header('Tambah Produk')
    nama_produk = st.text_input('Nama Produk')
    harga_produk = st.number_input('Harga Jual',0)
    harga_pokok = st.number_input('Harga Pokok',0)
    stok_produk = st.number_input('Stok Produk',0)
    if st.button('Simpan'):
        if nama_produk == "" or harga_pokok < 1000 or harga_produk < 1000 :
            st.warning('Input dengan benar')
        else:
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
    nama_pelanggan = st.text_input ('Nama Pelanggan')
    nama_produk = st.multiselect("Pilih Produk ", df['nama'].tolist())
    jumlah_produk = []
    total_harga = 0
    for produk in nama_produk:
        jumlah = st.number_input(f'Jumlah Produk {produk}',min_value=0)
        jumlah_produk.append(jumlah)

    if st.button('Simpan'):
        if nama_pelanggan == "" or sum(jumlah_produk) == 0 or 0 in jumlah_produk:
            st.warning("Periksa Nama Pelanggan dan Jumlah Produk")
        else:
            # Buat objek cursor
            cursor = cnx.cursor()
            transaksi_berhasil = True
            produk_stok_tidak_mencukupi = []
            for i in range(len(nama_produk)):
                query = 'SELECT harga, stok FROM produk WHERE nama = ?'
                cursor.execute(query, (nama_produk[i],))
                result = cursor.fetchone()
                harga_produk = result[0]
                stok_produk = result[1]
                total_harga = harga_produk * jumlah_produk[i]
                if stok_produk >= jumlah_produk[i]:
                    # Tambahkan transaksi baru ke tabel transaksi
                    query = 'INSERT INTO transaksi (tanggal, nama_pelanggan, nama, jumlah, harga, total) VALUES (?, ?, ?, ?, ?, ?)'
                    cursor.execute(query, (tanggal ,nama_pelanggan, nama_produk[i], jumlah_produk[i], harga_produk, total_harga))
                else:
                    transaksi_berhasil = False
                    produk_stok_tidak_mencukupi.append(nama_produk[i])

            if transaksi_berhasil:
                cnx.commit()
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
    tanggal = st.date_input('Tanggal')
    ket_pengeluaran = st.text_input('Keterangan Pengeluaran')
    jumlah_pengeluaran = st.number_input('Jumlah Pengeluaran',0)
    if st.button('Simpan'):
        if ket_pengeluaran == "" and jumlah_pengeluaran == 0:
            st.warning("Sebutkan Keterangan Pengeluaran")
        else:
            cursor = cnx.cursor()
            query = 'INSERT INTO pengeluaran (tanggal, nama_pengeluaran, jumlah_pengeluaran) VALUES (?, ?, ?)'
            cursor.execute(query, (tanggal, ket_pengeluaran, jumlah_pengeluaran))
            cnx.commit()
            st.success('Pengeluaran berhasil disimpan')
        
# Tampilan menu Laba
elif menu == 'Laba':
    st.header('Laba')
    tanggal_awal = st.date_input('Tanggal Awal')
    tanggal_akhir = st.date_input('Tanggal Akhir')
    if st.button('CEK LABA'):
        
    # Hitung total pengeluaran
        query = 'SELECT SUM(jumlah_pengeluaran) FROM pengeluaran WHERE tanggal BETWEEN ? AND ?'
        cursor = cnx.cursor()
        cursor.execute(query, (tanggal_awal, tanggal_akhir))
        result = cursor.fetchone()
        total_pengeluaran = result[0]
        total_pengeluaran_rupiah = 'Rp. {:,}'.format(total_pengeluaran).replace(',', '.')
        st.write('Total Pengeluaran:', total_pengeluaran_rupiah)

        # Hitung total transaksi
        query = 'SELECT SUM(total) FROM transaksi WHERE tanggal BETWEEN ? AND ?'
        cursor = cnx.cursor()
        cursor.execute(query, (tanggal_awal, tanggal_akhir))
        result = cursor.fetchone()
        total_transaksi = result[0]
        total_transaksi_rupiah = 'Rp. {:,}'.format(total_transaksi).replace(',', '.')
        st.write('Total transaksi:', total_transaksi_rupiah)
        
        # Hitung pemasukan
        query = 'SELECT SUM(total - harga_pokok * jumlah) FROM transaksi JOIN produk ON transaksi.nama = produk.nama WHERE transaksi.tanggal BETWEEN ? AND ?'
        cursor.execute(query, (tanggal_awal, tanggal_akhir))
        result = cursor.fetchone()
        pemasukan = result[0]
        pemasukan_rupiah = 'Rp. {:,}'.format(pemasukan).replace(',', '.')
        st.write('Keuntungan:', pemasukan_rupiah)
        
        # Hitung laba
        laba = pemasukan - total_pengeluaran
        laba_rupiah = 'Rp. {:,}'.format(laba).replace(',', '.')
        st.write('Laba Bersih:', laba_rupiah)

        # Hitung modal total saat ini
        query = 'SELECT SUM(harga_pokok * stok) FROM produk'
        cursor.execute(query)
        result = cursor.fetchone()
        modal_now = result[0]
        modal_now = 'Rp. {:,}'.format(modal_now).replace(',', '.')
        st.write('Seluruh Modal Saat Ini:', modal_now)
    else:
        st.info('LABA HANYA DAPAT DIHITUNG JIKA ADA PENGELUARAN')

# Tampilan menu Riwayat Transaksi
elif menu == 'Riwayat Transaksi':
    st.header('Riwayat Transaksi')
    query = 'SELECT tanggal, nama, jumlah, harga, total FROM transaksi'
    df = pd.read_sql(query, cnx)
    df = df.sort_values(by='tanggal', ascending=False)
    
    # Tampilkan harga dan total dalam bentuk angka dengan tanda titik sebagai pemisah ribuan
    df['harga'] = df['harga'].apply(lambda x: '{:,}'.format(x).replace(',', '.'))
    df['total'] = df['total'].apply(lambda x: '{:,}'.format(x).replace(',', '.'))
    st.dataframe(df)


    # Buat grafik jumlah penjualan per bulan
    tanggal_mulai = st.date_input('Tanggal Mulai')
    tanggal_akhir = st.date_input('Tanggal Akhir')
    if st.button('CEK GRAFIK'):
        query = "SELECT date(tanggal) as tanggal, SUM(jumlah) as jumlah_penjualan FROM transaksi WHERE tanggal BETWEEN ? AND ? GROUP BY date(tanggal)"
        df = pd.read_sql(query, cnx, params=(tanggal_mulai, tanggal_akhir))
        fig = px.bar(df, x='tanggal', y='jumlah_penjualan')
        fig.update_layout(autosize=True)
        st.plotly_chart(fig)
        st.warning('Input dengan teliti')
        query = "SELECT nama, tanggal, SUM(jumlah) as jumlah_penjualan FROM transaksi WHERE tanggal BETWEEN ? AND ? GROUP BY nama, date(tanggal)"
        df = pd.read_sql(query, cnx, params=(tanggal_mulai, tanggal_akhir))
        df = df.pivot(index='tanggal', columns='nama', values='jumlah_penjualan').fillna(0)
        st.line_chart(df)

            
# Tampilan menu Data Mining
elif menu == 'Data Mining':
    st.header('Data Mining')

    # Sub Menu untuk data mining
    sub_menu = st.selectbox('', ['Association Rule', 'Forecasting'])
    if sub_menu == 'Association Rule':
        st.header('Association Rule')
        # Input produk
        
        # Input tanggal awal dan akhir
        tanggal_mulai = st.date_input("Tanggal Mulai")
        tanggal_akhir = st.date_input("Tanggal Akhir")
        # Mendefinisikan nilai minimum support dan minimum confidence
        minimum_support = st.number_input("Nilai minimum support:",0.01)
        minimum_confidence = st.number_input("Nilai minimum confidence:",0.01)
        
        #if tanggal_mulai and tanggal_akhir:
            # Membaca data transaksi dari database SQLite
        query = 'SELECT tanggal, nama_pelanggan, nama FROM transaksi WHERE tanggal BETWEEN ? AND ?'
        df = pd.read_sql(query, cnx, params=(tanggal_mulai, tanggal_akhir))

            # Mengubah tanggal yang ditampilkan  dataframe menjadi objek datatime
        df['tanggal'] = pd.to_datetime(df['tanggal'])

            # Memfilter data transaksi berdasarkan tanggal mulai dan akhir
        df = df[(df['tanggal'] >= pd.to_datetime(tanggal_mulai)) & (df['tanggal'] <= pd.to_datetime(tanggal_akhir))]
            
            # Mengubah data menjadi tabulasi
        df['tanggal_nama_pelanggan'] = df['tanggal'].astype(str) +'-'+ df['nama_pelanggan']
        tabular = pd.crosstab(df['tanggal_nama_pelanggan'],df['nama'])


            #dta = pd.DataFrame(tabular)
            #download = dta.to_excel
            #if download :
            #        with open("Tabulasi.xlsx", "wb") as f: # buka file Tabulasi.xls dalam mode binary write

             #           dta.to_excel(f) # menulis dataframe dta ke file excel

              #      with open("Tabulasi.xlsx", "rb") as f: #buka file Tabulasi.xls dalam mode binary read

               #         excel_file = f.read() #membaca data biner

                #    st.download_button(label="Download Excel", data=excel_file, file_name="Tabulasi.xlsx", mime='text/xlsx')
            #else:
            #    st.warning('Input dengan teliti')
            # Encoding data
        def hot_encode(x) :
            if (x<=0):
                return 0
            if (x>=1):
                return 1

            # Menampilkan hasil dari algoritma Apriori
        if st.button("PROSES"):
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
        average = st.number_input('Masukan Jumlah Rentang',min_value=1)
        query = "SELECT nama FROM produk"
        df = pd.read_sql(query, cnx)
        nama_item = st.selectbox("Pilih produk ", df['nama'].tolist())
        if st.button('CEK FORECASTING'):
            query = "SELECT tanggal, jumlah FROM transaksi WHERE nama = ?"
            df = pd.read_sql(query, cnx,params=(nama_item,))
            df.set_index('tanggal', inplace=True)
            df = df.groupby(['tanggal'])['jumlah'].sum().reset_index()
            df['moving_avg'] = df['jumlah'].shift(1).rolling(window=average).mean()
            df = df.sort_values(by='tanggal', ascending=False)
            st.dataframe(df)
