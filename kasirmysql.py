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

                query = "SELECT SUM(id) FROM update_produk"
                cursor.execute(query)
                last_id = cursor.fetchone()[0]
                if last_id is None:
                    id = 1
                else:
                    id = last_id + 1

                query = 'INSERT INTO update_produk (id, tanggal, nama_produk, harga_jual, jumlah_update, jumlah_lama, harga_pokok) VALUES (%s, %s, %s, %s, %s)'
                cursor.execute(query, (id, tanggal, produk, harga_jual, stok_produk_baru, stok_lama,harga_pokok))
                cnx.commit()

                st.success('Stok produk berhasil diupdate')
