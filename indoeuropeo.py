#indoeuropeo.py
import streamlit as st
import os, json


DATA_DIR = "data_IE"
os.makedirs(DATA_DIR, exist_ok=True)
ROMANCE_FILE = os.path.join(DATA_DIR, "romance_to_latin.json")
GREEK_FILE = os.path.join(DATA_DIR, "greek_to_latin.json")
GERMANIC_FILE = os.path.join(DATA_DIR, "germanic_to_latin.json")
LATIN_PIE_FILE = os.path.join(DATA_DIR, "latin_to_pie.json")


def load_dict(file_path, default):
    if os.path.exists(file_path):
        with open(file_path,"r",encoding="utf-8") as f:
            return json.load(f)
    return default

def save_dict(file_path, data):
    with open(file_path,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

# -----------------------
# DIZIONARI BASE
# -----------------------
BASE_ROMANCE = {
    "italian": {"padre":"pater","madre":"mater","amore":"amor"},
    "spanish": {"padre":"pater","madre":"mater","amor":"amor"}
}
BASE_GREEK = {"πατήρ":"pater","μήτηρ":"mater","φῶς":"lux"}
BASE_GERMANIC = {"fadar":"pater","modar":"mater","liuhs":"lux"}
BASE_LATIN_PIE = {"pater":"*pəter","mater":"*mātēr","amor":"*h₂méh₁r","lux":"*lewkʷ-"}

ROMANCE = load_dict(ROMANCE_FILE, BASE_ROMANCE)
GREEK = load_dict(GREEK_FILE, BASE_GREEK)
GERMANIC = load_dict(GERMANIC_FILE, BASE_GERMANIC)
LATIN_PIE = load_dict(LATIN_PIE_FILE, BASE_LATIN_PIE)


# REGOLE GLOTTOLOGICHE- base per permettere al programma di capirci.

GREEK_PIE_RULES = {
    "π":"p","β":"b","φ":"pʰ","τ":"t","δ":"d","θ":"tʰ",
    "κ":"k","γ":"g","χ":"kʰ","σ":"s","ζ":"dz",
    "η":"ē","α":"a","ε":"e","ο":"o","ι":"i","υ":"u",
    "ει":"ei","αι":"ai","οι":"oi","ου":"u","ω":"ō"
}
#LEGGI TRASCRIZIONE GLOTTOLOGICA
GERMANIC_PIE_RULES = {
    "f":"p","þ":"t","h":"k","d":"t","g":"k","b":"p","w":"u̯",
    "ai":"oi","ei":"ei","au":"aw"
}

ABLAUT = {"e":"*e","o":"*o","0":"∅"}

# -----------------------
# FUNZIONI DI UTILITÀ
# -----------------------
def normalize(word):
    return word.strip().lower()

def apply_rules(word,rules):
    w = word
    for pat,rep in rules.items():
        w = w.replace(pat,rep)
    return w

# -----------------------
# TRADUZIONI PIE
# -----------------------
def latin_to_pie(word):
    w = normalize(word)
    return LATIN_PIE.get(w,f"*{w}-?")

def greek_to_pie(word):
    return "*"+apply_rules(word,GREEK_PIE_RULES)

def germanic_to_pie(word):
    return "*"+apply_rules(word,GERMANIC_PIE_RULES)

# -----------------------
# TRADUZIONI INTERATTIVE
# -----------------------
def romance_to_latin(word,lang):
    w = normalize(word)
    if w in ROMANCE.get(lang,{}):
        return ROMANCE[lang][w]
    latin = st.text_input(f"Inserisci forma latina per '{word}' ({lang})")
    if latin:
        ROMANCE[lang][w] = latin
        save_dict(ROMANCE_FILE,ROMANCE)
        return latin
    return None

def greek_to_latin_safe(word):
    if word in GREEK:
        return GREEK[word]
    latin = st.text_input(f"Inserisci forma latina per '{word}' (greco)")
    if latin:
        GREEK[word] = latin
        save_dict(GREEK_FILE,GREEK)
        return latin
    return None

def germanic_to_latin_safe(word):
    if word in GERMANIC:
        return GERMANIC[word]
    latin = st.text_input(f"Inserisci forma latina per '{word}' (germanico)")
    if latin:
        GERMANIC[word] = latin
        save_dict(GERMANIC_FILE,GERMANIC)
        return latin
    return None

# -----------------------
# FUNZIONE PRINCIPALE
# -----------------------
def translate(word,lang):
    lang = lang.lower()
    latin,pie = None,None
    stepwise = {}
    if lang in ("italian","spanish"):
        latin = romance_to_latin(word,lang)
        if latin:
            pie = latin_to_pie(latin)
            stepwise["Latino->PIE"]=pie
    elif lang=="latin":
        latin = word
        pie = latin_to_pie(word)
        stepwise["Latino->PIE"]=pie
    elif lang=="greek":
        latin = greek_to_latin_safe(word)
        pie = greek_to_pie(word)
        stepwise["Greco->PIE"]=pie
    elif lang=="germanic":
        latin = germanic_to_latin_safe(word)
        pie = germanic_to_pie(word)
        stepwise["Germanico->PIE"]=pie
    return latin,pie,stepwise

# -----------------------
# STREAMLIT INTERFACE
# -----------------------
st.title("🌿 Ricostruzione Indoeuropea ")

word = st.text_input("Inserisci parola")
lang = st.selectbox("Seleziona lingua", ["italian","spanish","latin","greek","germanic"])

if word:
    latin,pie,steps = translate(word,lang)
    if latin and pie:
        st.subheader("Risultati principali")
        st.write(f"**Latino o equivalente:** {latin}")
        st.write(f"**PIE ricostruito:** {pie}")

        st.subheader("Per una spiegazione più dettagliata")
        for k,v in steps.items():
            st.write(f"{k}: {v}")

        st.subheader("Confronto tra rami")
        st.table({
            "Ramo":["Romance/Latino","Greco","Germanico"],
            "Forma Latina/Equivalente":[latin,GREEK.get(word,"-"),GERMANIC.get(word,"-")],
            "PIE":[latin_to_pie(latin),greek_to_pie(GREEK.get(word,"-")),germanic_to_pie(GERMANIC.get(word,"-"))]
        })

