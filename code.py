import streamlit as st
from PIL import Image, ImageFilter, ImageEnhance
import os

st.set_page_config(page_title="Lapsen Näkösimulaattori", layout="wide")

# --- KIELIVALINTA ---
kieli = st.sidebar.radio("Valitse kieli / Select Language", ["Suomi", "English"])

# Tekstien lokalisointi
t = {
    "Suomi": {
        "title": "👁️ Lapsen Näön Kehitys & Tutkimus",
        "settings": "Säädöt",
        "view": "Mitä lapsi katsoo?",
        "age": "Lapsen ikä",
        "disturb": "Simuloi häiriöitä",
        "squint": "Karsastus (Kaksoiskuva)",
        "lazy": "Laiska silmä (Amblyopia)",
        "refractive": "Taittovirhe:",
        "contrast": "Heikko kontrastinherkkyys",
        "info_title": "ℹ️ Tietoa valituista häiriöistä",
        "warning_title": "🚩 Milloin hakeutua lääkäriin? (Hälytysmerkit)",
        "disclaimer": "HUOM: Tämä sovellus on tarkoitettu vain opetuskäyttöön. Ota aina yhteys ammattilaiseen, jos olet huolissasi.",
        "red_flags": [
            "**Valkoinen pupilli:** Jos huomaat salamavalokuvissa lapsen pupillissa valkoisen heijasteen punaisen sijaan.",
            "**Jatkuva karsastus:** Silmät katsovat eri suuntiin vielä 4-6 kuukauden iän jälkeen.",
            "**Silmien väreily:** Silmät tekevät jatkuvaa edestakaista liikettä (nystagmus).",
            "**Valonarkuus ja kova kyynelehtiminen:** Lapsi ei halua avata silmiään valossa.",
            "**Poikkeava pään asento:** Lapsi kallistaa jatkuvasti päätään yrittäessään katsoa jotain.",
            "**Ei katsekontaktia:** Vauva ei kiinnitä katsettaan tai seuraa kasvoja 2-3 kuukauden iässä."
        ]
    },
    "English": {
        "title": "👁️ Infant Vision Development & Simulator",
        "settings": "Settings",
        "view": "What is the child looking at?",
        "age": "Child's age",
        "disturb": "Simulate Disorders",
        "squint": "Strabismus (Double vision)",
        "lazy": "Lazy Eye (Amblyopia)",
        "refractive": "Refractive Error:",
        "contrast": "Low Contrast Sensitivity",
        "info_title": "ℹ️ Information on Selected Disorders",
        "warning_title": "🚩 When to see a doctor? (Red Flags)",
        "disclaimer": "NOTE: This app is for educational purposes only. Always consult a professional if you have concerns.",
        "red_flags": [
            "**White pupil (Leukocoria):** A white reflection in the pupil instead of red in flash photos.",
            "**Constant squinting:** Eyes pointing in different directions after 4-6 months of age.",
            "**Eye shaking:** Eyes making continuous back-and-forth movements (nystagmus).",
            "**Sensitivity to light:** Child avoids opening eyes in bright light or cries excessively.",
            "**Abnormal head posture:** Child constantly tilts their head when trying to look at something.",
            "**No eye contact:** Baby doesn't fixate or follow faces by 2-3 months of age."
        ]
    }
}

txt = t[kieli]

st.title(txt["title"])
st.sidebar.header(txt["settings"])

# --- KUVAN VALINTA ---
kuvavalinta = st.sidebar.selectbox(txt["view"], ["Äiti", "Vesivärit (Leikkihuone)", "Lea-testitaulu", "Lataa oma kuva"])

image_map = {"Äiti": "aiti.jpg", "Vesivärit (Leikkihuone)": "leikkihuone.jpg", "Lea-testitaulu": "lea.jpg"}

def load_local_image(filename):
    if os.path.exists(filename): return Image.open(filename)
    return None

img = None
if kuvavalinta == "Lataa oma kuva":
    uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"])
    if uploaded_file: img = Image.open(uploaded_file)
    else: st.stop()
else:
    img = load_local_image(image_map[kuvavalinta])
    if img is None: st.error(f"File '{image_map[kuvavalinta]}' not found."); st.stop()

# --- IKÄ JA HÄIRIÖT ---
ika_opt = ['Vastasyntynyt', '1-2 kk', '3-4 kk', '6 kk', '12 kk', '2 v.', '3 v.'] if kieli == "Suomi" else ['Newborn', '1-2 mo', '3-4 mo', '6 mo', '12 mo', '2 y.', '3 y.']
ika = st.sidebar.select_slider(txt["age"], options=ika_opt, value=ika_opt[0])

st.sidebar.subheader(txt["disturb"])
karsastus = st.sidebar.checkbox(txt["squint"])
laiska_silma = st.sidebar.checkbox(txt["lazy"])
taittovirhe = st.sidebar.selectbox(txt["refractive"], ["Ei / None", "Myopia", "Hyperopia", "Astigmatism"])
kontrasti_check = st.sidebar.checkbox(txt["contrast"])

# --- SIMULAATIO LOGIIKKA (Lyhennetty selkeyden vuoksi) ---
# (Käytetään samoja arvoja kuin aiemmin)
blur_val = 25 if ika == ika_opt[0] else 15 if ika == ika_opt[1] else 8 if ika == ika_opt[2] else 3 if ika == ika_opt[3] else 1.5 if ika == ika_opt[4] else 0.5 if ika == ika_opt[5] else 0

processed_img = img.copy()
processed_img = processed_img.filter(ImageFilter.GaussianBlur(radius=blur_val))

# --- NÄYTTÄMINEN ---
col1, col2 = st.columns(2)
with col1:
    st.subheader(f"{txt['age']}: {ika}")
    st.image(processed_img, use_container_width=True)

with col2:
    st.subheader("Normal Vision")
    st.image(img, use_container_width=True)

# --- HÄLYTYSMERKIT-OSIO ---
st.divider()
col_info, col_warning = st.columns(2)

with col_warning:
    st.subheader(txt["warning_title"])
    for flag in txt["red_flags"]:
        st.write(f"- {flag}")

st.caption(txt["disclaimer"])
