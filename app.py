import streamlit as st
import pandas as pd
from openai import OpenAI
import io

# Ρύθμιση σελίδας
st.set_page_config(page_title="AI Data Cleaner", layout="wide")

def clean_data_with_ai(dirty_text, client):
    if not dirty_text or pd.isna(dirty_text) or str(dirty_text).strip() == "":
        return dirty_text
    
    # Αυστηρό prompt για εγγυημένα αποτελέσματα στα Ελληνικά
    prompt = (
        f"Είσαι ένας έμπειρος διορθωτής δεδομένων. Διορθώσε την τιμή: '{dirty_text}'.\n"
        f"ΚΑΝΟΝΕΣ:\n"
        f"1. Διόρθωσε ορθογραφικά (π.χ. Ιωννης -> Ιωάννης).\n"
        f"2. Βάλε σωστούς τόνους παντού.\n"
        f"3. Κάνε Proper Case (π.χ. ΠΑΠΑΔΟΠΟΥΛΟΣ -> Παπαδόπουλος).\n"
        f"4. Αφαίρεσε περιττά κενά.\n"
        f"Απάντησε ΜΟΝΟ με τη διορθωμένη τιμή."
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Χρήση του ισχυρού μοντέλου
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Sidebar για το API Key
st.sidebar.title("Ρυθμίσεις")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# Αν δεν υπάρχει κλειδί στο πλαίσιο, έλεγχος στα Secrets
if not api_key and "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]

st.title("🚀 AI Data Cleaner & Formatter")
uploaded_file = st.file_uploader("Ανέβασε Excel ή CSV", type=["xlsx", "csv"])

if uploaded_file and api_key:
    client = OpenAI(api_key=api_key)
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    
    st.write("### Προεπισκόπηση Δεδομένων")
    st.dataframe(df.head())
    
    column_to_clean = st.selectbox("Επίλεξε στήλη για καθαρισμό", df.columns)
    
    if st.button("🚀 Έναρξη Καθαρισμού"):
        with st.spinner("Το AI καθαρίζει τα δεδομένα σου..."):
            df[f"{column_to_clean}_Cleaned"] = df[column_to_clean].apply(lambda x: clean_data_with_ai(x, client))
            st.success("Έτοιμο!")
            st.dataframe(df)
            
            # Προετοιμασία αρχείου για κατέβασμα
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Κατέβασμα", data=output.getvalue(), file_name="cleaned_data.xlsx")
elif not api_key:
    st.warning("Παρακαλώ εισάγετε το OpenAI API Key στα αριστερά.")





