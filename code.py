import streamlit as st
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import os

st.set_page_config(page_title="Lapsen Näkösimulaattori", layout="wide")

st.title("👁️ Lapsen Näön Kehitys & Taittovirheet")
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
    uploaded_file = st.file_uploader("Lataa kuva", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        img = Image.open(uploaded_file)
    else:
        st.info("Lataa kuva nähdäksesi simulaation.")
        st.stop()
else:
    img = load_local_image(image_map[kuvavalinta])
    if img is None:
        st.error(f"Tiedostoa '{image_map[kuvavalinta]}' ei löytynyt GitHubista.")
        st.stop()

# --- IKÄ ---
ika = st.sidebar.select_slider(
    'Lapsen ikä',
    options=['Vastasyntynyt', '1-2 kk', '3-4 kk', '6 kk', '12 kk', '2 v.', '3 v.'],
    value='Vastasyntynyt'
)

# --- NÄKÖHÄIRIÖT ---
st.sidebar.subheader("Häiriöt ja Taittovirheet")
karsastus = st.sidebar.checkbox("Karsastus (Kaksoiskuva)")
laiska_silma = st.sidebar.checkbox("Laiska silmä (Amblyopia)")
taittovirhe = st.sidebar.selectbox("Simuloi taittovirhettä:", ["Ei taittovirhettä", "Myopia (Likitaitteisuus)", "Hyperopia (Kaukotaitteisuus)", "Astigmatismi (Hajanaitteisuus)"])
kontrasti_check = st.sidebar.checkbox("Heikko kontrastinherkkyys")

# --- DATA ---
settings = {
    'Vastasyntynyt': {'blur': 25, 'sat': 0.0, 'contrast': 0.2, 'info': "Näkee vain valoa ja varjoja, hahmottaa kasvot läheltä."},
    '1-2 kk': {'blur': 15, 'sat': 0.3, 'contrast': 0.4, 'info': "Alkaa seurata liikettä, värit alkavat erottua."},
    '3-4 kk': {'blur': 8, 'sat': 0.7, 'contrast': 0.7, 'info': "Erottaa ilmeet ja kurottelee leluja. Silmien yhteistyö paranee."},
    '6 kk': {'blur': 3, 'sat': 1.0, 'contrast': 0.9, 'info': "Näkö tarkentuu huomattavasti, syvyysnäkö kehittyy."},
    '12 kk': {'blur': 1.5, 'sat': 1.0, 'contrast': 1.0, 'info': "Havaitsee pienet yksityiskohdat, kuten murut lattialta."},
    '2 v.': {'blur': 0.5, 'sat': 1.0, 'contrast': 1.0, 'info': "Näkee lähes yhtä tarkasti kuin aikuinen."},
    '3 v.': {'blur': 0, 'sat': 1.0, 'contrast': 1.0, 'info': "Näkö on valmis viralliseen Lea-testiin."}
}

current = settings[ika]
processed_img = img.copy()

# 1. PERUSKEHITYS (Sumennus, väri, kontrasti)
processed_img = processed_img.filter(ImageFilter.GaussianBlur(radius=current['blur']))
color_enhancer = ImageEnhance.Color(processed_img)
processed_img = color_enhancer.enhance(current['sat'])
contrast_val = 0.2 if kontrasti_check else current['contrast']
processed_img = ImageEnhance.Contrast(processed_img).enhance(contrast_val)

# 2. TAITTOVIRHEIDEN LISÄYS
if taittovirhe == "Myopia (Likitaitteisuus)":
    # Simuloidaan kauas-epätarkkuutta lisäsumennuksella (jos kyseessä esim. äiti kauempana)
    processed_img = processed_img.filter(ImageFilter.GaussianBlur(radius=4))
elif taittovirhe == "Hyperopia (Kaukotaitteisuus)":
    # Simuloidaan akkommodaatiovaikeutta pehmeällä sumennuksella
    processed_img = processed_img.filter(ImageFilter.GaussianBlur(radius=3))
elif taittovirhe == "Astigmatismi (Hajanaitteisuus)":
    # Simuloidaan hajanaitteisuutta sumentamalla vain yhtä akselia (pysty- tai vaaka)
    astig_img = processed_img.filter(ImageFilter.GaussianBlur(radius=2))
    processed_img = Image.blend(processed_img, astig_img.rotate(0, translate=(0, 8)), alpha=0.5)

# 3. KARSASSTUS JA LAISKA SILMÄ
if karsastus or laiska_silma:
    right_eye = processed_img.copy()
    if laiska_silma:
        right_eye = right_eye.filter(ImageFilter.GaussianBlur(radius=6))
    if karsastus:
        processed_img = Image.blend(processed_img, right_eye.rotate(0, translate=(25, 12)), alpha=0.5)
    else:
        processed_img = Image.blend(processed_img, right_eye, alpha=0.5)

# --- NÄYTTÄMINEN ---
col1, col2 = st.columns(2)
with col1:
    st.subheader(f"Lapsen näkö: {ika}")
    st.image(processed_img, use_container_width=True)
    st.info(current['info'])
    if taittovirhe != "Ei taittovirhettä":
        st.warning(f"Simuloidaan taittovirhettä: {taittovirhe}")

with col2:
    st.subheader("Vertailu: Aikuinen")
    st.image(img, use_container_width=True)

st.divider()
st.caption("HUOM: Tämä on vain simulaatio. Käänny aina asiantuntijan puoleen näköasioissa.")
