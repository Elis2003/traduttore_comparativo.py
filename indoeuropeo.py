#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IE Translator - Versione comparativa definitiva
Autore: [Il tuo nome]
Descrizione:
Sistema glottologico autonomo che traduce tra lingue romanze, greco e germanico
e ricostruisce la forma protoindoeuropea (PIE) usando metodo comparativo.
"""

import os
import json
import re
import pandas as pd
import streamlit as st
from collections import Counter

# ----------------------------
# CARTELLA DATI
# ----------------------------
DATA_DIR = "ie_data_autonomous"
os.makedirs(DATA_DIR, exist_ok=True)

ROMANCE_FILE = os.path.join(DATA_DIR, "romance_to_latin.json")
GREEK_FILE = os.path.join(DATA_DIR, "greek_to_latin.json")
LATIN_PIE_FILE = os.path.join(DATA_DIR, "latin_to_pie.json")
GERMANIC_GROUP_FILE = os.path.join(DATA_DIR, "germanic_group_to_latin.json")

# ----------------------------
# DIZIONARI DI BASE
# ----------------------------

ROMANCE = {
    "italian": {
        "padre":"pater","madre":"mater","fratello":"frater","sorella":"soror",
        "fuoco":"focus","tempo":"tempus","luce":"lux","cuore":"cor","mano":"manus",
        "occhio":"oculus","notte":"nox","acqua":"aqua","vino":"vinum","pane":"panis",
        "casa":"casa","mare":"mare","libro":"liber","amore":"amor"
    },
    "spanish": {
        "padre":"pater","madre":"mater","hermano":"frater","hermana":"soror",
        "fuego":"focus","tiempo":"tempus","luz":"lux","corazon":"cor","mano":"manus",
        "ojo":"oculus","noche":"nox","agua":"aqua","vino":"vinum","pan":"panis",
        "casa":"casa","mar":"mare","libro":"liber","amor":"amor"
    }
}

GREEK = {
    "πατήρ":"pater","μήτηρ":"mater","φῶς":"lux","ἀστήρ":"stella","θάλασσα":"mare"
}

GERMANIC_GROUP = {
    "old_english": {
        "fæder": "pater","mōdor": "mater","brōþor": "frater","swustor": "soror",
        "fyr": "focus","tīd": "tempus","léoht": "lux","heorte": "cor",
        "hand": "manus","ēage": "oculus","niht": "nox","wæter": "aqua",
        "win": "vinum","hlāf": "panis","hūs": "casa","sæ": "mare",
        "bōc": "liber","lufu": "amor"
    },
    "modern_german": {
        "vater": "pater","mutter": "mater","bruder": "frater","schwester": "soror",
        "feuer": "focus","zeit": "tempus","licht": "lux","herz": "cor",
        "hand": "manus","auge": "oculus","nacht": "nox","wasser": "aqua",
        "wein": "vinum","brot": "panis","haus": "casa","meer": "mare",
        "buch": "liber","liebe": "amor"
    }
}

LATIN_PIE = {
    "pater":"*ph₂tḗr","mater":"*méh₂tēr","frater":"*bʰréh₂tēr","soror":"*swésōr",
    "focus":"*péh₂ḱus","lux":"*lewkʷ-","aqua":"*h₂ekʷā","cor":"*ḱḗr","nox":"*nókʷts",
    "manus":"*mānus","oculus":"*h₃ekʷlos","stella":"*h₂stḗr","terra":"*térh₂",
    "amor":"*h₂m̥h₁r","mare":"*móri-","panis":"*paHnis","liber":"*h₁leubh-"
}

# ----------------------------
# FUNZIONI DI SUPPORTO
# ----------------------------
def norm(s): return s.strip().lower()

def load_dict(path, default):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return default

def save_dict(path, data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

ROMANCE = load_dict(ROMANCE_FILE, ROMANCE)
GREEK = load_dict(GREEK_FILE, GREEK)
LATIN_PIE = load_dict(LATIN_PIE_FILE, LATIN_PIE)
GERMANIC_GROUP = load_dict(GERMANIC_GROUP_FILE, GERMANIC_GROUP)

# ----------------------------
# REGOLE FONETICHE
# ----------------------------
LATIN_RULES = [
    ("qu","kʷ"),("ph","pʰ"),("th","tʰ"),("ch","kʰ"),("v","w"),
    ("c","k"),("g","g"),("j","y"),("b","b"),("p","p"),("t","t"),("d","d"),("f","f"),
    ("ae","e"),("oe","e"),("au","aw"),("e","e"),("a","a"),("o","o"),("i","i"),("u","u")
]

GREEK_TABLE = [
    ("αι","ai"),("ει","ei"),("οι","oi"),("ου","u"),
    ("π","p"),("β","b"),("φ","pʰ"),("τ","t"),("δ","d"),("θ","tʰ"),
    ("κ","k"),("γ","g"),("χ","kʰ"),("σ","s"),("ζ","dz"),
    ("η","ē"),("α","a"),("ε","e"),("ο","o"),("ι","i"),("υ","u"),("ω","ō")
]

GERMANIC_RULES = [
    ("f","p"),("þ","t"),("θ","t"),("h","k"),("d","t"),("b","p"),("g","k"),("w","u̯"),
    ("ai","oi"),("ei","ei"),("au","aw")
]

ROMANCE_RULES = {
    "italian":[("zione","tio"),("ch","c"),("gl","li"),("gn","gn"),("e$","us"),("o$","us"),("a$","a")],
    "spanish":[("ción","tio"),("h",""),("ll","l"),("ñ","n"),("j","i"),("e$","us"),("o$","us"),("a$","a")]
}

# ----------------------------
# FUNZIONI DI TRADUZIONE
# ----------------------------
def latin_to_pie(word):
    w = norm(word)
    steps = [f"Latino di partenza: {w}"]
    if w in LATIN_PIE:
        steps.append(f"Trovato nel dizionario: {LATIN_PIE[w]}")
        return LATIN_PIE[w], steps
    for a,b in LATIN_RULES:
        if a in w:
            w = w.replace(a,b)
            steps.append(f"/{a}/ → {b} → {w}")
    if not w.startswith("*"):
        w = "*" + w
    steps.append(f"Ricostruzione PIE: {w}")
    return w, steps

def greek_to_pie(word):
    w = word
    steps = [f"Input greco: {w}"]
    for a,b in GREEK_TABLE:
        if a in w:
            w = w.replace(a,b)
            steps.append(f"{a} → {b} → {w}")
    w = "*" + w
    return w, steps

def germanic_to_pie(word):
    w = norm(word)
    steps = [f"Input germanico: {w}"]
    for a,b in GERMANIC_RULES:
        if a in w:
            w = w.replace(a,b)
            steps.append(f"/{a}/ → {b} → {w}")
    w = "*" + w
    steps.append(f"Ricostruzione PIE: {w}")
    return w, steps

def romance_to_latin(word, lang):
    w = norm(word)
    steps = [f"Input {lang}: {w}"]
    if w in ROMANCE.get(lang, {}):
        lat = ROMANCE[lang][w]
        steps.append(f"Trovato nel dizionario: {lat}")
        return lat, steps
    for a,b in ROMANCE_RULES[lang]:
        if re.search(a, w):
            w = re.sub(a,b,w)
            steps.append(f"/{a}/ → {b} → {w}")
    if not re.search(r"(us|um|a|is|es|o)$", w):
        w += "-"
        steps.append(f"Aggiunto suffisso latino: {w}")
    return w, steps
# ----------------------------
# FUNZIONE ABLAUT PIE
# ----------------------------
def ablaut_variants(root):
    """
    Genera le varianti e/o/Ø della radice indoeuropea.
    Es: *bher- → *bher-, *bhor-, *bhr̥-
    """
    if not root.startswith("*"):
        root = "*" + root
    variants = [root]
    if "e" in root:
        variants.append(root.replace("e", "o"))
        variants.append(root.replace("e", "o"))
    elif "o" in root:
        variants.append(root.replace("o", "e"))
        variants.append(root.replace("o", ""))
    else:
        variants.append(root + " (no vocalic alternation)")
    return variants
# ----------------------------
# RICOSTRUZIONE COMPARATIVA
# ----------------------------
def most_common_root(forms):
    if not forms: return None
    return Counter(forms).most_common(1)[0][0]

def comparative_reconstruction(word):
    results = []
    pie_forms = []

    # --- Italiano ---
    lat_it, _ = romance_to_latin(word, "italian")
    pie_it, _ = latin_to_pie(lat_it)
    results.append(("italian", word, pie_it))
    pie_forms.append(pie_it)

    # --- Spagnolo ---
    form_es = next((es for es, la in ROMANCE["spanish"].items() if la == lat_it), None)
    if form_es:
        lat_es = ROMANCE["spanish"][form_es]
        pie_es, _ = latin_to_pie(lat_es)
        results.append(("spanish", form_es, pie_es))
        pie_forms.append(pie_es)
    else:
        results.append(("spanish", "—", None))

    # --- Latino ---
    pie_lat, _ = latin_to_pie(lat_it)
    results.append(("latin", lat_it, pie_lat))
    pie_forms.append(pie_lat)

    # --- Greco ---
    form_gr = next((gr for gr, la in GREEK.items() if la == lat_it), None)
    if form_gr:
        pie_gr, _ = greek_to_pie(form_gr)
        results.append(("greek", form_gr, pie_gr))
        pie_forms.append(pie_gr)
    else:
        results.append(("greek", "—", None))

    # --- Germanico (old_english + modern_german) ---
    for branch, data in GERMANIC_GROUP.items():
        form_ge = next((ge for ge, la in data.items() if la == lat_it), None)
        if form_ge:
            pie_ge, _ = germanic_to_pie(form_ge)
            results.append((branch, form_ge, pie_ge))
            pie_forms.append(pie_ge)
        else:
            results.append((branch, "—", None))

    best = most_common_root([p for p in pie_forms if p])
    return results, best

# ----------------------------
# STREAMLIT APP
# ----------------------------
st.set_page_config(page_title="Traduttore Glottologico Comparativo", page_icon="🌿", layout="wide")
st.title("🌿 Traduttore Glottologico Comparativo")
st.write("Sistema autonomo basato su regole glottologiche (Grimm, Verner, Ablaut, confronto interlinguistico).")

word = st.text_input("Inserisci una parola:")
lang = st.selectbox("Lingua di partenza", ["italian","spanish","latin","greek","old_english","modern_german"])
compare = st.checkbox("Esegui ricostruzione comparativa automatica", value=False)

if word:
    st.markdown("---")

    if lang == "italian":
        lat, s1 = romance_to_latin(word, "italian")
        pie, s2 = latin_to_pie(lat)
    elif lang == "spanish":
        lat, s1 = romance_to_latin(word, "spanish")
        pie, s2 = latin_to_pie(lat)
    elif lang == "latin":
        pie, s1 = latin_to_pie(word)
        s2 = []
        lat = word
    elif lang == "greek":
        pie, s1 = greek_to_pie(word)
        s2 = []
        lat = GREEK.get(word, "—")
    elif lang in GERMANIC_GROUP:
        data = GERMANIC_GROUP[lang]
        lat = data.get(word, "—")
        pie, s1 = germanic_to_pie(word)
        s2 = []
    else:
        pie, s1, s2, lat = "—", [], [], "—"

    st.subheader("Risultato singolo:")
    st.write(f"Latino: {lat}")
    st.write(f"PIE ricostruito: {pie}")
    st.subheader("Passaggi:")
    for s in s1+s2: st.write("-", s)

if word:
    st.markdown("---")
    results, best = comparative_reconstruction(word)
    df = pd.DataFrame(results, columns=["Lingua","Forma","PIE derivato"])
    st.table(df)

    if best:
        st.success(f"**Ricostruzione PIE media suggerita:** {best}")

        variants = ablaut_variants(best)
        st.markdown("### 📜 Varianti Ablaut PIE (e/o/Ø):")
        for v in variants:
            st.write("-", v)
st.markdown("---")
st.caption("Progetto universitario — Traduttore comparativo basato su regole linguistiche storiche.")
# ----------------------------
# FUNZIONI PER INTERFACCIA UTENTE
# ----------------------------
def get_master_vocabulary():
    """Raccoglie e ordina tutte le parole di input dai dizionari."""
    vocab = set()
    # Aggiungi parole dalle lingue romanze
    for lang_dict in ROMANCE.values():
        vocab.update(lang_dict.keys())
    # Aggiungi parole dal greco
    vocab.update(GREEK.keys())
    # Aggiungi parole dalle lingue germaniche
    for lang_dict in GERMANIC_GROUP.values():
        vocab.update(lang_dict.keys())
        
    # La prima opzione deve essere vuota per la selezione
    sorted_vocab = sorted(list(vocab))
    sorted_vocab.insert(0, "— Seleziona una parola —")
    return sorted_vocab
