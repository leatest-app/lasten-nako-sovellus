import streamlit as st
from PIL import Image, ImageFilter, ImageEnhance
import os

st.set_page_config(page_title="Lapsen Näkösimulaattori", layout="wide")

st.title("👁️ Lapsen Näön Kehitys (0–3 v.)")
st.sidebar.header("Säädöt")

# --- KUVAN VALINTA ---
st.sidebar.subheader("Valitse näkymä")
kuvavalinta = st.sidebar.selectbox(
    "Valitse kuva simulaatioon:",
    ["Lea-testitaulu", "Lataa oma kuva"]
)

# Funktio kuvan lataamiseen paikallisesti
def load_local_image(filename):
    if os.path.exists(filename):
        return Image.open(filename)
    else:
        return None

# Ladataan kuva
img = None

if kuvavalinta == "Lataa oma kuva":
    uploaded_file = st.file_uploader("Lataa JPG tai PNG kuva", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        img = Image.open(uploaded_file)
    else:
        st.info("Lataa kuva yläpuolelta kokeillaksesi simulaattoria omalla kuvallasi.")
        st.stop()
else:
    # Yritetään ladata GitHubiin lataamasi lea.jpg
    img = load_local_image("lea.jpg")
    if img is None:
        st.error("Tiedostoa 'lea.jpg' ei löytynyt GitHubista. Lataa se sinne, niin simulaattori toimii!")
        st.stop()

# --- IKÄ JA SIMULAATIO ---
ika = st.sidebar.select_slider(
    'Lapsen ikä',
    options=['Vastasyntynyt', '1-2 kk', '3-4 kk', '6 kk', '12 kk', '2 v.', '3 v.'],
    value='Vastasyntynyt'
)

# Häiriöt
st.sidebar.subheader("Simuloi häiriöitä")
karsastus = st.sidebar.checkbox("Karsastus (Kaksoiskuva)")
kontrasti_check = st.sidebar.checkbox("Heikko kontrastinherkkyys")

# --- DATA ---
settings = {
    'Vastasyntynyt': {'blur': 25, 'sat': 0.0, 'contrast': 0.2, 'info': "Näkee parhaiten n. 20-30 cm päähän. Suosii voimakkaita kontrasteja ja mustavalkoisia kuvioita."},
    '1-2 kk': {'blur': 15, 'sat': 0.3, 'contrast': 0.4, 'info': "Alkaa erottaa punaisen ja vihreän. Katse alkaa seurata hitaasti liikkuvaa kohdetta."},
    '3-4 kk': {'blur': 8, 'sat': 0.7, 'contrast': 0.7, 'info': "Erottaa värejä jo hyvin. Kädet alkavat kurotella kohteita. Karsastuksen pitäisi vähentyä."},
    '6 kk': {'blur': 3, 'sat': 1.0, 'contrast': 0.9, 'info': "Näöntarkkuus kehittyy nopeasti. Syvyysnäkö ja silmien yhteispeli vahvistuvat."},
    '12 kk': {'blur': 1.5, 'sat': 1.0, 'contrast': 1.0, 'info': "Erottaa jo pieniä muruja lattialta. Arvioi etäisyyksiä melko tarkasti."},
    '2 v.': {'blur': 0.5, 'sat': 1.0, 'contrast': 1.0, 'info': "Erottaa pieniä kuvia kirjoista. Syvyysnäkö on jo pitkälle kehittynyt."},
    '3 v.': {'blur': 0, 'sat': 1.0, 'contrast': 1.0, 'info': "Näöntarkkuus on lähellä aikuista. Voidaan testata Lea-symboleilla."}
}

current = settings[ika]
processed_img = img.copy()

# 1. Sumennus
if current['blur'] > 0:
    processed_img = processed_img.filter(ImageFilter.GaussianBlur(radius=current['blur']))

# 2. Värikylläisyys
color_enhancer = ImageEnhance.Color(processed_img)
processed_img = color_enhancer.enhance(current['sat'])

# 3. Kontrasti
contrast_val = 0.2 if kontrasti_check else current['contrast']
contrast_enhancer = ImageEnhance.Contrast(processed_img)
processed_img = contrast_enhancer.enhance(contrast_val)

# 4. Karsastus
if karsastus:
    img_copy = processed_img.copy()
    processed_img = Image.blend(processed_img, img_copy.rotate(0, translate=(20, 10)), alpha=0.5)

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
st.caption("HUOM: Tämä on vain simulaatio. Jos olet huolissasi lapsen näöstä, ota yhteys ammattilaiseen.")
