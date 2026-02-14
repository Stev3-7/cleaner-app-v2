import streamlit as st
import pandas as pd
from openai import OpenAI
import io

def clean_data_with_ai(dirty_text, client):
    if pd.isna(dirty_text) or str(dirty_text).strip() == "":
        return dirty_text
    prompt = f"Είσαι Data Expert. Καθάρισε, διόρθωσε ορθογραφικά και βγάλε περιττά κενά (TRIM) από την τιμή: '{dirty_text}'. Δώσε ΜΟΝΟ την καθαρή τιμή."
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except:
        return dirty_text

st.set_page_config(page_title="AI Data Cleaner", layout="wide")
st.title("🧼 AI Data Cleaner & Formatter")

api_key = st.sidebar.text_input("OpenAI API Key", type="password")
uploaded_file = st.file_uploader("Ανέβασε Excel ή CSV", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
    st.write("### Προεπισκόπηση", df.head())
    
    col_to_clean = st.selectbox("Επίλεξε στήλη για καθάρισμα:", df.columns)
    
    if st.button("🚀 Έναρξη Καθαρισμού"):
        if not api_key:
            st.error("Βάλε το API Key σου αριστερά!")
        else:
            client = OpenAI(api_key=api_key)
            with st.spinner('Καθαρίζεται...'):
                df[f'{col_to_clean}_Cleaned'] = df[col_to_clean].apply(lambda x: clean_data_with_ai(x, client))
            st.success("Έτοιμο!")
            st.write(df.head())
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Κατέβασμα", data=output.getvalue(), file_name="cleaned.xlsx")