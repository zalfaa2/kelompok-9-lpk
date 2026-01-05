import streamlit as st
import re
import pandas as pd

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Kalkulator ChemWeight",
    page_icon="🧪",
    layout="wide"
)

# ==================================================
# DATABASE Ar (praktikum-friendly, bisa ditambah)
# ==================================================
AR = {
    "H": 1.0, "He": 4.0,
    "Li": 6.9, "Be": 9.0, "B": 10.8, "C": 12.0, "N": 14.0, "O": 16.0,
    "F": 19.0, "Ne": 20.2,
    "Na": 23.0, "Mg": 24.3, "Al": 27.0, "Si": 28.1, "P": 31.0, "S": 32.1,
    "Cl": 35.5, "Ar": 39.9,
    "K": 39.1, "Ca": 40.1,
    "Fe": 55.8, "Cu": 63.5, "Zn": 65.4,
    "Br": 79.9, "Ag": 107.9, "I": 126.9, "Ba": 137.3, "Pb": 207.2
}

# ==================================================
# PARSER RUMUS (KURUNG & HIDRAT)
# Mendukung: Ca(OH)2, CuSO4·5H2O, CuSO4.5H2O
# ==================================================
def parse_formula(formula: str) -> dict:
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
            # angka setelah unsur: misal H2 -> token '2'
            prev = list(stack[-1].keys())[-1]
            stack[-1][prev] += int(token) - 1

        else:
            # unsur
            stack[-1][token] = stack[-1].get(token, 0) + 1

        i += 1

    return stack[0]


def hitung_mr(rumus: str):
    # split hidrat pakai titik biasa atau titik tengah
    parts = re.split(r"[·\.]", rumus.replace(" ", ""))

    total = {}
    for part in parts:
        if not part:
            continue

        # dukung koefisien depan hidrat: 5H2O
        m = re.match(r"^(\d+)(.*)$", part)
        if m:
            koef = int(m.group(1))
            core = m.group(2)
        else:
            koef = 1
            core = part

        parsed = parse_formula(core)
        for el, cnt in parsed.items():
            total[el] = total.get(el, 0) + cnt * koef

    mr = 0.0
    detail = []
    for el, cnt in total.items():
        if el not in AR:
            return None, f"Unsur '{el}' tidak ada di database Ar.", None
        kontribusi = AR[el] * cnt
        mr += kontribusi
        detail.append({"Unsur": el, "Jumlah": cnt, "Ar": AR[el], "Kontribusi": kontribusi})

    return mr, None, detail


# ==================================================
# UI - SIDEBAR
# ==================================================
st.sidebar.title("🧪 Kalkulator Timbangan Zat Kimia")
st.sidebar.write(
    "Menghitung **Mr otomatis** dari rumus kimia, lalu menghitung **massa (gram)** "
    "berdasarkan **M, N, ppm, atau % b/v** dengan pilihan volume **mL/L**."
)

st.sidebar.markdown("---")
show_ar = st.sidebar.checkbox("Tampilkan database Ar (ringkas)", value=False)

# ==================================================
# UI - MAIN
# ==================================================
st.title("🧪 Kalkulator Timbangan Zat Kimia (Mr & Massa Otomatis)")
st.write(
    "Masukkan **rumus kimia** + pilih **jenis konsentrasi** dan **volume**, "
    "maka web akan menghitung **Mr** dan **massa zat yang harus ditimbang (gram)**."
)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    rumus = st.text_input("Rumus kimia", placeholder="Contoh: NaCl, Ca(OH)2, CuSO4·5H2O")

    jenis_konsentrasi = st.selectbox(
        "Jenis konsentrasi",
        ["Molaritas (M)", "Normalitas (N)", "ppm", "% b/v"]
    )

    nilai_konsentrasi = st.number_input(
        "Nilai konsentrasi",
        min_value=0.0,
        step=0.01
    )

with col2:
    satuan_volume = st.radio("Satuan volume", ["mL", "L"], horizontal=True)

    volume = st.number_input(
        f"Volume larutan ({satuan_volume})",
        min_value=0.0,
        step=1.0 if satuan_volume == "mL" else 0.01
    )

    # Normalitas: ekuivalen (opsional)
    faktor_ekuivalen_manual = None
    if jenis_konsentrasi == "Normalitas (N)":
        faktor_ekuivalen_manual = st.number_input(
            "Faktor ekuivalen (n) (opsional, default otomatis=jumlah H)",
            min_value=1,
            step=1
        )

st.markdown("---")

# ==================================================
# HITUNG
# ==================================================
if st.button("⚖️ Hitung Massa", use_container_width=True):
    if not rumus or nilai_konsentrasi <= 0 or volume <= 0:
        st.warning("⚠️ Rumus, nilai konsentrasi, dan volume harus diisi (> 0).")
    else:
        mr, err, detail = hitung_mr(rumus)

        if err:
            st.error(err)
        else:
            # konversi volume ke liter bila perlu
            volume_l = volume / 1000 if satuan_volume == "mL" else volume

            # hitung massa sesuai jenis konsentrasi
            if jenis_konsentrasi == "Molaritas (M)":
                massa = nilai_konsentrasi * volume_l * mr
                ekuivalen = "-"

            elif jenis_konsentrasi == "Normalitas (N)":
                # otomatis sederhana: jumlah H pada senyawa (asam) -> ekuivalen
                # jika manual diisi, gunakan manual
                jumlah_H = 1
                for row in detail:
                    if row["Unsur"] == "H":
                        jumlah_H = int(row["Jumlah"])
                        break

                ekuivalen = faktor_ekuivalen_manual if faktor_ekuivalen_manual else jumlah_H
                massa = nilai_konsentrasi * volume_l * (mr / ekuivalen)

            elif jenis_konsentrasi == "ppm":
                # asumsi larutan encer: 1 ppm ≈ 1 mg/L
                massa = (nilai_konsentrasi * volume_l) / 1000  # mg -> g
                ekuivalen = "-"

            elif jenis_konsentrasi == "% b/v":
                # % b/v = gram per 100 mL
                if satuan_volume == "L":
                    volume_ml = volume * 1000
                else:
                    volume_ml = volume
                massa = (nilai_konsentrasi * volume_ml) / 100
                ekuivalen = "-"

            # ==================================================
            # OUTPUT
            # ==================================================
            st.success("✅ Perhitungan berhasil")

            st.subheader("🔬 Detail Perhitungan Mr")
            df_detail = pd.DataFrame(detail)
            df_detail["Kontribusi"] = df_detail["Kontribusi"].map(lambda x: f"{x:.2f}")
            st.dataframe(df_detail, use_container_width=True)

            st.write(f"### **Mr {rumus} = {mr:.2f} g/mol**")

            st.subheader("📊 Ringkasan")
            df_ringkas = pd.DataFrame({
                "Parameter": [
                    "Rumus kimia",
                    "Jenis konsentrasi",
                    "Nilai konsentrasi",
                    "Volume",
                    "Faktor ekuivalen",
                    "Mr (g/mol)",
                    "Massa ditimbang (g)"
                ],
                "Nilai": [
                    rumus,
                    jenis_konsentrasi,
                    nilai_konsentrasi,
                    f"{volume} {satuan_volume}",
                    ekuivalen,
                    f"{mr:.2f}",
                    f"{massa:.4f}"
                ]
            })
            st.table(df_ringkas)

            st.subheader("⚖️ Massa yang harus ditimbang")
            st.markdown(f"## **{massa:.4f} gram**")

# ==================================================
# OPTIONAL: tampilkan AR ringkas
# ==================================================
if show_ar:
    st.markdown("---")
    st.subheader("📚 Database Ar (ringkas)")
    st.dataframe(pd.DataFrame({"Unsur": list(AR.keys()), "Ar": list(AR.values())}),
                 use_container_width=True)

st.caption("Web Praktikum Kimia – Mr otomatis (kurung & hidrat) | M, N, ppm, % b/v | mL/L")
