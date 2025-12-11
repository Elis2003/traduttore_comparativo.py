#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IE Translator - Versione Corretta 
"""

import os
import json
import re
import pandas as pd
import streamlit as st
from collections import Counter

# ----------------------------
# DATI E CONFIGURAZIONE
# ----------------------------
DATA_DIR = "ie_data_autonomous"
os.makedirs(DATA_DIR, exist_ok=True)

# --- DIZIONARI DI TRADUZIONE ---
ROMANCE = {
    "italian": {
        "padre": "pater", "madre": "mater", "fratello": "frater", "sorella": "soror",
        "luce": "lux", "notte": "nox", "stella": "stella", "acqua": "aqua", 
        "terra": "terra", "mare": "mare",
        "cuore": "cor", "occhio": "oculus", "mano": "manus",
        "amore": "amor", "pane": "panis", "focolare": "focus", "fuoco": "focus"
    },
    "spanish": {
        "padre": "pater", "madre": "mater", "hermano": "frater", "hermana": "soror",
        "luz": "lux", "noche": "nox", "estrella": "stella", "agua": "aqua", 
        "tierra": "terra", "mar": "mare",
        "corazon": "cor", "ojo": "oculus", "mano": "manus",
        "amor": "amor", "pan": "panis", "fuego": "focus"
    }
}

GREEK = {
    "πατήρ": "pater", "μήτηρ": "mater", "φράτηρ": "frater",
    "λευκός": "lux", "νύξ": "nox", "ἀστήρ": "stella", 
    "τέρσομαι": "terra", "θάλασσα": "mare", 
    "καρδία": "cor", "κῆρ": "cor", "ὄψ": "oculus", "χείρ": "manus", 
    "πατέομαι": "panis"
}

GERMANIC_GROUP = {
    "old_english": {
        "fæder": "pater", "mōdor": "mater", "brōþor": "frater", "swustor": "soror",
        "léoht": "lux", "niht": "nox", "steorra": "stella", "wæter": "aqua",
        "eorþe": "terra", "sæ": "mare",
        "heorte": "cor", "ēage": "oculus", "hand": "manus",
        "lufu": "amor", "hlāf": "panis", "fyr": "focus"
    },
    "modern_german": {
        "vater": "pater", "mutter": "mater", "bruder": "frater", "schwester": "soror",
        "licht": "lux", "nacht": "nox", "stern": "stella", "wasser": "aqua",
        "erde": "terra", "meer": "mare",
        "herz": "cor", "auge": "oculus", "hand": "manus",
        "liebe": "amor", "brot": "panis", "feuer": "focus"
    }
}

LATIN_PIE = {
    "pater": "*ph₂tḗr", "mater": "*méh₂tēr", "frater": "*bʰréh₂tēr", "soror": "*swésōr",
    "lux": "*lewkʷ-", "nox": "*nókʷts", "stella": "*h₂stḗr", "aqua": "*h₂ekʷā",
    "terra": "*térh₂", "mare": "*móri-",
    "cor": "*ḱḗr", "oculus": "*h₃ekʷlos", "manus": "*mānus",
    "amor": "*h₂m̥h₁r", "panis": "*paHnis", "focus": "*péh₂ḱus"
}

# --- SCHEDE POKORNY/STAROSTIN ---
POKORNY_NOTES = {
    "pater": "Radice pǝtḗ(r). Dal PIE ph₂tḗr. La radice indica il capofamiglia e protettore. In latino pater non è solo il genitore biologico, ma l'autorità giuridica e sacrale della casa (paterfamilias). Corrisponde esattamente al greco patḗr e all'inglese father.",
    "mater": "Radice māter-. Dal PIE méh₂tēr. La radice è universale e indica la madre. È interessante notare come nel dizionario questa parola sia collegata anche a māteria (la materia), suggerendo un'idea arcaica della madre come \"origine\", \"tronco\" o \"sostanza\" da cui nasce la vita.",
    "frater": "Radice bhrātēr. Dal PIE bʰréh₂tēr. Nota importante: mentre in latino e nelle lingue germaniche indica il fratello di sangue, in greco phrā́tēr indicava il membro di una \"fratria\" (un clan politico/religioso). Questo suggerisce che in origine la parola indicasse un membro maschio dello stesso gruppo tribale.",
    "soror": "Radice su̯esor-. Dal PIE swésōr. La parola latina soror mostra il rotacismo (la 's' intervocalica diventa 'r'), tipico del latino (da swesor a soror). Potrebbe significare letteralmente \"la donna del proprio gruppo\" (da swe- \"proprio\").",
    "lux": " Radice leuk- / leuĝh-. Dal PIE lewkʷ-. La radice unisce i concetti di \"luce\", \"bianco\" e \"vedere\". È la stessa radice che ha dato origine a luna (l'astro luminoso) e lumen.",
    "nox": "Radice nekʷ-(t-), nokʷ-t-s. Dal PIE nókʷts. È una delle parole indoeuropee più stabili, rimasta quasi identica in tutte le lingue (Latino nox, Tedesco Nacht, Inglese Night, Greco Nyx). Indica il tempo dell'oscurità.",
    "stella": "Radice ster-. Dal PIE h₂stḗr. In latino stella è un diminutivo arcaico (ster-la). L'etimologia ci offre un'immagine poetica: le stelle sono viste come oggetti \"sparsi\" o \"seminati\" nel firmamento.",
    "aqua": "Radice akā-, akʷā-. Dal PIE h₂ekʷā. Indica l'acqua che scorre o l'acqua come elemento naturale. Curiosità dal dizionario: aquila potrebbe derivare da qui, forse per il colore scuro delle piume paragonato all'acqua scura o per il suo habitat.",
    "terra": "Radice ters-. Dal PIE térh₂ (o ters-). Il latino terra significava originariamente \"la secca\", \"l'asciutta\", in contrapposizione al mare. Condivide la radice con \"torrido\" e \"tostare\".",
    "mare": " Radice mori-. Dal PIE móri-. Parola comune alle lingue europee (latino, celtico, germanico, slavo) per indicare il mare.",
    "cor": "Radice k̂erd-. Dal PIE ḱḗr. Sede delle emozioni e dell'intelletto per gli antichi. La 'h' germanica (heart) corrisponde regolarmente alla 'c' latina (cor) secondo la legge di Grimm.",
    "oculus": "Radice okʷ-. Dal PIE h₃ekʷlos. La radice okw- indica la vista. È affascinante notare che feroce (ferox) derivi da qui: significava originariamente \"dall'aspetto selvaggio\", \"che ha uno sguardo fiero\".",
    "manus": "Radice man-. Dal PIE mānus. In latino manus indicava non solo l'arto fisico, ma il \"potere giuridico\" (la manus maritale, o la manomissione degli schiavi). È la mano che afferra e controlla.",
    "amor": "Radice am(m)a. Dal PIE h₂m̥h₁r (o radice infantile amma). Come confermato dal dizionario, amor non nasce come passione romantica astratta, ma dal linguaggio infantile (amma = mamma) per esprimere attaccamento, cura e nutrizione.",
    "panis": "Radice pā-. Dal PIE paHnis. Il pane è, etimologicamente, \"il nutrimento\" per eccellenza. Deriva dalla stessa radice di pascere (portare al pascolo) e pasto.",
    "focus": "Radice bheg- / bhā-. Dal PIE péh₂ḱus (o bho-k-). Originariamente il focus non era il \"fuoco\" in sé (che era ignis), ma il \"focolare domestico\", il punto centrale della casa dove si cucinava e ci si riuniva."
}

# ----------------------------
#  LOGICA E FUNZIONI
# ----------------------------
def norm(s): return s.strip().lower()

LATIN_RULES = [("qu","kʷ"),("c","k"),("ae","ai"),("oe","oi")]
GREEK_TABLE = [("αι","ai"),("ει","ei"),("οι","oi"),("ου","u"),("φ","ph"),("θ","th"),("χ","kh")]
GERMANIC_RULES = [("f","p"),("þ","t"),("h","k"),("d","t"),("w","u̯")]
ROMANCE_RULES = {
    "italian":[("zione","tio"),("ch","c"),("gl","li"),("gn","ni")],
    "spanish":[("ción","tio"),("h","f"),("ll","pl")]
}

def latin_to_pie(word):
    w = norm(word)
    steps = []
    if w in LATIN_PIE:
        return LATIN_PIE[w], steps
    for a,b in LATIN_RULES: w = w.replace(a,b)
    if not w.startswith("*"): w = "*" + w
    return w, steps

def greek_to_pie(word):
    w = word
    steps = []
    for a,b in GREEK_TABLE: w = w.replace(a,b)
    return "*" + w, steps

def germanic_to_pie(word):
    w = norm(word)
    steps = []
    for a,b in GERMANIC_RULES: w = w.replace(a,b)
    return "*" + w, steps

def find_latin_key(word, lang):
    """
    Funzione cruciale: Identifica la chiave latina universale (es. 'frater')
    indipendentemente dalla lingua di input (es. 'hermano' o 'fratello').
    """
    w = norm(word)
    key = None
    
    if lang == "latin":
        return w if w in LATIN_PIE else None
        
    if lang == "italian":
        key = ROMANCE["italian"].get(w)
    elif lang == "spanish":
        key = ROMANCE["spanish"].get(w)
    elif lang == "greek":
        key = GREEK.get(w) # Input diretto greco
    elif lang in GERMANIC_GROUP:
        key = GERMANIC_GROUP[lang].get(w)
        
    return key

def reverse_lookup(dictionary, target_value):
    """Trova la parola nella lingua target che corrisponde alla chiave latina, ricorda che è la parte cruciale"""
    for k, v in dictionary.items():
        if v == target_value:
            return k
    return "—"

def build_comparative_table(latin_key):
    """Costruisce la tabella partendo dalla chiave latina sicura"""
    results = []
    
    # PIE base
    pie_root, _ = latin_to_pie(latin_key)
    
    # 1. Italiano
    it_word = reverse_lookup(ROMANCE["italian"], latin_key)
    results.append(("Italiano", it_word, pie_root))
    
    # 2. Spagnolo
    es_word = reverse_lookup(ROMANCE["spanish"], latin_key)
    results.append(("Spagnolo", es_word, pie_root))
    
    # 3. Latino
    results.append(("Latino", latin_key, pie_root))
    
    # 4. Greco
    gr_word = reverse_lookup(GREEK, latin_key)
    if gr_word != "—":
        pie_gr, _ = greek_to_pie(gr_word)
        results.append(("Greco", gr_word, pie_gr))
    else:
        results.append(("Greco", "—", "—"))
        
    # 5. Germanico
    for branch, data in GERMANIC_GROUP.items():
        ge_word = reverse_lookup(data, latin_key)
        if ge_word != "—":
            pie_ge, _ = germanic_to_pie(ge_word)
            results.append((branch, ge_word, pie_ge))
        else:
            results.append((branch, "—", "—"))
            
    return results

# ----------------------------
#  INTERFACCIA COME APPARE IL SITO
# ----------------------------
st.set_page_config(page_title="Traduttore Glottologico Comparativo", page_icon="🌿", layout="wide")
st.title("🌿 Traduttore Glottologico Comparativo")
st.write("Sistema autonomo basato su regole glottologiche e schede Pokorny/Starostin.")

word_input = st.text_input("Inserisci una delle seguenti parole: Padre, Madre, Fratello, Sorella," \
" luce, notte, stella, acqua, terra, mare," \
" cuore, occhio, mano, amore, pane e fuoco ")
lang_input = st.selectbox("Lingua di partenza", ["italian","spanish","latin","greek","old_english","modern_german"])

if word_input:
    st.markdown("---")
    
    # 1. IDENTIFICAZIONE CHIAVE LATINA
    # Questo è il passaggio che mancava prima per lo spagnolo!
    latin_key = find_latin_key(word_input, lang_input)
    
    # Se non trova la chiave nel dizionario, usa l'input come fallback (euristico)
    if not latin_key and lang_input == "latin":
        latin_key = norm(word_input)
    
    # 2. VISUALIZZAZIONE RISULTATO SINGOLO
    if latin_key:
        pie, steps = latin_to_pie(latin_key)
        st.subheader("Risultato Tecnico:")
        st.write(f"Concetto Latino identificato: **{latin_key}**")
        st.write(f"PIE ricostruito: **{pie}**")
    else:
        st.warning("Parola non trovata nei dizionari della tesi. Provo una ricostruzione fonetica generica.")
        # Fallback generico
        latin_key = "—"
        steps = ["Parola non presente nel corpus Pokorny."]

    # 3. TABELLA COMPARATIVA
    if latin_key and latin_key != "—":
        st.markdown("### 🌍 Comparazione Interlinguistica")
        table_data = build_comparative_table(latin_key)
        df = pd.DataFrame(table_data, columns=["Lingua", "Forma", "PIE derivato"])
        st.table(df)

    # 4. RIQUADRO POKORNY (INFO BOX)
    # Ora funziona sicuramente perché si basa su 'latin_key' calcolato all'inizio
    if latin_key and latin_key in POKORNY_NOTES:
        st.markdown("---")
        st.markdown("### 📖 Scheda Etimologica (Fonte: Pokorny/Starostin)")
        st.info(f"**{latin_key.upper()}**: {POKORNY_NOTES[latin_key]}")

st.markdown("---")
st.caption("Progetto universitario — Traduttore glottologico comparativo.")
st.caption("Dati basati su J. Pokorny. Edizione digitale rivista dalla Associazione Dnghu (2007), con contributi di G. Starostin e A. Lubotsky. Licenza CC BY-SA 3.0.")
