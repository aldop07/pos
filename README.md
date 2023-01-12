# Point Of Sale
Web-based point of sale application with apriori algorithm
This script is a point-of-sale management system which allow users to manage and monitor their sales transaction through a web interface. The script utilizes the Streamlit library to create a user interface, the sqlite3 library to connect to the database and the pandas, matplotlib, plotly and mlxtend library to manipulate and visualize data.

- Import Library:
The script starts by importing the necessary libraries. It uses streamlit to create a web-based user interface, sqlite3 to connect to the SQLite database, pandas to manipulate and display data, matplotlib to create charts and plots, plotly for data visualization and the mlxtend library to perform association rule mining using the Apriori algorithm.

- Connect to Database:
The script connects to an SQLite database called 'kasir.db' where the information of the products, transactions and expenses are stored.

- Create Sidebar and Dropdown Menu:
A sidebar with a dropdown menu is created using st.sidebar.header('Menu') and menu = st.sidebar.selectbox('', ['Daftar Produk', 'Tambah Produk', 'Tambah Transaksi', 'Tambah Pengeluaran', 'Laba', 'Riwayat Transaksi','Apriori']) the user can select different options from the menu, such as displaying a list of products, adding a new product, adding a new transaction or analyzing sales data.

- List of products:
If the user selects "Daftar Produk" from the menu, the script retrieves data from the "produk" table in the database and displays it in a table. It also allows the user to update the stock of a product by selecting a product from a drop-down list and entering a new stock value.

- Add New Product:
If the user selects "Tambah Produk" from the menu, the script displays a form that allows the user to enter information about a new product, such as its name, price, and stock. When the form is submitted, the script saves the new product data to the "produk" table in the database.

- Add New Transaction:
If the user selects "Tambah Transaksi" from the menu, the script displays a form that allows the user to enter information about a new transaction, such as the date, product, quantity and price. When the form is submitted, the script saves the new transaction data to the "transaksi" table in the database and update the "produk" table.

- Add New Expense:
If the user selects "Tambah Pengeluaran" from the menu, the script displays a form that allows the user to enter information about a new expense, such as the date and amount. When the form is submitted, the script saves the new expense data to the "pengeluaran" table in the database

- Apriori:
The Apriori option allows the user to perform association rule mining by analyzing transaction data from the "transaksi" table in the database and creating association rules between the purchased products. The apriori function from mlxtend.frequent_patterns is used to find the frequent item sets and association_rules is used to find the association rules

The script also has several other options to display the profit, transaction history and also other features that you can customize.
