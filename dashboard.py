"""Dashboard Analisis E-Commerce Olist (Jan 2017 - Agu 2018).

Jalankan dari folder submission:
    streamlit run dashboard/dashboard.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Dashboard E-Commerce Olist", layout="wide")

ACCENT, MUTED, WARN, INK = "#2A6EBB", "#B4BAC2", "#D9822B", "#2B2F36"
SEGMENTS = ["Champions", "Repeat (At Risk)", "Potential Loyalists",
            "New / Low Spenders", "Win-back Priority", "Hibernating"]
DELAY_LABELS = ["Tepat waktu / lebih cepat", "Terlambat 1-3 hari", "Terlambat 4-7 hari", "Terlambat > 7 hari"]


# data
@st.cache_data
def load_data() -> pd.DataFrame:
    path = Path(__file__).resolve().parent / "main_data.csv"
    return pd.read_csv(path, parse_dates=["order_purchase_timestamp"])


def to_order_level(df: pd.DataFrame) -> pd.DataFrame:
    """Ringkas data level item menjadi level pesanan agar tidak terjadi penghitungan ganda."""
    return (df.groupby("order_id", as_index=False)
              .agg(customer_unique_id=("customer_unique_id", "first"),
                   customer_state=("customer_state", "first"),
                   purchase=("order_purchase_timestamp", "first"),
                   revenue=("price", "sum"),
                   delivery_days=("delivery_days", "first"),
                   delay_days=("delay_days", "first"),
                   review_score=("review_score", "first"),
                   lat=("customer_lat", "first"),
                   lng=("customer_lng", "first")))


def quartile_score(values: pd.Series, labels: list) -> pd.Series:
    try:
        return pd.qcut(values, 4, labels=labels).astype(int)
    except ValueError:  # terlalu banyak nilai kembar pada data hasil filter
        return pd.qcut(values.rank(method="first"), 4, labels=labels).astype(int)


def compute_rfm(ol: pd.DataFrame):
    snapshot = ol.purchase.max().normalize() + pd.Timedelta(days=1)
    rfm = (ol.groupby("customer_unique_id")
             .agg(last_purchase=("purchase", "max"), frequency=("order_id", "nunique"), monetary=("revenue", "sum"))
             .reset_index())
    rfm["recency"] = (snapshot - rfm.last_purchase.dt.normalize()).dt.days
    rfm["r_score"] = quartile_score(rfm.recency, [4, 3, 2, 1])
    rfm["f_score"] = np.select([rfm.frequency >= 3, rfm.frequency == 2], [3, 2], default=1)
    rfm["m_score"] = quartile_score(rfm.monetary, [1, 2, 3, 4])
    conditions = [
        (rfm.f_score >= 2) & (rfm.r_score >= 3),
        (rfm.f_score >= 2) & (rfm.r_score <= 2),
        (rfm.f_score == 1) & (rfm.r_score >= 3) & (rfm.m_score >= 3),
        (rfm.f_score == 1) & (rfm.r_score >= 3) & (rfm.m_score <= 2),
        (rfm.f_score == 1) & (rfm.r_score <= 2) & (rfm.m_score >= 3),
    ]
    rfm["segment"] = np.select(conditions, SEGMENTS[:5], default=SEGMENTS[5])
    return rfm, snapshot


def brl(x: float) -> str:
    return f"R${x / 1e6:,.2f}M" if abs(x) >= 1e6 else f"R${x / 1e3:,.1f}K"


def style(fig, height=380):
    fig.update_layout(template="plotly_white", height=height, margin=dict(l=0, r=10, t=50, b=0),
                      font=dict(color=INK), title_font=dict(size=15), legend_title_text="")
    return fig


#  load + filters
df_all = load_data()
min_d, max_d = df_all.order_purchase_timestamp.min().date(), df_all.order_purchase_timestamp.max().date()

with st.sidebar:
    st.header("Filter")
    date_range = st.date_input("Periode pembelian", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    states = st.multiselect("State pelanggan", sorted(df_all.customer_state.dropna().unique()), placeholder="Semua state")
    categories = st.multiselect("Kategori produk", sorted(df_all.product_category_english.unique()), placeholder="Semua kategori")
    st.caption("Kosongkan pilihan untuk menampilkan semua state / kategori.")
    st.divider()
    st.caption("Sumber: Olist Brazilian E-Commerce. Hanya pesanan berstatus *delivered*. "
               "Revenue = jumlah harga item (tanpa ongkos kirim), dalam Real Brasil (R$).")

st.title("Dashboard Analisis E-Commerce Olist")
st.caption("Pesanan delivered, 1 Januari 2017 - 31 Agustus 2018. Semua grafik mengikuti filter di sebelah kiri.")

if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
    st.info("Pilih tanggal awal dan tanggal akhir pada filter periode.")
    st.stop()

start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
df = df_all[(df_all.order_purchase_timestamp >= start) & (df_all.order_purchase_timestamp < end)]
if states:
    df = df[df.customer_state.isin(states)]
if categories:
    df = df[df.product_category_english.isin(categories)]

if df.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini. Ubah periode, state, atau kategori.")
    st.stop()

ol = to_order_level(df)

# KPI
revenue, n_orders, n_customers = df.price.sum(), ol.order_id.nunique(), ol.customer_unique_id.nunique()
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total revenue", f"R$ {revenue:,.0f}")
k2.metric("Jumlah pesanan", f"{n_orders:,}")
k3.metric("Pelanggan unik", f"{n_customers:,}")
k4.metric("Rata-rata nilai pesanan", f"R$ {revenue / n_orders:,.2f}")
k5, k6, k7, _ = st.columns(4)
k5.metric("Rata-rata lama kirim", f"{ol.delivery_days.mean():.1f} hari")
k6.metric("Rata-rata review score", f"{ol.review_score.mean():.2f} / 5")
k7.metric("Pesanan terlambat", f"{(ol.delay_days > 0).mean() * 100:.1f}%")

tab_trend, tab_cat, tab_geo, tab_rfm, tab_ship = st.tabs(
    ["Tren Penjualan", "Kategori Produk", "Geografis", "Segmentasi RFM", "Pengiriman & Kepuasan"])

# tab 1: tren
with tab_trend:
    st.subheader("Bagaimana tren pesanan dan revenue bulanan?")
    monthly = (ol.set_index("purchase").resample("MS")
                 .agg(orders=("order_id", "nunique"), revenue=("revenue", "sum")).reset_index())
    monthly["mom_pct"] = monthly.revenue.pct_change() * 100
    peak = monthly.loc[monthly.revenue.idxmax()]
    st.markdown(f"**Puncak revenue pada periode terpilih:** {peak.purchase:%B %Y} ({brl(peak.revenue)}; {int(peak.orders):,} pesanan).")

    c1, c2 = st.columns(2)
    f1 = px.line(monthly, x="purchase", y="orders", markers=True, title="Jumlah pesanan per bulan",
                 labels={"purchase": "Bulan", "orders": "Pesanan"}, color_discrete_sequence=[ACCENT])
    f1.update_yaxes(rangemode="tozero"); f1.update_traces(hovertemplate="%{x|%b %Y}<br>%{y:,} pesanan<extra></extra>")
    c1.plotly_chart(style(f1))
    f2 = px.line(monthly, x="purchase", y="revenue", markers=True, title="Total revenue per bulan (R$)",
                 labels={"purchase": "Bulan", "revenue": "Revenue (R$)"}, color_discrete_sequence=[ACCENT])
    f2.update_yaxes(rangemode="tozero"); f2.update_traces(hovertemplate="%{x|%b %Y}<br>R$ %{y:,.0f}<extra></extra>")
    c2.plotly_chart(style(f2))

    g = monthly.dropna(subset=["mom_pct"]).copy()
    if not g.empty:
        g["arah"] = np.where(g.mom_pct >= 0, "Naik", "Turun")
        f3 = px.bar(g, x="purchase", y="mom_pct", color="arah", title="Pertumbuhan revenue Month-over-Month (%)",
                    color_discrete_map={"Naik": ACCENT, "Turun": WARN}, labels={"purchase": "Bulan", "mom_pct": "MoM (%)"})
        f3.update_traces(hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra></extra>")
        st.plotly_chart(style(f3, 320))

# tab 2: kategori
with tab_cat:
    st.subheader("Kategori produk apa yang menyumbang revenue terbesar dan terkecil?")
    cat = (df.groupby("product_category_english")
             .agg(revenue=("price", "sum"), items=("order_item_id", "count"), orders=("order_id", "nunique"))
             .sort_values("revenue", ascending=False))
    cat["share_pct"] = cat.revenue / cat.revenue.sum() * 100
    cat["avg_price"] = cat.revenue / cat["items"]
    rank = cat.drop(index="Unknown", errors="ignore")

    if rank.empty:
        st.info("Tidak ada kategori berlabel pada filter ini.")
    else:
        a, b = st.columns([2, 3])
        n_top = a.slider("Jumlah kategori ditampilkan", 3, 15, 5)
        mode = b.radio("Urutan", ["Revenue terbesar", "Revenue terkecil"], horizontal=True)
        n_top = min(n_top, len(rank))
        view = rank.head(n_top) if mode == "Revenue terbesar" else rank.tail(n_top)
        view = view.iloc[::-1].reset_index()
        fig = px.bar(view, x="revenue", y="product_category_english", orientation="h",
                     text=view.apply(lambda r: f"{brl(r.revenue)} ({r.share_pct:.2f}%)", axis=1),
                     title=f"{n_top} kategori dengan {mode.lower()}",
                     labels={"revenue": "Revenue (R$)", "product_category_english": ""},
                     color_discrete_sequence=[ACCENT if mode == "Revenue terbesar" else MUTED])
        fig.update_traces(textposition="outside", cliponaxis=False,
                          hovertemplate="%{y}<br>Revenue: R$ %{x:,.0f}<extra></extra>")
        fig.update_xaxes(range=[0, view.revenue.max() * 1.35])
        st.plotly_chart(style(fig, 80 + 38 * n_top))
        st.caption(f"{n_top} kategori ini menyumbang {view.share_pct.sum():.2f}% dari total revenue pada filter terpilih. "
                   "Kategori tanpa label (Unknown) tidak diikutkan dalam peringkat.")
        st.dataframe(rank.head(15).rename(columns={"revenue": "Revenue (R$)", "items": "Item terjual", "orders": "Pesanan",
                                                   "share_pct": "Kontribusi (%)", "avg_price": "Harga rata-rata (R$)"})
                     .round(2))

# tab 3: geografis
with tab_geo:
    st.subheader("State mana yang menyumbang revenue dan pelanggan terbanyak, dan berapa lama pengirimannya?")
    state = (ol.groupby("customer_state")
               .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"), customers=("customer_unique_id", "nunique"),
                    avg_delivery_days=("delivery_days", "mean"), lat=("lat", "mean"), lng=("lng", "mean"))
               .sort_values("revenue", ascending=False))
    state["revenue_share_pct"] = state.revenue / state.revenue.sum() * 100

    color_by = st.radio("Warna lingkaran pada peta berdasarkan", ["Rata-rata lama pengiriman (hari)", "Jumlah pelanggan"], horizontal=True)
    color_col = "avg_delivery_days" if color_by.startswith("Rata-rata") else "customers"
    left, right = st.columns([3, 2])

    geo = state.dropna(subset=["lat", "lng"]).reset_index()
    if geo.empty:
        left.info("Tidak ada koordinat pada filter ini.")
    else:
        fig = px.scatter_geo(geo, lat="lat", lon="lng", size="revenue", color=color_col, hover_name="customer_state",
                             hover_data={"lat": False, "lng": False, "revenue": ":,.0f", "customers": ":,",
                                         "avg_delivery_days": ":.1f"},
                             size_max=48, color_continuous_scale="Blues", scope="south america",
                             labels={"revenue": "Revenue (R$)", "customers": "Pelanggan",
                                     "avg_delivery_days": "Lama kirim (hari)"},
                             title="Ukuran lingkaran = revenue")
        fig.update_geos(fitbounds="locations", showcountries=True, countrycolor=MUTED, showland=True, landcolor="#F4F5F7")
        left.plotly_chart(style(fig, 520))

    top10 = state.head(10).reset_index()
    f_rev = px.bar(top10.iloc[::-1], x="revenue", y="customer_state", orientation="h", title="Revenue 10 state teratas (R$)",
                   labels={"revenue": "Revenue (R$)", "customer_state": ""}, color_discrete_sequence=[ACCENT],
                   text=top10.iloc[::-1].revenue_share_pct.map(lambda v: f"{v:.1f}%"))
    f_rev.update_traces(textposition="outside", cliponaxis=False, hovertemplate="%{y}: R$ %{x:,.0f}<extra></extra>")
    f_rev.update_xaxes(range=[0, top10.revenue.max() * 1.25])
    right.plotly_chart(style(f_rev, 300))
    f_del = px.bar(top10.iloc[::-1], x="avg_delivery_days", y="customer_state", orientation="h",
                   title="Rata-rata lama pengiriman (hari), urutan sama", labels={"avg_delivery_days": "Hari", "customer_state": ""},
                   color_discrete_sequence=[WARN], text=top10.iloc[::-1].avg_delivery_days.map(lambda v: f"{v:.1f}"))
    f_del.update_traces(textposition="outside", cliponaxis=False, hovertemplate="%{y}: %{x:.1f} hari<extra></extra>")
    f_del.update_xaxes(range=[0, top10.avg_delivery_days.max() * 1.2])
    right.plotly_chart(style(f_del, 300))

    slowest = state[state.customers >= 30].sort_values("avg_delivery_days", ascending=False).head(5)
    if not slowest.empty:
        st.caption("State dengan pengiriman terlama (minimal 30 pelanggan): " +
                   ", ".join(f"{s} ({r.avg_delivery_days:.1f} hari)" for s, r in slowest.iterrows()) + ".")

# tab 4: RFM
with tab_rfm:
    st.subheader("Bagaimana segmentasi pelanggan berdasarkan RFM?")
    if ol.customer_unique_id.nunique() < 8:
        st.info("Jumlah pelanggan terlalu sedikit untuk segmentasi RFM. Perluas filter.")
    else:
        rfm, snapshot = compute_rfm(ol)
        seg = (rfm.groupby("segment")
                  .agg(customers=("customer_unique_id", "count"), revenue=("monetary", "sum"),
                       avg_recency=("recency", "mean"), avg_frequency=("frequency", "mean"), avg_monetary=("monetary", "mean"))
                  .reindex(SEGMENTS).fillna(0))
        seg["customers_pct"] = seg.customers / seg.customers.sum() * 100
        seg["revenue_pct"] = seg.revenue / seg.revenue.sum() * 100
        repeat = (rfm.frequency > 1).mean() * 100
        st.markdown(f"Tanggal acuan RFM: **{snapshot:%d %b %Y}** (sehari setelah pesanan terakhir pada filter). "
                    f"Pelanggan yang membeli lebih dari sekali: **{repeat:.1f}%**.")

        plot_seg = seg.reset_index().iloc[::-1]
        c1, c2 = st.columns(2)
        for col, key, ttl, color in [(c1, "customers_pct", "% pelanggan per segmen", MUTED), (c2, "revenue_pct", "% revenue per segmen", ACCENT)]:
            f = px.bar(plot_seg, x=key, y="segment", orientation="h", title=ttl, text=plot_seg[key].map(lambda v: f"{v:.1f}%"),
                       labels={key: "%", "segment": ""}, color_discrete_sequence=[color])
            f.update_traces(textposition="outside", cliponaxis=False, hovertemplate="%{y}: %{x:.1f}%<extra></extra>")
            f.update_xaxes(range=[0, max(seg.customers_pct.max(), seg.revenue_pct.max()) * 1.2])
            col.plotly_chart(style(f, 360))

        st.dataframe(seg.rename(columns={"customers": "Pelanggan", "revenue": "Revenue (R$)", "avg_recency": "Rata-rata recency (hari)",
                                         "avg_frequency": "Rata-rata frekuensi", "avg_monetary": "Rata-rata belanja (R$)",
                                         "customers_pct": "% pelanggan", "revenue_pct": "% revenue"}).round(2))
        with st.expander("Cara membaca segmen RFM"):
            st.markdown("""
- **Recency**: hari sejak pembelian terakhir (skor 1-4 berdasarkan kuartil; 4 = paling baru).
- **Frequency**: jumlah pesanan unik (skor 1 = 1 kali, 2 = 2 kali, 3 = 3 kali atau lebih).
- **Monetary**: total revenue pelanggan (skor 1-4 berdasarkan kuartil).
- **Champions**: membeli berulang dan baru-baru ini. **Repeat (At Risk)**: membeli berulang tetapi sudah lama tidak belanja.
- **Potential Loyalists**: pembeli satu kali, baru, belanja tinggi. **New / Low Spenders**: pembeli satu kali, baru, belanja rendah.
- **Win-back Priority**: pembeli satu kali, sudah lama, belanja tinggi. **Hibernating**: pembeli satu kali, sudah lama, belanja rendah.
""")

# tab 5: pengiriman & kepuasan
with tab_ship:
    st.subheader("Seberapa besar keterlambatan pengiriman menurunkan kepuasan pelanggan?")
    rv = ol.dropna(subset=["review_score", "delay_days"]).copy()
    if rv.empty:
        st.info("Tidak ada data ulasan pada filter ini.")
    else:
        rv["delay_bin"] = pd.cut(rv.delay_days, bins=[-np.inf, 0, 3, 7, np.inf], labels=DELAY_LABELS)
        rv["low_score"] = rv.review_score <= 2
        bins = (rv.groupby("delay_bin", observed=False)
                  .agg(orders=("order_id", "count"), avg_score=("review_score", "mean"), low_score_pct=("low_score", "mean"))
                  .reset_index())
        bins["low_score_pct"] *= 100
        bins["warna"] = ["Tepat waktu"] + ["Terlambat"] * 3
        cmap = {"Tepat waktu": ACCENT, "Terlambat": WARN}

        c1, c2 = st.columns(2)
        f1 = px.bar(bins, x="delay_bin", y="avg_score", color="warna", color_discrete_map=cmap,
                    text=bins.avg_score.map(lambda v: "-" if pd.isna(v) else f"{v:.2f}"), title="Rata-rata review score (skala 1-5)",
                    labels={"delay_bin": "", "avg_score": "Skor"}, hover_data={"orders": ":,"})
        f1.update_yaxes(range=[0, 5]); f1.update_layout(showlegend=False); f1.update_traces(textposition="outside")
        c1.plotly_chart(style(f1, 380))
        f2 = px.bar(bins, x="delay_bin", y="low_score_pct", color="warna", color_discrete_map=cmap,
                    text=bins.low_score_pct.map(lambda v: "-" if pd.isna(v) else f"{v:.1f}%"), title="Persentase ulasan buruk (skor 1-2)",
                    labels={"delay_bin": "", "low_score_pct": "%"}, hover_data={"orders": ":,"})
        f2.update_yaxes(range=[0, 105]); f2.update_layout(showlegend=False); f2.update_traces(textposition="outside")
        c2.plotly_chart(style(f2, 380))
        st.caption("Keterlambatan = tanggal tiba aktual dikurangi tanggal estimasi. Hanya pesanan yang memiliki ulasan. "
                   "Ini menunjukkan hubungan (asosiasi), bukan bukti sebab-akibat murni.")
        st.dataframe(bins.drop(columns="warna").rename(columns={"delay_bin": "Kelompok keterlambatan", "orders": "Pesanan",
                                                                 "avg_score": "Rata-rata skor", "low_score_pct": "% ulasan buruk"}).round(2))