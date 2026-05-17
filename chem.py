import streamlit as st
import requests
import py3Dmol
from stmol import showmol
import math
import streamlit.components.v1 as components
import io
import matplotlib.pyplot as plt

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="ChemPro AI - Kelompok 1", 
    page_icon="🧪", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. DATABASE ALAT KIMIA LOKAL ---
DATABASE_ALAT = {
    "gelas kimia": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?q=80&w=600&auto=format&fit=crop", 
    "labu erlenmeyer": "https://commons.wikimedia.org/wiki/Special:FilePath/Erlenmeyer_flask.jpg?width=480",
    "gelas ukur": "https://commons.wikimedia.org/wiki/Special:FilePath/Measuring_cylinder.jpg?width=480",
    "tabung reaksi": "https://images.unsplash.com/photo-1576086213369-97a306d36557?q=80&w=600&auto=format&fit=crop", 
    "rak tabung reaksi": "https://images.unsplash.com/photo-1583912265922-98fc11c10924?q=80&w=600&auto=format&fit=crop", 
    "pipet tetes": "https://commons.wikimedia.org/wiki/Special:FilePath/Pipette_01.jpg?width=480",
    "pipet volume": "https://commons.wikimedia.org/wiki/Special:FilePath/Volumetric_pipette.jpg?width=480",
    "pipet ukur": "https://commons.wikimedia.org/wiki/Special:FilePath/Graduated_pipette.jpg?width=480",
    "buret": "https://commons.wikimedia.org/wiki/Special:FilePath/Burette.jpg?width=480",
    "labu ukur": "https://commons.wikimedia.org/wiki/Special:FilePath/Volumetric_flask.jpg?width=480",
    "batang pengaduk": "https://commons.wikimedia.org/wiki/Special:FilePath/Glass_stir_rod.jpg?width=480",
    "corong kaca": "https://commons.wikimedia.org/wiki/Special:FilePath/Funnel.jpg?width=480",
    "kaca arloji": "https://commons.wikimedia.org/wiki/Special:FilePath/Watch_glass.jpg?width=480",
    "mortar dan alu": "https://commons.wikimedia.org/wiki/Special:FilePath/Mortar_and_pestle.jpg?width=480",
    "spatula": "https://commons.wikimedia.org/wiki/Special:FilePath/Spatula.jpg?width=480",
    "neraca analitik": "https://commons.wikimedia.org/wiki/Special:FilePath/Analytical_balance.jpg?width=480",
    "pembakar bunsen": "https://commons.wikimedia.org/wiki/Special:FilePath/Bunsen_burner.jpg?width=480",
    "kaki tiga": "https://commons.wikimedia.org/wiki/Special:FilePath/Tripod_(laboratory).jpg?width=480",
    "kawat kasa": "https://commons.wikimedia.org/wiki/Special:FilePath/Wire_gauze.jpg?width=480",
    "cawan penguap": "https://commons.wikimedia.org/wiki/Special:FilePath/Evaporating_dish.jpg?width=480",
    "krusibel": "https://commons.wikimedia.org/wiki/Special:FilePath/Crucible.jpg?width=480",
    "botol semprot": "https://commons.wikimedia.org/wiki/Special:FilePath/Wash_bottle.jpg?width=480",
    "termometer": "https://commons.wikimedia.org/wiki/Special:FilePath/Thermometer.jpg?width=480",
    "klem dan statif": "https://commons.wikimedia.org/wiki/Special:FilePath/Retort_stand.jpg?width=480",
    "desikator": "https://commons.wikimedia.org/wiki/Special:FilePath/Desiccator.jpg?width=480",
    "sentrifugasi": "https://commons.wikimedia.org/wiki/Special:FilePath/Tabletop_centrifuge.jpg?width=480",
    "kertas saring": "https://commons.wikimedia.org/wiki/Special:FilePath/Filter_paper.jpg?width=480",
    "corong pisah": "https://commons.wikimedia.org/wiki/Special:FilePath/Separatory_funnel.jpg?width=480",
    "indikator universal": "https://commons.wikimedia.org/wiki/Special:FilePath/Universal_indicator_paper.jpg?width=480",
    "lemari asam": "https://commons.wikimedia.org/wiki/Special:FilePath/Fume_hood.jpg?width=480"
}

# --- 3. FUNGSI PENDUKUNG ---
def tampilkan_gambar_aman(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            st.image(io.BytesIO(response.content), width=380)
        else:
            st.warning("⚠️ Server gambar sedang sibuk, visualisasi tidak dapat dimuat saat ini.")
    except Exception:
        st.warning("⚠️ Kesalahan koneksi saat memuat gambar.")

@st.cache_data
def cari_gambar_wikipedia_pro(query):
    try:
        search_url = f"https://id.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=1&format=json"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res_search = requests.get(search_url, headers=headers).json()
        if len(res_search[1]) > 0:
            best_title = res_search[1][0]
            summary_url = f"https://id.wikipedia.org/api/rest_v1/page/summary/{best_title.replace(' ', '_')}"
            res_summary = requests.get(summary_url, headers=headers).json()
            if 'thumbnail' in res_summary:
                return res_summary['thumbnail']['source'], f"🔍 Ditemukan: **{best_title}**"
    except: return None, None
    return None, None

@st.cache_data
def cari_struktur_pubchem(query):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{query.strip()}/PNG"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200: return url, f"🔬 Struktur Kimia 2D: **{query.title()}**"
    except: return None, None
    return None, None

@st.cache_data
def get_chem_data(nama_zat):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{nama_zat}/property/MolecularWeight,MolecularFormula,IUPACName/JSON"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['PropertyTable']['Properties'][0]
            return {"mr": float(data.get('MolecularWeight', 0)), "formula": data.get('MolecularFormula', 'N/A')}
        return None
    except: return None

@st.cache_data
def get_3d_sdf(nama_zat):
    nama_zat = nama_zat.strip()
    url_3d = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{nama_zat}/record/SDF/?record_type=3d"
    try:
        response = requests.get(url_3d)
        if response.status_code == 200: return response.text
        url_2d = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{nama_zat}/record/SDF/?record_type=2d"
        res_2d = requests.get(url_2d)
        if res_2d.status_code == 200: return res_2d.text
        return None
    except: return None

@st.cache_data
def get_wiki_summary(nama_zat):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{nama_zat}"
        response = requests.get(url)
        if response.status_code == 200: return response.json().get('extract', 'Deskripsi tidak ditemukan.')
        return "Deskripsi tidak tersedia."
    except: return "Gagal memuat ensiklopedia."

def render_3d_molecule(sdf_data):
    view = py3Dmol.view(width=800, height=450)
    view.addModel(sdf_data, 'sdf')
    view.setStyle({'stick': {'radius': 0.15}, 'sphere': {'scale': 0.3}})
    view.setBackgroundColor('rgba(14, 17, 23, 0)') 
    view.zoomTo()
    view.spin(True)
    showmol(view, height=450, width=800)

@st.cache_data(ttl=3600)
def cari_jurnal_akademik(query, batas_tahun, jumlah_hasil=5):
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "filter": f"type:journal-article,from-pub-date:{batas_tahun}-01-01",
        "select": "title,author,published,URL,DOI,is-referenced-by-count,publisher",
        "sort": "relevance",
        "rows": jumlah_hasil
    }
    headers = {'User-Agent': 'ChemProAI_EduProject/5.0'}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code == 200: return response.json()['message']['items']
        return None
    except: return None

# --- 4. SIDEBAR (NAVIGASI) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/995/995440.png", width=80)
    st.title("ChemPro AI")
    st.caption("Lab Assistant v4.0")
    st.divider()
    
    # MENU TELAH DIPADATKAN (PENGGABUNGAN FITUR)
    menu = st.radio("Pilih Modul Utama:", 
             ["🧮 Kalkulator & Simulasi Terpadu",
              "🌐 Ensiklopedia 3D", 
              "🛡️ K3 & Keamanan Lab", 
              "📋 Generator Diagram Alir", 
              "🤖 Asisten AI Kimia",
              "📚 Pustaka Jurnal Pro", 
              "🎓 Ujian HOTS Pro"], key="modul_lab")
    st.divider()
    
    st.markdown("### 🛠️ Developer:")
    st.success("""**✨ Kelompok 1**\n
**Anggota Tim:**
• Gusti Ayu Made Artiwi
• Tinsi Pebriani
• Ashila Agnia
• Afdlo Khairul Hafiz
• Bunga Ria Lestari S
• Sep Fanni Ferin Dinika
• Afifa Nabilatu Zahra\n
Pendidikan Kimia 2024
Universitas Lampung""")


# --- 5. LOGIKA DYNAMIC BACKGROUND ---
BG_SPACE_1 = "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=2000&auto=format&fit=crop"
BG_SPACE_2 = "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2000&auto=format&fit=crop"
BG_SPACE_4 = "https://images.unsplash.com/photo-1464802686167-b939a6910659?q=80&w=2000&auto=format&fit=crop"
BG_SPACE_5 = "https://images.unsplash.com/photo-1534447677768-be436bb09401?q=80&w=2000&auto=format&fit=crop"

if menu in ["🤖 Asisten AI Kimia", "🌐 Ensiklopedia 3D"]:
    active_bg = BG_SPACE_1
elif menu == "🧮 Kalkulator & Simulasi Terpadu":
    active_bg = BG_SPACE_2
elif menu in ["🛡️ K3 & Keamanan Lab", "📋 Generator Diagram Alir"]:
    active_bg = BG_SPACE_4
elif menu in ["📚 Pustaka Jurnal Pro", "🎓 Ujian HOTS Pro"]:
    active_bg = BG_SPACE_5


# --- 6. INJEKSI CSS ---
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {{
        background-color: transparent !important;
    }}
    @keyframes panBackground {{
        0% {{ background-position: 0% 0%; }}
        50%