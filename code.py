import streamlit as st
from PIL import Image, ImageFilter, ImageOps, ImageEnhance

st.set_page_config(page_title="Lasten Näkösimulaattori", layout="wide")

st.title("👁️ Lasten Näön Kehitys & Tutkimus")
st.sidebar.header("Säädöt")

# 1. Iän valinta
ika = st.sidebar.select_slider(
    'Lapsen ikä',
    options=['Vastasyntynyt', '1 kk', '2 kk', '3 kk', '6 kk', '12 kk', '24 kk', '3 v.'],
    value='Vastasyntynyt'
)

# 2. Lisäasetukset (Häiriöt)
st.sidebar.subheader("Simuloi häiriöitä")
karsastus = st.sidebar.checkbox("Karsastus (Kaksoiskuva)")
heikko_kontrasti = st.sidebar.checkbox("Heikko kontrastinherkkyys")

# Kuvan lataus
uploaded_file = st.file_uploader("Lataa kuva testattavaksi", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    
    # --- LOGIIKKA IKÄKAUSILLE ---
    # Määritellään sumennus ja värikylläisyys iän mukaan
    settings = {
        'Vastasyntynyt': {'blur': 25, 'sat': 0.0, 'info': "Näkee vain valoa ja varjoja, mustavalkoinen maailma."},
        '1 kk': {'blur': 15, 'sat': 0.1, 'info': "Alkaa erottaa punaisen värin, katse ei vielä kohdistu tarkasti."},
        '2 kk': {'blur': 10, 'sat': 0.3, 'info': "Värit alkavat vahvistua. Katse alkaa seurata liikettä."},
        '3 kk': {'blur': 7, 'sat': 0.6, 'info': "Erottaa kasvot jo selkeämmin. Syvyysnäkö alkaa kehittyä."},
        '6 kk': {'blur': 4, 'sat': 1.0, 'info': "Käsien ja silmien yhteistyö paranee huimasti."},
        '12 kk': {'blur': 2, 'sat': 1.0, 'info': "Näkö on jo melko tarkka, mutta kaukokohteet voivat olla vielä epäselviä."},
        '24 kk': {'blur': 1, 'sat': 1.0, 'info': "Erottaa pieniä yksityiskohtia kuvakirjoista."},
        '3 v.': {'blur': 0, 'sat': 1.0, 'info': "Näöntarkkuus on lähellä aikuisen tasoa."}
    }

    current = settings[ika]
    
    # --- KUVAN KÄSITTELY ---
    # 1. Sumennus
    processed_img = img.filter(ImageFilter.GaussianBlur(radius=current['blur']))
    
    # 2. Värikylläisyys
    converter = ImageEnhance.Color(processed_img)
    processed_img = converter.enhance(current['sat'])
    
    # 3. Kontrasti
    if heikko_kontrasti:
        contrast = ImageEnhance.Contrast(processed_img)
        processed_img = contrast.enhance(0.3)

    # 4. Karsastus (tehdään kaksoiskuva luomalla kaksi läpinäkyvää tasoa)
    if karsastus:
        # Yksinkertaistettu kaksoiskuva: siirretään kuvaa hieman sivulle
        img2 = processed_img.copy()
        processed_img = Image.blend(processed_img, img2.rotate(0, translate=(15, 5)), alpha=0.5)

    # --- NÄYTTÄMINEN ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"Lapsen näkö: {ika}")
        st.image(processed_img, use_container_width=True)
        st.info(current['info'])

    with col2:
        st.subheader("Vertailu: Aikuinen")
        st.image(img, use_container_width=True)

    # --- TIETOPANKKI (Leatest-tyylinen) ---
    st.divider()
    st.subheader(f"Mitä tarkkailla {ika} iässä?")
    
    if ika in ['Vastasyntynyt', '1 kk']:
        st.write("- **Heijasteet:** Tarkista pupillien punavaste kuvatessa salamalla.")
        st.write("- **Kontakti:** Saako lapsi lyhyen katsekontaktin läheltä?")
    elif ika == '3 kk':
        st.write("- **Seuraaminen:** Seuraavatko silmät lelua tasaisesti laidasta laitaan?")
        st.write("- **Silmien asento:** Jatkuva karsastus tässä iässä on syy hakeutua tutkimuksiin.")
    # Tästä voi jatkaa listaa kaikille ikäkausille...

else:
    st.info("Lataa kuva (esim. olohuone tai leluja) nähdäksesi simulaation.")
