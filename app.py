import streamlit as st
import pandas as pd
from openai import OpenAI
import io
import time

# Ρύθμιση σελίδας
st.set_page_config(page_title="AI Data Cleaner", layout="wide")

def clean_data_with_ai(dirty_text, client):
    if not dirty_text or pd.isna(dirty_text) or str(dirty_text).strip() == "":
        return dirty_text
    
    prompt = (
        f"Είσαι ένας ειδικός στην εκκαθάριση δεδομένων. Διορθώσε την τιμή: '{dirty_text}'.\n\n"
        f"ΚΑΝΟΝΕΣ ΑΝΑΛΟΓΑ ΜΕ ΤΟ ΠΕΡΙΕΧΟΜΕΝΟ:\n"
        f"1. ΑΝ ΕΙΝΑΙ ΟΝΟΜΑ: Διόρθωσε ορθογραφία, βάλε τόνους και κάνε το Proper Case (π.χ. παπαδοπουλος -> Παπαδόπουλος).\n"
        f"2. ΑΝ ΕΙΝΑΙ EMAIL: Μετάτρεψε όλα τα γράμματα σε μικρά και αφαίρεσε τυχόν κενά.\n"
        f"3. ΑΝ ΕΙΝΑΙ ΤΗΛΕΦΩΝΟ: Κράτα μόνο τους αριθμούς. Αν ξεκινάει από 69 ή 2, βεβαιώσου ότι έχει 10 ψηφία.\n"
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

# Sidebar για το API Key
st.sidebar.title("Ρυθμίσεις")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

if not api_key and "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]

st.title("🚀 AI Data Cleaner & Formatter")
uploaded_file = st.file_uploader("Ανέβασε Excel ή CSV", type=["xlsx", "csv"])

if uploaded_file and api_key:
    client = OpenAI(api_key=api_key)
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.write("### Προεπισκόπηση Δεδομένων")
    st.dataframe(df.head())
    
    column_to_clean = st.selectbox("Επίλεξε στήλη για καθαρισμό", df.columns)
    
    if st.button("🚀 Έναρξη Καθαρισμού"):
        with st.spinner("Το AI καθαρίζει τα δεδομένα σου... παρακαλώ περιμένετε (1 δευτ./γραμμή)"):
            cleaned_values = []
            progress_bar = st.progress(0)
            total_rows = len(df)
            
            for i, val in enumerate(df[column_to_clean]):
                cleaned_val = clean_data_with_ai(val, client)
                cleaned_values.append(cleaned_val)
                time.sleep(1)  # Αποφυγή Rate Limit
                progress_bar.progress((i + 1) / total_rows)
            
            df[f"{column_to_clean}_Cleaned"] = cleaned_values
            st.success("Έτοιμο!")
            st.dataframe(df)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Κατέβασμα", data=output.getvalue(), file_name="cleaned_data.xlsx")
elif not api_key:
    st.warning("Παρακαλώ εισάγετε το OpenAI API Key στα αριστερά.")









