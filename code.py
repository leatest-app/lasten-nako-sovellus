import streamlit as st
from PIL import Image, ImageFilter, ImageEnhance
import os

st.set_page_config(page_title="Lapsen Näkösimulaattori", layout="wide")

st.title("👁️ Lapsen Näön Kehitys (0–3 v.)")
st.sidebar.header("Säädöt")

# --- KUVAN VALINTA ---
st.sidebar.subheader("Valitse näkymä")
kuvavalinta = st.sidebar.selectbox(
    "Mitä lapsi katsoo?",
    ["Äiti", "Vesivärit (Leikkihuone)", "Lea-testitaulu", "Lataa oma kuva"]
)

image_map = {
    "Äiti": "aiti.jpg",
    "Vesivärit (Leikkihuone)": "leikkihuone.jpg",
    "Lea-testitaulu": "lea.jpg"
}

def load_local_image(filename):
    if os.path.exists(filename):
        return Image.open(filename)
    return None

img = None

if kuvavalinta == "Lataa oma kuva":
    uploaded_file = st.file_uploader("Lataa JPG tai PNG kuva", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        img = Image.open(uploaded_file)
    else:
        st.info("Lataa kuva nähdäksesi simulaation.")
        st.stop()
else:
    fname = image_map[kuvavalinta]
    img = load_local_image(fname)
    if img is None:
        st.error(f"Tiedostoa '{fname}' ei löytynyt GitHubista. Lataa se GitHubiin, jotta tämä näkymä toimii!")
        st.stop()

# --- IKÄ JA SIMULAATIO ---
ika = st.sidebar.select_slider(
    'Lapsen ikä',
    options=['Vastasyntynyt', '1-2 kk', '3-4 kk', '6 kk', '12 kk', '2 v.', '3 v.'],
    value='Vastasyntynyt'
)

st.sidebar.subheader("Simuloi häiriöitä")
karsastus = st.sidebar.checkbox("Karsastus (Kaksoiskuva)")
laiska_silma = st.sidebar.checkbox("Laiska silmä (Amblyopia)")
kontrasti_check = st.sidebar.checkbox("Heikko kontrastinherkkyys")

# --- KEHITYSDATA ---
settings = {
    'Vastasyntynyt': {'blur': 25, 'sat': 0.0, 'contrast': 0.2, 'info': "Vauva näkee äidin kasvot ja vesivärit vain harmaina hahmoina. Silmälasit eivät vielä erotu hahmosta."},
    '1-2 kk': {'blur': 15, 'sat': 0.3, 'contrast': 0.4, 'info': "Kasvojen ja esineiden ääriviivat alkavat hahmottua. Punainen vesiväri alkaa erottua muista."},
    '3-4 kk': {'blur': 8, 'sat': 0.7, 'contrast': 0.7, 'info': "Äidin silmälasit alkavat erottua kasvoilla. Lapsi alkaa kiinnostua vesivärien eri sävyistä."},
    '6 kk': {'blur': 3, 'sat': 1.0, 'contrast': 0.9, 'info': "Lapsi alkaa nähdä vesiväripurkkien pienempiä yksityiskohtia. Syvyysnäkö auttaa kurottamisessa."},
    '12 kk': {'blur': 1.5, 'sat': 1.0, 'contrast': 1.0, 'info': "Lapsi erottaa jo pienetkin roiskeet paperilla. Näkö on varsin tarkka kotiympäristössä."},
    '2 v.': {'blur': 0.5, 'sat': 1.0, 'contrast': 1.0, 'info': "Lapsi pystyy nimeämään värejä ja erottamaan hyvin pieniä yksityiskohtia."},
    '3 v.': {'blur': 0, 'sat': 1.0, 'contrast': 1.0, 'info': "Näkö on täysin kehittynyt. On aika tehdä ensimmäinen virallinen Lea-testi."}
}

current = settings[ika]
processed_img = img.copy()

# Sumennus
if current['blur'] > 0:
    processed_img = processed_img.filter(ImageFilter.GaussianBlur(radius=current['blur']))

# Värit
color_enhancer = ImageEnhance.Color(processed_img)
processed_img = color_enhancer.enhance(current['sat'])

# Kontrasti
contrast_val = 0.2 if kontrasti_check else current['contrast']
contrast_enhancer = ImageEnhance.Contrast(processed_img)
processed_img = contrast_enhancer.enhance(contrast_val)

# Karsastus ja Laiska silmä logiikka
if karsastus or laiska_silma:
    left_eye = processed_img.copy()
    right_eye = processed_img.copy()
    
    if laiska_silma:
        # Laiskan silmän kuva on sumeampi
        right_eye = right_eye.filter(ImageFilter.GaussianBlur(radius=5))
        
    if karsastus:
        # Karsastus siirtää toista kuvaa
        processed_img = Image.blend(left_eye, right_eye.rotate(0, translate=(25, 12)), alpha=0.5)
    else:
        # Jos vain laiska silmä ilman karsastusta (simuloidaan aivojen kokemaa epätarkkuutta)
        processed_img = Image.blend(left_eye, right_eye, alpha=0.5)

# --- NÄYTTÄMINEN ---
col1, col2 = st.columns(2)
with col1:
    st.subheader(f"Lapsen näkö: {ika}")
    st.image(processed_img, use_container_width=True)
    st.info(current['info'])

with col2:
    st.subheader("Vertailu: Aikuinen")
    st.image(img, use_container_width=True)

st.divider()
st.caption("HUOM: Tämä on simulaatio. Jos olet huolissasi lapsen näöstä, ota yhteys neuvolaan.")
