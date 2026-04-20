import streamlit as st

st.set_page_config(
    page_title="Sport Predictor",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Sport Predictor")
st.markdown("### Prédiction de performances sportives personnalisées")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🏃 Running")
    st.markdown(
        "Prédisez vos temps sur **5km, 10km, semi-marathon et marathon** "
        "à partir de votre profil physiologique ou d'un temps de référence récent."
    )
    if st.button("Accéder au Running", use_container_width=True):
        st.switch_page("pages/running.py")

with col2:
    st.markdown("#### 🧗 Escalade")
    st.markdown(
        "Estimez votre **niveau en falaise** (cotation française) "
        "à partir de votre profil physique et de votre expérience."
    )
    if st.button("Accéder à l'Escalade", use_container_width=True):
        st.switch_page("pages/climbing.py")

st.markdown("---")
st.caption("Projet fil rouge — Ynov Bachelor 3 Data & IA | Modèles entraînés sur Boston Marathon 2015-2017 et 8a.nu Climb Dataset")
