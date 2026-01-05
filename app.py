import streamlit as st
import re
import pandas as pd

# ==================================================
# KONFIGURASI HALAMAN
# ==================================================
st.set_page_config(
    page_title="Chemical Weighing Calculator",
    page_icon="🧪",
    layout="wide"
)

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.title("🧪 Chemical Weighing Calculator")
st.sidebar.write(
    "Web praktikum profesional untuk menghitung "
    "**Mr otomatis** dan **massa zat (gram)** "
    "berdasarkan berbagai **jenis konsentrasi**."
)
st.sidebar.markdown("---")

# ==================================================
# DATABASE Ar (PRAKTIKUM-FRIENDLY)
# ==================================================
AR = {
    "H": 1.0, "C": 12.0, "N": 14.0, "O": 16.0,
    "Na": 23.0, "Mg": 24.3, "Al": 27.0, "Si": 28.1,
    "P": 31.0, "S": 32.1, "Cl": 35.5, "K": 39.1,
    "Ca": 40.1, "Fe": 55.8, "Cu": 63.5, "Zn": 65.4,
    "Ag": 107.9, "Ba": 137.3
}

# ==================================================
# PARSER RUMUS KIMIA (KURUNG + HIDRAT)
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


def hitung_mr_lengkap(rumus):
    parts = re.split(r'[·\.]', rumus)
    total = {}
    detail = []

    for part in parts:
        parsed = parse_formula(part)
        for el, cnt in parsed.items():
            total[el] = total.get(el, 0) + cnt

    mr = 0
    for el, cnt in total.items():
        if el not in AR:
            return None, f"Unsur '{el}' tidak ada di database"
        kontribusi = AR[el] * cnt
        mr += kontribusi
        detail.append(f"{el} × {cnt} = {kontribusi:.2f}")

    return mr, detail, total


# ==================================================
# VALIDASI FAKTOR EKUIVALEN (ASAM–BASA)
# ==================================================
def auto_equivalent_factor(komposisi):
    if "H" in komposisi:
        return komposisi["H"]  # asam
    if "OH" in komposisi:
        return komposisi["OH"]  # basa
    return 1


# ==================================================
# UI UTAMA
# ==================================================
st.title("🧪 Chemical Weighing Calculator")
st.write(
    "Aplikasi ini menghitung **Mr secara otomatis dari rumus kimia (kurung & hidrat)**, "
    "lalu menentukan **massa zat (gram)** yang harus ditimbang "
    "berdasarkan **M, N, ppm, atau % b/v**."
)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    rumus = st.text_input("Rumus kimia", placeholder="Contoh: Ca(OH)2, CuSO4·5H2O")
    jenis = st.selectbox("Jenis konsentrasi", ["Molaritas (M)", "Normalitas (N)", "ppm", "% b/v"])
    nilai = st.number_input("Nilai konsentrasi", min_value=0.0)

with col2:
    satuan_volume = st.radio("Satuan volume", ["mL", "L"])
    volume = st.number_input("Volume larutan", min_value=0.0)

    faktor_manual = None
    if jenis == "Normalitas (N)":
        faktor_manual = st.number_input(
            "Faktor ekuivalen (opsional, otomatis jika dikosongkan)",
            min_value=1,
            step=1
        )

# ==================================================
# HITUNG
# ==================================================
if st.button("⚖️ Hitung Massa", use_container_width=True):
    if rumus == "" or nilai == 0 or volume == 0:
        st.warning("⚠️ Semua data harus diisi")
    else:
        mr, detail, komposisi = hitung_mr_lengkap(rumus)

        if mr is None:
            st.error(detail)
        else:
            volume_l = volume / 1000 if satuan_volume == "mL" else volume

            if jenis == "Molaritas (M)":
                massa = nilai * volume_l * mr
                ekuivalen = "-"

            elif jenis == "Normalitas (N)":
                ekuivalen = faktor_manual if faktor_manual else auto_equivalent_factor(komposisi)
                massa = nilai * volume_l * (mr / ekuivalen)

            elif jenis == "ppm":
                massa = (nilai * volume_l) / 1000
                ekuivalen = "-"

            elif jenis == "% b/v":
                massa = (nilai * volume) / 100
                ekuivalen = "-"

            # ==================================================
            # TABEL RINGKASAN
            # ==================================================
            data = {
                "Parameter": [
                    "Rumus kimia",
                    "Mr (g/mol)",
                    "Jenis konsentrasi",
                    "Nilai konsentrasi",
                    "Volume",
                    "Faktor ekuivalen",
                    "Massa ditimbang (g)"
                ],
                "Nilai": [
                    rumus,
                    f"{mr:.2f}",
                    jenis,
                    nilai,
                    f"{volume} {satuan_volume}",
                    ekuivalen,
                    f"{massa:.4f}"
                ]
            }

            df = pd.DataFrame(data)

            st.success("✅ Perhitungan Berhasil")

            st.subheader("🔬 Detail Perhitungan Mr")
            for d in detail:
                st.write(d)

            st.subheader("📊 Ringkasan Perhitungan")
            st.table(df)

            st.subheader("⚖️ Massa yang Harus Ditimbang")
            st.markdown(f"## **{massa:.4f} gram**")

st.markdown("---")
st.caption("Professional Chemical Web App – Ar, Mr, Kurung, Hidrat, M/N/ppm/% b/v")

