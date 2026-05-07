import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from num2words import num2words
import math

st.set_page_config(page_title="Facture", layout="wide")

# --- HEADER ---
st.title("FACTURE")

logo = st.file_uploader("Télécharger le logo de l'entreprise", type=["png","jpg","jpeg"])
if logo:
    st.image(logo, width=120)

facture_num = st.text_input("Numéro de facture", "001/2026")
date_facture = datetime.today().strftime("%d/%m/%Y")
st.write(f"Date: {date_facture}")

# --- INFO SOCIETE ET CLIENT ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Votre société")
    st.text("EURL AK BATICOM")
    st.text("ACTIVITE : ETB - TCE")
    st.text("ADRESSE : cite 1108 logts residence chrea Bt.B4 N°32 Local A - BLIDA")
    st.text("RC: 09/00-0812541B24")
    st.text("NIF: 002409081254142")
    st.text("NIS : 0024 0901 00368 53")
    st.text("BP: 2000251719")

with col2:
    st.subheader("Client")
    client_nom = st.text_input("Nom du client")
    client_capital = st.text_input("Capital social")
    client_adresse = st.text_input("Adresse")
    client_banque = st.text_input("Banque")
    client_rc = st.text_input("N° RC")
    client_nif = st.text_input("N° IF")
    client_nis = st.text_input("N° IS")
    client_bp = st.text_input("BP")

# --- PROJET ---
projet = st.text_input("Nom du projet")

# --- TABLEAU ARTICLES ---
st.subheader("Détails des travaux")

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["CODE","DESIGNATION","U","QTE","PU","MONTANT"])

code = st.text_input("Code")
designation = st.text_input("Désignation")
u = st.text_input("Unité (m², etc.)")
qte = st.number_input("Quantité", min_value=0.0, step=0.01)
pu = st.number_input("Prix unitaire", min_value=0.0, step=0.01)

if st.button("Ajouter ligne"):
    montant = qte * pu
    new_row = {"CODE":code,"DESIGNATION":designation,"U":u,"QTE":qte,"PU":pu,"MONTANT":montant}
    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)

st.dataframe(st.session_state.df)

# --- CALCULS ---
st.subheader("Résumé")

total_ht = st.session_state.df["MONTANT"].sum() if not st.session_state.df.empty else 0
tva_rate = st.number_input("TVA (%)", value=19)
timbre_rate = st.number_input("Timbre (%)", value=2)

tva = total_ht * tva_rate/100
timbre = total_ht * timbre_rate/100
total_ttc = total_ht + tva
net_a_payer = total_ttc + timbre

col1, col2 = st.columns(2)
with col1:
    st.write(f"TOTAL HT: {total_ht:,.2f} DA")
    st.write(f"TVA ({tva_rate}%): {tva:,.2f} DA")
    st.write(f"TIMBRE ({timbre_rate}%): {timbre:,.2f} DA")
    st.write(f"TOTAL TTC: {total_ttc:,.2f} DA")
    st.write(f"NET À PAYER: {net_a_payer:,.2f} DA")

with col2:
    mode = st.radio("Mode de paiement", ["ESPECE","CHEQUE","VERSEMENT BANCAIRE"])
    st.write(f"Mode choisi: {mode}")

# --- MONTANT EN LETTRES ---
st.write("Montant en lettres:")
st.write(num2words(math.floor(net_a_payer), lang="fr"))

# --- GENERER PDF ---
def generate_pdf(df, total_ht, tva, timbre, total_ttc, net_a_payer, mode):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="FACTURE", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Numéro: {facture_num} - Date: {date_facture}", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Projet: {projet}", ln=True, align="L")

    pdf.cell(200, 10, txt="--- Articles ---", ln=True)
    for i, row in df.iterrows():
        pdf.cell(200, 10, txt=f"{row['CODE']} | {row['DESIGNATION']} | {row['QTE']} | {row['PU']} | {row['MONTANT']}", ln=True)

    pdf.cell(200, 10, txt=f"TOTAL HT: {total_ht}", ln=True)
    pdf.cell(200, 10, txt=f"TVA: {tva}", ln=True)
    pdf.cell(200, 10, txt=f"TIMBRE: {timbre}", ln=True)
    pdf.cell(200, 10, txt=f"TOTAL TTC: {total_ttc}", ln=True)
    pdf.cell(200, 10, txt=f"NET À PAYER: {net_a_payer}", ln=True)
    pdf.cell(200, 10, txt=f"Mode de paiement: {mode}", ln=True)

    pdf.output("facture.pdf")

if st.button("Télécharger en PDF"):
    generate_pdf(st.session_state.df, total_ht, tva, timbre, total_ttc, net_a_payer, mode)
    st.success("Facture PDF générée avec succès ! (facture.pdf)")

# --- GENERER EXCEL ---
if st.button("Télécharger en Excel"):
    st.session_state.df.to_excel("facture.xlsx", index=False)
    st.success("Facture Excel générée avec succès ! (facture.xlsx)")
