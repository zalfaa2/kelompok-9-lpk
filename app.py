import streamlit as st
import re
import pandas as pd

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Chemical Weighing Calculator",
    page_icon="🧪",
    layout="wide"
)

# ==================================================
# DATABASE Ar
# ==================================================
AR = {
    "H": 1.0, "C": 12.0, "N": 14.0, "O": 16.0,
    "Na": 23.0, "Mg": 24.3, "Al": 27.0, "Si": 28.1,
    "P": 31.0, "S": 32.1, "Cl": 35.5, "K": 39.1,
    "Ca": 40.1, "Fe": 55.8, "Cu": 63.5, "Zn": 65.4,
    "Ag": 107.9, "Ba": 137.3
}

# ==================================================
# PARSER RUMUS (KURUNG & HIDRAT)
# ==================================================
def parse_formula(formula):
    tokens = re.findall(r'([A-Z][a-z]?|\(|\)|\d+)', formula)
    stack = [{}]
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if token == "(":
            stack.append({})
        elif token == ")":
            group = stack.pop()
            multiplier = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                multiplier = int(tokens[i + 1])
                i += 1
            for el, cnt in group.items():
                stack[-1][el] = stack[-1].get(el, 0) + cnt * multiplier
        elif token.isdigit():
            prev = list(stack[-1].keys())[-1]
            stack[-1][prev] += int(token) - 1
        else:
            stack[-1][token] = stack[-1].get(token, 0) + 1
        i += 1

    return stack[0]


def hitung_mr(rumus):
    parts = re.split(r'[·\.]', rumus)
    total = {}

    for part in parts:
        parsed = parse_formula(part)
        for el, cnt in parsed.items():
            total[el] = total.get(el, 0) + cnt

    mr = 0
    detail = []

    for el, cnt in total.items():
        if el not in AR:
            return None, f"Unsur '{el}' tidak ada dalam database"
        kontribusi = AR[el] * cnt
        mr += kontribusi
        detail.append(f"{el} × {cnt} = {kontribusi:.2f}")

    return mr, detail, total

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.title("🧪 Chemical Weighing Calculator")
st.sidebar.write(
    "Menghitung **Mr otomatis** dan **massa zat (gram)** "
    "berdasarkan **M, N, ppm, atau % b/v**."
)

# ==================================================
# INPUT
# ==================================================
col1, col2 = st.columns(2)

with col1:
    rumus = st.text_input("Rumus kimia", placeholder="Contoh: NaCl, Ca(OH)2, CuSO4·5H2O")
    jenis = st.selectbox("Jenis konsentrasi", ["Molaritas (M)", "Normalitas (N)", "ppm", "% b/v"])
    nilai = st.number_input("Nilai konsentrasi", min_value=0.0)

with col2:
    satuan = st.radio("Satuan volume", ["mL", "L"])
    volume = st.number_input("Volume larutan", min_value=0.0)

# ==================================================
# SESSION STATE
# ==================================================
if "hasil" not in st.session_state:
    st.session_state.hasil = None

# ==================================================
# HITUNG OTOMATIS
# ==================================================
def hitung_otomatis():
    mr, detail, komposisi = hitung_mr(rumus)
    if mr is None:
        st.session_state.hasil = ("error", detail)
        return

    volume_l = volume / 1000 if satuan == "mL" else volume

    if jenis == "Molaritas (M)":
        massa = nilai * volume_l * mr
        ekuivalen = "-"

    elif jenis == "Normalitas (N)":
        ekuivalen = komposisi.get("H", 1)
        massa = nilai * volume_l * (mr / ekuivalen)

    elif jenis == "ppm":
        massa = (nilai * volume_l) / 1000
        ekuivalen = "-"

    elif jenis == "% b/v":
        massa = (nilai * volume) / 100
        ekuivalen = "-"

    st.session_state.hasil = {
        "mr": mr,
        "massa": massa,
        "detail": detail,
        "ekuivalen": ekuivalen
    }

if rumus and nilai > 0 and volume > 0:
    hitung_otomatis()

# ==================================================
# OUTPUT
# ==================================================
st.markdown("---")

if st.session_state.hasil:
    if isinstance(st.session_state.hasil, tuple):
        st.error(st.session_state.hasil[1])
    else:
        hasil = st.session_state.hasil

        st.success("✅ Hasil ter-update otomatis")

        st.subheader("🔬 Perhitungan Mr")
        for d in hasil["detail"]:
            st.write(d)
        st.write(f"**Mr = {hasil['mr']:.2f} g/mol**")

        df = pd.DataFrame({
            "Parameter": [
                "Rumus kimia",
                "Jenis konsentrasi",
                "Nilai konsentrasi",
                "Volume",
                "Faktor ekuivalen",
                "Massa (g)"
            ],
            "Nilai": [
                rumus,
                jenis,
                nilai,
                f"{volume} {satuan}",
                hasil["ekuivalen"],
                f"{hasil['massa']:.4f}"
            ]
        })

        st.subheader("📊 Ringkasan Perhitungan")
        st.table(df)

        st.subheader("⚖️ Massa yang Harus Ditimbang")
        st.markdown(f"## **{hasil['massa']:.4f} gram**")

# ==================================================
# FOOTER
# ==================================================
st.caption("Web Praktikum Kimia – Ar & Mr Otomatis | M, N, ppm, % b/v")

