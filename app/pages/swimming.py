import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Natation — Sport Predictor", page_icon="🏊", layout="wide")

API_URL = "http://localhost:8008/api/v1/swimming"

def plot_predictions(predictions):
    distances = [p["distance"] for p in predictions]
    seconds = [p["seconds"] for p in predictions]
    formatted = [p["formatted"] for p in predictions]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=distances,
        y=[s / 60 for s in seconds],
        text=formatted,
        textposition="outside",
        marker_color=["#4ECDC4", "#2EC4B6", "#1BA8A0", "#0D8C86"],
        hovertemplate="<b>%{x}</b><br>Temps : %{text}<extra></extra>",
    ))
    fig.update_layout(
        title="Temps prédits par distance",
        yaxis_title="Temps (minutes)",
        xaxis_title="Distance",
        showlegend=False,
        plot_bgcolor="white",
        height=350,
        margin=dict(t=50, b=30),
    )
    fig.update_yaxes(gridcolor="#f0f0f0")
    return fig

def plot_pace_chart(predictions):
    data = [{"Distance": p["distance"], "Allure": p["pace_per_100m"]} for p in predictions]
    df = pd.DataFrame(data)
    # Convertir allure en secondes pour l'axe
    def pace_to_sec(pace_str):
        parts = pace_str.replace("/100m", "").split(":")
        return int(parts[0]) * 60 + int(parts[1])
    df["pace_sec"] = df["Allure"].apply(pace_to_sec)

    fig = px.line(df, x="Distance", y="pace_sec", text="Allure",
                  markers=True, title="Allure par distance (/100m)")
    fig.update_traces(
        textposition="top center",
        line=dict(color="#4ECDC4", width=2),
        marker=dict(size=10, color="#0D8C86"),
    )
    fig.update_layout(
        plot_bgcolor="white", height=300,
        yaxis=dict(autorange="reversed", gridcolor="#f0f0f0", title="Allure (s/100m)"),
        margin=dict(t=50, b=30),
    )
    return fig

# --- UI ---
st.title("🏊 Prédiction Natation")
st.markdown("Estimez vos temps sur les distances clés de la natation (piscine et eau libre).")
st.markdown("---")

mode = st.radio(
    "Mode de prédiction",
    ["🔵 Mode simple (profil uniquement)", "🟢 Mode avancé (temps de référence)"],
    horizontal=True,
)
is_advanced = mode.startswith("🟢")

st.markdown("---")

with st.form("swimming_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Profil")
        age = st.number_input("Âge", min_value=10, max_value=85, value=30)
        gender = st.selectbox("Sexe", ["Homme", "Femme"])
        gender_val = 0 if gender == "Homme" else 1

    with col2:
        if is_advanced:
            st.markdown("##### Temps de référence récent")
            ref_dist = st.selectbox("Distance de référence", ["100m", "200m", "400m", "750m", "1500m"])
            ref_dist_map = {"100m": 100, "200m": 200, "400m": 400, "750m": 750, "1500m": 1500}
            ref_minutes = st.number_input("Minutes", min_value=0, max_value=120, value=7)
            ref_seconds_input = st.number_input("Secondes", min_value=0, max_value=59, value=30)
        else:
            st.markdown("##### Mode simple")
            st.info("Le modèle prédit votre performance attendue selon votre âge et genre, sur la base de 2,5M+ résultats de triathlons (Sprint / Olympic / Half / Full).")

    submitted = st.form_submit_button("Prédire mes temps", use_container_width=True)

if submitted:
    with st.spinner("Calcul en cours..."):
        try:
            if not is_advanced:
                payload = {"mode": "simple", "age": age, "gender": gender_val}
                resp = requests.post(f"{API_URL}/predict/simple", json=payload, timeout=10)
            else:
                total_sec = ref_minutes * 60 + ref_seconds_input
                payload = {
                    "mode": "advanced",
                    "age": age,
                    "gender": gender_val,
                    "ref_distance_m": ref_dist_map[ref_dist],
                    "ref_time_seconds": total_sec,
                }
                resp = requests.post(f"{API_URL}/predict/advanced", json=payload, timeout=10)

            if resp.status_code == 200:
                data = resp.json()
                predictions = data["predictions"]

                st.markdown("---")
                st.markdown("## Résultats")

                level_colors = {
                    "Débutant":      "#74C0FC",
                    "Intermédiaire": "#69DB7C",
                    "Avancé":        "#FF922B",
                    "Expert":        "#F03E3E",
                }
                level = data.get("level_label", "")
                color = level_colors.get(level, "#ADB5BD")
                st.markdown(
                    f"<div style='background:{color};padding:14px 20px;border-radius:8px;"
                    f"display:inline-block;margin-bottom:16px'>"
                    f"<span style='font-size:1.2rem;font-weight:600;color:#212529'>Niveau : {level}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                cols = st.columns(4)
                for col, pred in zip(cols, predictions):
                    col.metric(pred["distance"], pred["formatted"], pred["pace_per_100m"])

                st.markdown("---")
                col_left, col_right = st.columns(2)
                with col_left:
                    st.plotly_chart(plot_predictions(predictions), use_container_width=True)
                with col_right:
                    st.plotly_chart(plot_pace_chart(predictions), use_container_width=True)

                st.markdown("---")
                info_cols = st.columns(2)
                info_cols[0].metric("Méthode", data["method"].split(" (")[0])
                confidence_labels = {"low": "🟡 Faible", "medium": "🟠 Moyenne", "high": "🟢 Élevée"}
                info_cols[1].metric("Fiabilité", confidence_labels.get(data["confidence"], data["confidence"]))

                if data.get("disclaimer"):
                    st.info(f"ℹ️ {data['disclaimer']}")

            else:
                err = resp.json()
                st.error(f"Erreur API ({resp.status_code}) : {err.get('detail', resp.text)}")

        except requests.exceptions.ConnectionError:
            st.error("❌ L'API n'est pas accessible. Lancez-la avec : `python3 -m uvicorn api.main:app --reload --port 8008`")

st.markdown("---")
with st.expander("ℹ️ Comment fonctionnent les prédictions ?"):
    st.markdown("""
**Mode simple** — Sans temps de référence :
- Modèle Gradient Boosting entraîné sur 2,5M+ résultats de triathlons (Sprint 750m / Olympic 1500m / Half 1900m / Full 3800m)
- Prédit l'allure attendue selon votre profil âge/genre
- Précision indicative ±20%

**Mode avancé** — Avec un temps récent :
- Formule Riegel : T₂ = T₁ × (D₂/D₁)^1.06
- Extrapolation à partir de votre temps sur une distance connue (100m, 400m, 750m, 1500m...)
- Niveau déterminé par comparaison à la distribution des 2,5M+ athlètes

**Seuils de niveau (allure /100m)** :
- Débutant : > 2:30/100m
- Intermédiaire : 2:00–2:30/100m
- Avancé : 1:30–2:00/100m
- Expert : < 1:30/100m
    """)
