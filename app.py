import streamlit as st
import re

# --------------------------------------------------
# KONFIGURASI HALAMAN
# --------------------------------------------------
st.set_page_config(
    page_title="Kalkulator Timbangan Zat Kimia",
    layout="centered"
)

st.title("🧪 Kalkulator Timbangan Zat Kimia")
st.write(
    "Web ini menghitung **massa atom relatif (Ar)** dan **massa molekul relatif (Mr)** "
    "secara otomatis dari **rumus kimia**, kemudian menentukan "
    "**massa (gram) bahan kimia** yang harus ditimbang "
    "untuk memperoleh **konsentrasi larutan tertentu**."
)

st.divider()

# --------------------------------------------------
# DATABASE Ar – TABEL PERIODIK (LENGKAP & PRAKTIKUM)
# --------------------------------------------------
AR = {
    "H": 1.0, "He": 4.0,
    "Li": 6.9, "Be": 9.0, "B": 10.8, "C": 12.0, "N": 14.0, "O": 16.0,
    "F": 19.0, "Ne": 20.2,
    "Na": 23.0, "Mg": 24.3, "Al": 27.0, "Si": 28.1, "P": 31.0, "S": 32.1,
    "Cl": 35.5, "Ar": 39.9,
    "K": 39.1, "Ca": 40.1, "Sc": 45.0, "Ti": 47.9, "V": 50.9,
    "Cr": 52.0, "Mn": 54.9, "Fe": 55.8, "Co": 58.9, "Ni": 58.7,
    "Cu": 63.5, "Zn": 65.4, "Ga": 69.7, "Ge": 72.6, "As": 74.9,
    "Se": 79.0, "Br": 79.9, "Kr": 83.8,
    "Rb": 85.5, "Sr": 87.6, "Y": 88.9, "Zr": 91.2, "Nb": 92.9,
    "Mo": 95.9, "Tc": 98.0, "Ru": 101.1, "Rh": 102.9, "Pd": 106.4,
    "Ag": 107.9, "Cd": 112.4, "In": 114.8, "Sn": 118.7,
    "Sb": 121.8, "I": 126.9, "Xe": 131.3,
    "Cs": 132.9, "Ba": 137.3, "La": 138.9, "Ce": 140.1,
    "Pr": 140.9, "Nd": 144.2, "Pm": 145.0, "Sm": 150.4,
    "Eu": 152.0, "Gd": 157.3, "Tb": 158.9, "Dy": 162.5,
    "Ho": 164.9, "Er": 167.3, "Tm": 168.9, "Yb": 173.0,
    "Lu": 175.0, "Hf": 178.5, "Ta": 180.9, "W": 183.8,
    "Re": 186.2, "Os": 190.2, "Ir": 192.2, "Pt": 195.1,
    "Au": 197.0, "Hg": 200.6, "Pb": 207.2,
    "Bi": 209.0, "Po": 209.0, "At": 210.0, "Rn": 222.0,
    "Fr": 223.0, "Ra": 226.0, "Ac": 227.0, "Th": 232.0,
    "Pa": 231.0, "U": 238.0, "Np": 237.0, "Pu": 244.0
}

# --------------------------------------------------
# FUNGSI HITUNG Mr (TANPA KURUNG & HIDRAT)
# --------------------------------------------------
def hitung_mr(rumus):
    pola = r'([A-Z][a-z]*)(\d*)'
    hasil = re.findall(pola, rumus)

    mr = 0
    detail = []

    for unsur, jumlah in hasil:
        if unsur not in AR:
            return None, f"Unsur '{unsur}' tidak terdapat dalam database Ar"
        n = int(jumlah) if jumlah else 1
        kontribusi = AR[unsur] * n
        mr += kontribusi
        detail.append(f"{unsur} × {n} = {kontribusi:.2f}")

    return mr, detail


# --------------------------------------------------
# INPUT PENGGUNA
# --------------------------------------------------
rumus = st.text_input("Rumus kimia (contoh: NaCl, H2SO4, NaOH)")
konsentrasi = st.number_input("Konsentrasi larutan (M)", min_value=0.0, step=0.01)
volume_ml = st.number_input("Volume larutan (mL)", min_value=0.0, step=1.0)

# --------------------------------------------------
# PROSES PERHITUNGAN
# --------------------------------------------------
if st.button("Hitung Massa"):
    if rumus == "" or konsentrasi == 0 or volume_ml == 0:
        st.warning("⚠️ Semua data harus diisi dengan benar")
    else:
        mr, info = hitung_mr(rumus)

        if mr is None:
            st.error(info)
        else:
            volume_l = volume_ml / 1000
            mol = konsentrasi * volume_l
            massa = mol * mr

            st.success("✅ Perhitungan Berhasil")

            st.subheader("🔬 Perhitungan Mr")
            for i in info:
                st.write(i)

            st.write(f"**Mr {rumus} = {mr:.2f} g/mol**")
            st.write(f"**Jumlah mol = {mol:.4f} mol**")

            st.subheader("⚖️ Massa yang harus ditimbang")
            st.write(f"### **{massa:.4f} gram**")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()
st.caption("Web Praktikum Kimia – Perhitungan Ar, Mr, dan Bobot Timbangan Otomatis")
