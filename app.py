import streamlit as st
import pandas as pd
from openai import OpenAI
import io
import time

st.set_page_config(page_title="Ultimate AI Cleaner", layout="wide")

def clean_data_with_ai(dirty_text, client):
    if not dirty_text or pd.isna(dirty_text) or str(dirty_text).strip() == "":
        return dirty_text
    
    # Εξελιγμένο prompt για Ονόματα, Emails και Τηλέφωνα
    prompt = (
        f"Είσαι ειδικός στην εκκαθάριση δεδομένων. Διορθώσε την τιμή: '{dirty_text}'.\n\n"
        f"ΚΑΝΟΝΕΣ:\n"
        f"1. ΑΝ ΕΙΝΑΙ ΟΝΟΜΑ: Βάλε τόνους, κάνε Proper Case και διόρθωσε ορθογραφία.\n"
        f"2. ΑΝ ΕΙΝΑΙ EMAIL: Μετάτρεψε σε μικρά, αφαίρεσε κενά και τελείες στο τέλος.\n"
        f"3. ΑΝ ΕΙΝΑΙ ΤΗΛΕΦΩΝΟ: Κράτα μόνο τα 10 ψηφία (αφαίρεσε +30, παύλες, κενά).\n"
        f"Απάντησε ΜΟΝΟ με τη διορθωμένη τιμή."
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Sidebar 
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if not api_key and "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]

st.title("🚀 Ultimate AI Data Cleaner")
uploaded_file = st.file_uploader("Ανέβασε το Stress Test αρχείο", type=["xlsx", "csv"])

if uploaded_file and api_key:
    client = OpenAI(api_key=api_key)
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    
    st.write("### Δεδομένα προς Επεξεργασία")
    st.dataframe(df.head())
    
    column_to_clean = st.selectbox("Επίλεξε στήλη (Όνομα, Email ή Τηλέφωνο)", df.columns)
    
    if st.button("🚀 Έναρξη Καθαρισμού"):
        with st.spinner("Το AI επεξεργάζεται τα δεδομένα..."):
            cleaned_values = []
            for val in df[column_to_clean]:
                cleaned_values.append(clean_data_with_ai(val, client))
                time.sleep(1) # Αποφυγή Rate Limit
            
            df[f"{column_to_clean}_Cleaned"] = cleaned_values
            st.success("Ολοκληρώθηκε!")
            st.dataframe(df)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Κατέβασμα", data=output.getvalue(), file_name="cleaned_data.xlsx")









