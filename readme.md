# Brazilian E-Commerce Data Analysis Dashboard

<p align="center">
  **Exploratory Data Analysis & Interactive Business Intelligence Dashboard**
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Completed-success" />
</p>

---

## 📌 Project Overview

Proyek ini merupakan analisis data menggunakan **Brazilian E-Commerce Public Dataset by Olist**, sebuah dataset publik dari marketplace Olist di Brasil, dengan periode transaksi Januari 2017 hingga Agustus 2018.

Analisis difokuskan pada pesanan dengan status **delivered** untuk memperoleh gambaran performa penjualan, karakteristik pelanggan, distribusi geografis, serta hubungan antara keterlambatan pengiriman dan kepuasan pelanggan.

Seluruh nilai transaksi menggunakan mata uang Real Brasil (R$). Revenue dihitung berdasarkan total harga item tanpa memasukkan ongkos kirim.

## 🎯 Business Questions

Proyek ini bertujuan menjawab lima pertanyaan bisnis utama:

1. **Product Category Performance**  
   Kategori produk apa saja yang menjadi lima penyumbang revenue terbesar dan terkecil?

2. **Monthly Sales Trends**  
   Bagaimana tren jumlah pesanan dan revenue setiap bulan, serta kapan periode puncak penjualan terjadi?

3. **Geographical Analysis**  
   State mana yang menyumbang revenue dan pelanggan terbanyak, serta bagaimana rata-rata waktu pengirimannya?

4. **Customer Segmentation (RFM)**  
   Bagaimana segmentasi pelanggan berdasarkan Recency, Frequency, dan Monetary (RFM)?

5. **Delivery Performance & Customer Satisfaction**  
   Seberapa besar keterlambatan pengiriman berkaitan dengan penurunan review score pelanggan?

## 📊 Dashboard Features

Dashboard dibangun menggunakan Streamlit dan menyediakan lima tab analisis interaktif.

| Tab | Analisis |
|---|---|
| Tren Penjualan | Tren jumlah pesanan dan revenue bulanan |
| Kategori Produk | Top 5 dan bottom 5 kategori berdasarkan revenue |
| Geografis | Distribusi pelanggan, revenue, dan pengiriman berdasarkan state |
| Segmentasi RFM | Segmentasi pelanggan berdasarkan Recency, Frequency, dan Monetary |
| Pengiriman & Kepuasan | Analisis keterlambatan pengiriman terhadap review score |

Dashboard juga dilengkapi filter interaktif berdasarkan:
- Periode transaksi
- State pelanggan
- Kategori produk

## 🛠️ Tech Stack

| Teknologi | Penggunaan |
|---|---|
| Python | Data processing dan analisis |
| Pandas | Data manipulation |
| NumPy | Numerical computation |
| Streamlit | Interactive dashboard |
| Plotly | Data visualization |
| Jupyter Notebook | Exploratory Data Analysis |
| CSV / Excel | Data storage dan processing |

## 📁 Project Structure

```text
submission/
│
├── dashboard/
│   ├── main_data.csv
│   └── dashboard.py
│
├── data/
│   ├── customers_dataset.csv
│   ├── geolocation_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── products_dataset.csv
│   └── sellers_dataset.csv
│
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## 🚀 Installation & Usage

### 1. Clone Repository

```bash
git clone https://github.com/vikinura/Streamlite-Proyek-analisis-data.git
```

### 2. Navigate to Project Directory

```bash
cd REPOSITORY
```

### 3. Install Dependencies

Pastikan Python versi 3.10 atau lebih baru sudah terpasang.

```bash
pip install -r requirements.txt
```

### 4. Run Streamlit Dashboard

```bash
streamlit run dashboard.py
```

Dashboard akan otomatis terbuka di browser melalui:

```text
http://localhost:8501
```

**Note:** Peta pada tab Geografis memerlukan koneksi internet.

## 📓 Running the Notebook

Untuk menjalankan proses Exploratory Data Analysis (EDA), gunakan perintah berikut:

```bash
pip install -r requirements.txt notebook
```

Kemudian jalankan:

```bash
jupyter notebook notebook.ipynb
```

Jalankan notebook dari direktori utama `submission` karena dataset dibaca dari folder `data`.

Notebook akan menghasilkan ulang file `dashboard/main_data.csv` yang digunakan oleh dashboard Streamlit.

## 🌐 Live Dashboard

Dashboard yang telah di-deploy dapat diakses melalui tautan berikut:

**[Open Interactive Dashboard](https://submiisonviki.streamlit.app/)**

## 📚 Dataset Source

**Brazilian E-Commerce Public Dataset by Olist**

Sumber: Kaggle

Dataset mencakup informasi transaksi, pelanggan, produk, pembayaran, ulasan, penjual, serta lokasi geografis dalam ekosistem marketplace Olist.


<p align="center">
  Developed with Python & Streamlit
</p>