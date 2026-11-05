Proyek analisis data menggunakan E-Commerce Public Dataset dari Olist (marketplace di Brasil) pada periode Januari 2017 sampai Agustus 2018. Analisis hanya memakai pesanan berstatus delivered. Seluruh nilai transaksi dalam Real Brasil (R$), dan revenue dihitung dari jumlah harga item tanpa ongkos kirim.

Proyek ini menjawab lima pertanyaan bisnis:
1. Kategori produk apa saja yang menjadi 5 penyumbang revenue terbesar dan terkecil.
2. Bagaimana tren jumlah pesanan dan revenue bulanan, dan kapan puncaknya.
3. State mana yang menyumbang revenue dan pelanggan terbanyak, serta berapa lama pengirimannya (analisis geospasial).
4. Bagaimana segmentasi pelanggan berdasarkan RFM (Recency, Frequency, Monetary).
5. Seberapa besar keterlambatan pengiriman menurunkan review score (binning).

## Struktur Folder

```
submission
├── dashboard
│   ├── main_data.csv
│   └── dashboard.py
├── data
│   ├── customers_dataset.csv
│   ├── geolocation_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── products_dataset.csv
│   └── sellers_dataset.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Cara Menjalankan Dashboard

Pastikan Python 3.10 atau lebih baru sudah terpasang. Buka terminal di folder `submission`, lalu jalankan:

```
pip install -r requirements.txt
streamlit run dashboard/dashboard.py
```

Dashboard akan terbuka di browser pada alamat http://localhost:8501. Peta pada tab Geografis memerlukan koneksi internet.

Dashboard dapat difilter berdasarkan periode, state pelanggan, dan kategori produk, dan memiliki lima tab: Tren Penjualan, Kategori Produk, Geografis, Segmentasi RFM, serta Pengiriman dan Kepuasan.

## Cara Menjalankan Notebook

```
pip install -r requirements.txt notebook
jupyter notebook notebook.ipynb
```

Jalankan notebook dari folder `submission` karena dataset dibaca dari folder `data`. Saat dijalankan, notebook akan membuat ulang file `dashboard/main_data.csv`.

## Link Dashboard

Dashboard yang sudah di-deploy dapat dibuka melalui tautan pada file `url.txt`.

## Sumber Data

Brazilian E-Commerce Public Dataset by Olist (Kaggle).