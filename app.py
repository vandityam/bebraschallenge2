# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# =============================================================================
# KONFIGURASI DASHBOARD
# =============================================================================
st.set_page_config(page_title="Bebras CT Dashboard", layout="wide")
st.title("Dashboard Hasil Bebras Challenge 2024")
st.markdown("Visualisasi kemampuan **Computational Thinking** siswa SD, SMP, dan SMA berdasarkan data hasil pengerjaan soal Bebras.")

# =============================================================================
# LOAD DATA
# =============================================================================
@st.cache_data
def load_data():
    bebras = pd.read_csv("dashboard_bebras.csv")
    return bebras

bebras = load_data()

# =============================================================================
# MAPPING
# =============================================================================
mapping_kat = (
    bebras[["Kategori", "Kelas"]]
    .drop_duplicates()
    .groupby("Kategori")["Kelas"]
    .apply(list)
    .to_dict()
)

mapping_prov = (
    bebras[["Provinsi", "SekolahKotaKabupaten"]]
    .drop_duplicates()
    .groupby("Provinsi")["SekolahKotaKabupaten"]
    .apply(list)
    .to_dict()
)

# =============================================================================
# SIDEBAR FILTER
# =============================================================================
st.sidebar.header("🔍 Filter Data")

# ---- Provinsi ----
provinsi = st.sidebar.multiselect(
    "Pilih Provinsi:",
    sorted(bebras["Provinsi"].dropna().unique())
)

# ---- Kota/Kabupaten ----
all_kota = sorted(bebras["SekolahKotaKabupaten"].dropna().unique())

if provinsi:
    allowed_kota = sorted({k for p in provinsi for k in mapping_prov.get(p, [])})

    kota = st.sidebar.multiselect(
        "Pilih Kota/Kabupaten:",
        allowed_kota,
        disabled=True
    )
else:
    kota = st.sidebar.multiselect(
        "Pilih Kota/Kabupaten:",
        all_kota
    )

# ---- Kategori ----
kategori = st.sidebar.multiselect(
    "Pilih Kategori:",
    sorted(bebras["Kategori"].dropna().unique())
)

# ---- Kelas ----
all_kelas = sorted(bebras["Kelas"].dropna().unique())

if kategori:
    allowed_kelas = sorted({k for cat in kategori for k in mapping_kat.get(cat, [])})

    kelas = st.sidebar.multiselect(
        "Pilih Kelas (Mengikuti Kategori):",
        allowed_kelas,
        disabled=True
    )
else:
    kelas = st.sidebar.multiselect(
        "Pilih Kelas:",
        all_kelas
    )

# =============================================================================
# FILTER DATA
# =============================================================================
filtered = bebras.copy()

if provinsi:
    filtered = filtered[filtered["Provinsi"].isin(provinsi)]

if kota:
    filtered = filtered[filtered["SekolahKotaKabupaten"].isin(kota)]

if kategori:
    filtered = filtered[filtered["Kategori"].isin(kategori)]

if kelas:
    filtered = filtered[filtered["Kelas"].isin(kelas)]

st.sidebar.write(f"Total data: {len(filtered)} peserta")


# =============================================================================
# 1️⃣ STATISTIK RINGKAS
# =============================================================================
st.subheader("📈 Statistik Umum")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Jumlah Peserta", len(filtered))
col2.metric("Rata-rata Nilai", round(filtered["Nilai"].mean(), 2))
col3.metric("Nilai Tertinggi", round(filtered["Nilai"].max(), 2))
col4.metric("Nilai Terendah", round(filtered["Nilai"].min(), 2))

# =============================================================================
# 2️⃣ DISTRIBUSI DEMOGRAFI
# =============================================================================
st.subheader("👥 Distribusi Peserta")

col1, col2 = st.columns(2)

with col1:
    gender_counts = filtered["JenisKelamin"].value_counts().reset_index()
    gender_counts.columns = ["JenisKelamin", "count"]
    fig_gender = px.pie(
        gender_counts,
        values="count",
        names="JenisKelamin",
        title="Distribusi Berdasarkan Jenis Kelamin",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_gender, use_container_width=True)

with col2:
    kategori_counts = filtered["Kategori"].value_counts().reset_index()
    kategori_counts.columns = ["Kategori", "count"]
    fig_kategori = px.pie(
        kategori_counts,
        values="count",
        names="Kategori",
        title="Distribusi Berdasarkan Kategori",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_kategori, use_container_width=True)

# =============================================================================
# 3️⃣ NILAI PESERTA
# =============================================================================
st.subheader("🎯 Analisis Nilai Peserta")

tab1, tab2, tab3 = st.tabs(["Distribusi Nilai", "Perbandingan", "Provinsi"])

with tab1:
    fig_hist = px.histogram(
        filtered, x="Nilai", nbins=10, title="Distribusi Nilai Peserta",
        color_discrete_sequence=["#82C9FF"]
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    fig_box = px.box(filtered, y="Nilai", title="Sebaran Nilai (Boxplot)")
    st.plotly_chart(fig_box, use_container_width=True)

with tab2:
    col1, col2, col3 = st.columns(3)
    with col1:
        fig_gender = px.box(filtered, x="JenisKelamin", y="Nilai", title="Nilai Berdasarkan Jenis Kelamin")
        st.plotly_chart(fig_gender, use_container_width=True)
    with col2:
        fig_kelas = px.box(filtered, x="Kelas", y="Nilai", title="Nilai Berdasarkan Kelas")
        st.plotly_chart(fig_kelas, use_container_width=True)
    with col3:
        fig_kategori = px.bar(
            filtered.groupby("Kategori", as_index=False)["Nilai"].mean(),
            x="Kategori", y="Nilai", title="Rata-rata Nilai Berdasarkan Kategori",
            color="Kategori", color_discrete_sequence=px.colors.qualitative.Vivid
        )
        st.plotly_chart(fig_kategori, use_container_width=True)

with tab3:
    top_prov = filtered["Provinsi"].value_counts().head(10).reset_index()
    top_prov.columns = ["Provinsi", "Jumlah Peserta"]
    fig_prov = px.bar(
        top_prov, x="Jumlah Peserta", y="Provinsi",
        orientation="h", title="10 Provinsi dengan Jumlah Peserta Terbanyak",
        color="Jumlah Peserta", color_continuous_scale="Blues"
    )
    st.plotly_chart(fig_prov, use_container_width=True)

# =============================================================================
# 4️⃣ HUBUNGAN NILAI & DURASI
# =============================================================================
st.subheader("⏱️ Hubungan Nilai dan Durasi Tes")

if "Durasi_min" in filtered.columns:
    fig_corr = px.scatter(
        filtered, x="Durasi_min", y="Nilai",
        trendline="ols", title="Korelasi Durasi Tes dan Nilai"
    )
    st.plotly_chart(fig_corr, use_container_width=True)
else:
    st.warning("Kolom Durasi_min belum tersedia di dataset!")

# =============================================================================
# 5️⃣ TABEL DATA
# =============================================================================
st.subheader("🏆 Top 10 Peserta Dengan Nilai Tertinggi")
top10 = filtered.nlargest(10, 'Nilai')[['Nama', 'Kelas', 'SekolahNama', 'SekolahKotaKabupaten', 'Nilai']]
top10.index = range(1, len(top10) + 1)
top10 = top10.rename(columns={'Nama': 'Nama', 'Kelas' : 'Kelas', 'SekolahNama': 'Sekolah', 'SekolahKotaKabupaten': 'Kota/Kab', 'Nilai': 'Nilai'})
st.dataframe(top10.style.format({'Nilai': '{:.2f}'}), use_container_width=True)
col_d1, col_d2 = st.columns(2)
with st.expander("📋 Tampilkan Seluruh Data"):
 st.dataframe(
        filtered[['Nama', 'Kelas','SekolahNama', 'SekolahKotaKabupaten', 'Nilai']],
        use_container_width=True
    )
