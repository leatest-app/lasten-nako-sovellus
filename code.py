import streamlit as st
from PIL import Image, ImageFilter, ImageEnhance
import os

st.set_page_config(page_title="Lapsen Näkösimulaattori", layout="wide")

# --- KIELIVALINTA ---
kieli = st.sidebar.radio("Valitse kieli / Välj språk / Select Language", ["Suomi", "Svenska", "English"])

# --- LOKALISOINTI (Kaikki kolme kieltä) ---
t = {
    "Suomi": {
        "title": "👁️ Lapsen Näön Kehitys & Tutkimus",
        "settings": "Säädöt",
        "view": "Mitä lapsi katsoo?",
        "view_opts": ["Äiti", "Vesivärit (Leikkihuone)", "Lea-testitaulu", "Lataa oma kuva"],
        "age": "Lapsen ikä",
        "disturb": "Simuloi häiriöitä",
        "squint": "Karsastus (Kaksoiskuva)",
        "lazy": "Laiska silmä (Amblyopia)",
        "refractive": "Taittovirhe:",
        "refractive_opts": ["Ei taittovirhettä", "Myopia (Likitaitteisuus)", "Hyperopia (Kaukotaitteisuus)", "Astigmatismi (Hajanaitteisuus)"],
        "contrast": "Heikko kontrastinherkkyys",
        "info_title": "ℹ️ Tietoa valituista häiriöistä",
        "warning_title": "🚩 Hälytysmerkit – Milloin lääkäriin?",
        "disclaimer": "HUOM: Tämä sovellus on tarkoitettu vain opetuskäyttöön. Ota aina yhteys ammattilaiseen, jos olet huolissasi.",
        "ages": ['Vastasyntynyt', '1-2 kk', '3-4 kk', '6 kk', '12 kk', '2 v.', '3 v.'],
        "age_data": {
            'Vastasyntynyt': {'info': "Näkee parhaiten n. 20-30 cm päähän. Suosii mustavalkoisia kuvioita."},
            '1-2 kk': {'info': "Värien erottelu alkaa punaisesta. Katse alkaa seurata kohdetta hitaasti."},
            '3-4 kk': {'info': "Erottaa kasvot ja ilmeet jo selvästi. Syvyysnäkö alkaa kehittyä."},
            '6 kk': {'info': "Näkö on jo melko tarkka. Karsastuksen tulisi tässä iässä yleensä loppua."},
            '12 kk': {'info': "Lapsi erottaa pienet murut lattialta. Näkee tarkasti kauemmaskin."},
            '2 v.': {'info': "Näkökyky on lähellä aikuista. Lapsi osaa etsiä kuvista pieniä kohteita."},
            '3 v.': {'info': "Näkö on kehittynyt. Tässä iässä voidaan tehdä viralliset Lea-testit."}
        },
        "red_flags": ["Valkoinen pupilli", "Jatkuva karsastus 6kk jälkeen", "Silmien väreily", "Ei katsekontaktia 3kk iässä"],
        "exp_squint": "Karsastuksessa aivot saavat kaksi eri kuvaa, mikä voi häiritä syvyysnäköä.",
        "exp_lazy": "Laiskassa silmässä aivot suosivat toista silmää, jolloin toisen näkö jää sumeaksi."
    },
    "Svenska": {
        "title": "👁️ Barnets synutveckling & Simulator",
        "settings": "Inställningar",
        "view": "Vad tittar barnet på?",
        "view_opts": ["Mamma", "Vattenfärger (Lekrum)", "Lea-tavla", "Ladda upp bild"],
        "age": "Barnets ålder",
        "disturb": "Simulera störningar",
        "squint": "Skelning (Dubbelseende)",
        "lazy": "Amblyopi (Synnedsättning)",
        "refractive": "Refraktionsfel:",
        "refractive_opts": ["Inget fel", "Myopi (Närsynthet)", "Hyperopi (Översynthet)", "Astigmatism"],
        "contrast": "Nedsatt kontrastkänslighet",
        "info_title": "ℹ️ Information om valda störningar",
        "warning_title": "🚩 Varningssignaler – När ska man söka vård?",
        "disclaimer": "OBS: Denna app är endast för utbildningsändamål. Kontakta alltid en professionell vid oro.",
        "ages": ['Nyfödd', '1-2 mån', '3-4 mån', '6 mån', '12 mån', '2 år', '3 år'],
        "age_data": {
            'Nyfödd': {'info': "Ser bäst på ca 20-30 cm avstånd. Föredrar svartvita mönster."},
            '1-2 mån': {'info': "Färgseendet börjar med rött. Blicket börjar följa föremål långsamt."},
            '3-4 mån': {'info': "Ser ansikten och uttryck tydligt. Djupseendet börjar utvecklas."},
            '6 mån': {'info': "Synen är redan ganska skarp. Skelning bör normalt upphöra vid denna ålder."},
            '12 mån': {'info': "Barnet ser små smulor på golvet. Ser tydligt även på avstånd."},
            '2 år': {'info': "Synen är nära en vuxens nivå. Kan hitta små föremål i böcker."},
            '3 år': {'info': "Synen är utvecklad. Nu kan man göra officiella Lea-tester."},
        },
        "red_flags": ["Vit pupill", "Konstant skelning efter 6 mån", "Dallrande ögonrörelser", "Ingen ögonkontakt vid 3 mån"],
        "exp_squint": "Vid skelning får hjärnan två olika bilder, vilket kan störa djupseendet.",
        "exp_lazy": "Vid amblyopi favoriserar hjärnan det ena ögat, vilket gör det andra ögat suddigt."
    },
    "English": {
        "title": "👁️ Infant Vision Development & Simulator",
        "settings": "Settings",
        "view": "What is the child looking at?",
        "view_opts": ["Mother", "Watercolors (Playroom)", "Lea Chart", "Upload image"],
        "age": "Child's age",
        "disturb": "Simulate Disorders",
        "squint": "Strabismus (Double vision)",
        "lazy": "Lazy Eye (Amblyopia)",
        "refractive": "Refractive Error:",
        "refractive_opts": ["No error", "Myopia (Nearsighted)", "Hyperopia (Farsighted)", "Astigmatism"],
        "contrast": "Low Contrast Sensitivity",
        "info_title": "ℹ️ Information on Selected Disorders",
        "warning_title": "🚩 Red Flags – When to see a doctor",
        "disclaimer": "NOTE: This app is for educational purposes only. Always consult a professional.",
        "ages": ['Newborn', '1-2 mo', '3-4 mo', '6 mo', '12 mo', '2 y.', '3 y.'],
        "age_data": {
            'Newborn': {'info': "Sees best at 20-30 cm distance. Prefers high contrast patterns."},
            '1-2 mo': {'info': "Starts to distinguish red. Begins to follow moving objects slowly."},
            '3-4 mo': {'info': "Recognizes faces and expressions. Depth perception starts to develop."},
            '6 mo': {'info': "Vision is quite sharp. Strabismus should usually stop by this age."},
            '12 mo': {'info': "Can spot tiny crumbs on the floor. Sees clearly at a distance."},
            '2 y.': {'info': "Vision is close to an adult's. Can spot small items in books."},
            '3 y.': {'info': "Vision is developed. Reliable Lea tests can be done now."}
        },
        "red_flags": ["White pupil", "Constant squint after 6 months", "Eye shaking", "No eye contact by 3 months"],
        "exp_squint": "In strabismus, the brain receives two different images, which can hinder depth perception.",
        "exp_lazy": "In a lazy eye (amblyopia), the brain favors one eye, leaving the other's vision blurry."
    }
}

txt = t[kieli]
st.title(txt["title"])
st.sidebar.header(txt["settings"])

# --- KUVAN LATAUS ---
valittu_näkymä = st.sidebar.selectbox(txt["view"], txt["view_opts"])
img = None

def load_img(fname):
    if os.path.exists(fname): return Image.open(fname)
    return None

if valittu_näkymä == txt["view_opts"][3]: 
    up = st.file_uploader("Upload", type=["jpg","png","jpeg"])
    if up: img = Image.open(up)
    else: st.info("Lataa kuva / Ladda upp bild / Upload image"); st.stop()
else:
    # Käytetään samoja tiedostoja kielestä riippumatta
    map_idx = txt["view_opts"].index(valittu_näkymä)
    f_list = ["aiti.jpg", "leikkihuone.jpg", "lea.jpg"]
    img = load_img(f_list[map_idx])
    if img is None: st.error("Image file missing from GitHub."); st.stop()

# --- INPUTIT ---
ika_valittu = st.sidebar.select_slider(txt["age"], options=txt["ages"], value=txt["ages"][0])
# Haetaan index jotta saadaan oikeat arvot perusasetuksista (Suomi-avaimilla)
avain_index = txt["ages"].index(ika_valittu)
suomi_avain = t["Suomi"]["ages"][avain_index]
base_settings = {
    'Vastasyntynyt': {'blur': 25, 'sat': 0.0, 'contrast': 0.2},
    '1-2 kk': {'blur': 15, 'sat': 0.3, 'contrast': 0.4},
    '3-4 kk': {'blur': 8, 'sat': 0.7, 'contrast': 0.7},
    '6 kk': {'blur': 3, 'sat': 1.0, 'contrast': 0.9},
    '12 kk': {'blur': 1.5, 'sat': 1.0, 'contrast': 1.0},
    '2 v.': {'blur': 0.5, 'sat': 1.0, 'contrast': 1.0},
    '3 v.': {'blur': 0, 'sat': 1.0, 'contrast': 1.0}
}
current_vals = base_settings[suomi_avain]

st.sidebar.subheader(txt["disturb"])
is_squint = st.sidebar.checkbox(txt["squint"])
is_lazy = st.sidebar.checkbox(txt["lazy"])
refr = st.sidebar.selectbox(txt["refractive"], txt["refractive_opts"])
is_contrast = st.sidebar.checkbox(txt["contrast"])

# --- PROSESSOINTI ---
proc = img.copy()
proc = proc.filter(ImageFilter.GaussianBlur(radius=current_vals['blur']))
proc = ImageEnhance.Color(proc).enhance(current_vals['sat'])
proc = ImageEnhance.Contrast(proc).enhance(0.2 if is_contrast else current_vals['contrast'])

if "Myopia" in refr or "Närsynthet" in refr: proc = proc.filter(ImageFilter.GaussianBlur(radius=4))
elif "Hyperopia" in refr or "Översynthet" in refr: proc = proc.filter(ImageFilter.GaussianBlur(radius=3))
elif "Astigmatism" in refr:
    ast_img = proc.filter(ImageFilter.GaussianBlur(radius=2))
    proc = Image.blend(proc, ast_img.rotate(0, translate=(0, 8)), alpha=0.5)

if is_squint or is_lazy:
    r_eye = proc.copy()
    if is_lazy: r_eye = r_eye.filter(ImageFilter.GaussianBlur(radius=6))
    if is_squint: proc = Image.blend(proc, r_eye.rotate(0, translate=(25, 12)), alpha=0.5)
    else: proc = Image.blend(proc, r_eye, alpha=0.5)

# --- NÄYTTÄMINEN ---
c1, c2 = st.columns(2)
with c1:
    st.subheader(f"{txt['age']}: {ika_valittu}")
    st.image(proc, use_container_width=True)
    st.info(txt["age_data"][ika_valittu]["info"])

with c2:
    st.subheader("Normal Vision")
    st.image(img, use_container_width=True)

st.divider()
inf, warn = st.columns(2)
with inf:
    st.subheader(txt["info_title"])
    if is_squint: st.write(f"**{txt['squint']}**: {txt['exp_squint']}")
    if is_lazy: st.write(f"**{txt['lazy']}**: {txt['exp_lazy']}")

with warn:
    st.subheader(txt["warning_title"])
    for f in txt["red_flags"]: st.write(f"- {f}")

st.caption(txt["disclaimer"])
