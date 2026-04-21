import streamlit as st
from PIL import Image, ImageFilter, ImageEnhance
import os

st.set_page_config(page_title="Lapsen Näkösimulaattori", layout="wide")

st.title("👁️ Lapsen Näön Kehitys & Tutkimus")
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

# --- IKÄVALINTA ---
ika = st.sidebar.select_slider(
    'Lapsen ikä',
    options=['Vastasyntynyt', '1-2 kk', '3-4 kk', '6 kk', '12 kk', '2 v.', '3 v.'],
    value='Vastasyntynyt'
)

# --- HÄIRIÖIDEN VALINTA ---
st.sidebar.subheader("Simuloi häiriöitä")
karsastus = st.sidebar.checkbox("Karsastus (Kaksoiskuva)")
laiska_silma = st.sidebar.checkbox("Laiska silmä (Amblyopia)")
taittovirhe = st.sidebar.selectbox("Taittovirhe:", ["Ei taittovirhettä", "Myopia (Likitaitteisuus)", "Hyperopia (Kaukotaitteisuus)", "Astigmatismi (Hajanaitteisuus)"])
kontrasti_check = st.sidebar.checkbox("Heikko kontrastinherkkyys")

# --- KEHITYSDATA ---
settings = {
    'Vastasyntynyt': {'blur': 25, 'sat': 0.0, 'contrast': 0.2, 'info': "Näkee parhaiten n. 20-30 cm päähän. Suosii mustavalkoisia kuvioita ja voimakkaita kontrasteja."},
    '1-2 kk': {'blur': 15, 'sat': 0.3, 'contrast': 0.4, 'info': "Värien erottelu alkaa punaisesta. Katse alkaa seurata kohdetta hitaasti."},
    '3-4 kk': {'blur': 8, 'sat': 0.7, 'contrast': 0.7, 'info': "Erottaa kasvot ja ilmeet jo selvästi. Syvyysnäkö ja kurottelu alkavat kehittyä."},
    '6 kk': {'blur': 3, 'sat': 1.0, 'contrast': 0.9, 'info': "Näkö on jo melko tarkka. Karsastuksen tulisi tässä iässä yleensä loppua."},
    '12 kk': {'blur': 1.5, 'sat': 1.0, 'contrast': 1.0, 'info': "Lapsi erottaa pienet murut ja yksityiskohdat. Näkee tarkasti kauemmaskin."},
    '2 v.': {'blur': 0.5, 'sat': 1.0, 'contrast': 1.0, 'info': "Näkökyky on lähellä aikuista. Lapsi osaa jo etsiä kuvista pieniä kohteita."},
    '3 v.': {'blur': 0, 'sat': 1.0, 'contrast': 1.0, 'info': "Näkö on kehittynyt. Tässä iässä voidaan tehdä ensimmäiset luotettavat Lea-testit."}
}

current = settings[ika]
processed_img = img.copy()

# 1. Perusprosessointi (Ikä)
processed_img = processed_img.filter(ImageFilter.GaussianBlur(radius=current['blur']))
processed_img = ImageEnhance.Color(processed_img).enhance(current['sat'])
contrast_val = 0.2 if kontrasti_check else current['contrast']
processed_img = ImageEnhance.Contrast(processed_img).enhance(contrast_val)

# 2. Taittovirheet
if taittovirhe == "Myopia (Likitaitteisuus)":
    processed_img = processed_img.filter(ImageFilter.GaussianBlur(radius=4))
elif taittovirhe == "Hyperopia (Kaukotaitteisuus)":
    processed_img = processed_img.filter(ImageFilter.GaussianBlur(radius=3))
elif taittovirhe == "Astigmatismi (Hajanaitteisuus)":
    astig_img = processed_img.filter(ImageFilter.GaussianBlur(radius=2))
    processed_img = Image.blend(processed_img, astig_img.rotate(0, translate=(0, 8)), alpha=0.5)

# 3. Karsastus ja Laiska silmä
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

with col2:
    st.subheader("Vertailu: Aikuinen / Normaalinäkö")
    st.image(img, use_container_width=True)

# --- INFORMAATIO-OSIO (Aktiiviset häiriöt) ---
st.divider()
if karsastus or laiska_silma or taittovirhe != "Ei taittovirhettä" or kontrasti_check:
    st.subheader("ℹ️ Tietoa valituista häiriöistä")
    
    if karsastus:
        with st.expander("Karsastus (Strabismus)"):
            st.write("Karsastuksessa silmät katsovat eri suuntiin. Tämä voi johtaa siihen, että aivot saavat kaksi eri kuvaa (kaksoiskuvat). Jos karsastusta ei hoideta, aivot saattavat alkaa hylätä toisen silmän kuvaa, mikä johtaa laiskaan silmään.")
            
    if laiska_silma:
        with st.expander("Laiska silmä (Amblyopia)"):
            st.write("Laiska silmä tarkoittaa, että silmän ja aivojen välinen yhteistyö ei ole kehittynyt normaalisti. Toisen silmän näöntarkkuus jää heikommaksi. Hoito (kuten peittohoito) on tehokkainta pienenä, kun näköjärjestelmä on vielä muovautuva.")

    if taittovirhe == "Myopia (Likitaitteisuus)":
        with st.expander("Myopia (Likitaitteisuus)"):
            st.write("Likitaitteinen lapsi näkee lähellä olevat asiat (kuten kirjan tai vesivärit) hyvin, mutta kaukana olevat kohteet (kuten taulun tai äidin huoneen toisella puolella) ovat sumeita. Myopia yleistyy usein vasta kouluiässä.")

    if taittovirhe == "Hyperopia (Kaukotaitteisuus)":
        with st.expander("Hyperopia (Kaukotaitteisuus)"):
            st.write("Lapsilla on luonnostaan pieni määrä kaukotaitteisuutta. Jos sitä on paljon, silmä joutuu tekemään jatkuvasti työtä (akkommodaatio) nähdäkseen tarkasti. Tämä voi aiheuttaa silmien väsymistä, päänsärkyä tai karsastusta.")

    if taittovirhe == "Astigmatismi (Hajanaitteisuus)":
        with st.expander("Astigmatismi (Hajanaitteisuus)"):
            st.write("Hajanaitteisuus johtuu silmän sarveiskalvon epäsäännöllisestä muodosta. Se aiheuttaa epätarkkuutta ja vääristymiä kaikilla etäisyyksillä. Viivat saattavat näyttää venyneiltä tietyssä suunnassa.")

    if kontrasti_check:
        with st.expander("Heikko kontrastinherkkyys"):
            st.write("Kontrastinherkkyys tarkoittaa kykyä erottaa kohde taustastaan, jos ne ovat lähellä toisiaan (esim. vaalea hahmo vaalealla taustalla). Heikko kontrasti tekee maailmasta 'lattean' ja vaikeuttaa muun muassa portaiden ja kasvojen piirteiden havaitsemista.")

st.caption("HUOM: Tämä sovellus on tarkoitettu vain opetuskäyttöön ja havainnollistamiseen. Ota aina yhteys neuvolaan tai silmälääkäriin, jos epäilet lapsen näössä olevan poikkeavuutta.")
