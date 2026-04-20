import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Vélo — Sport Predictor", page_icon="🚴", layout="wide")

API_URL = "http://localhost:8008/api/v1/cycling"

def seconds_to_display(s):
    s = int(s)
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    if h > 0:
        return f"{h}h {m:02d}m {sec:02d}s"
    return f"{m}m {sec:02d}s"

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
        marker_color=["#F5A623", "#E8901A", "#D97B0F", "#C66A00"],
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

def plot_speed_chart(predictions):
    data = [{"Distance": p["distance"], "Vitesse (km/h)": p["speed_kmh"],
             "Label": f"{p['speed_kmh']} km/h"} for p in predictions]
    df = pd.DataFrame(data)
    fig = px.line(df, x="Distance", y="Vitesse (km/h)", text="Label",
                  markers=True, title="Vitesse moyenne par distance")
    fig.update_traces(
        textposition="top center",
        line=dict(color="#F5A623", width=2),
        marker=dict(size=10, color="#C66A00"),
    )
    fig.update_layout(
        plot_bgcolor="white", height=300,
        yaxis=dict(gridcolor="#f0f0f0"),
        margin=dict(t=50, b=30),
    )
    return fig

# --- UI ---
st.title("🚴 Prédiction Vélo de route")
st.markdown("Estimez vos temps sur les distances clés du vélo de route.")
st.markdown("---")

mode = st.radio(
    "Mode de prédiction",
    ["🔵 Mode simple (profil uniquement)", "🟢 Mode avancé (temps de référence)"],
    horizontal=True,
)
is_advanced = mode.startswith("🟢")

st.markdown("---")

with st.form("cycling_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Profil")
        age = st.number_input("Âge", min_value=15, max_value=85, value=30)
        gender = st.selectbox("Sexe", ["Homme", "Femme"])
        gender_val = 0 if gender == "Homme" else 1

    with col2:
        if is_advanced:
            st.markdown("##### Temps de référence récent")
            ref_dist = st.selectbox("Distance de référence", ["20 km", "40 km", "100 km"])
            ref_dist_map = {"20 km": 20.0, "40 km": 40.0, "100 km": 100.0}
            ref_hours = st.number_input("Heures", min_value=0, max_value=10, value=0)
            ref_minutes = st.number_input("Minutes", min_value=0, max_value=59, value=45)
            ref_seconds = st.number_input("Secondes", min_value=0, max_value=59, value=0)
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
                total_sec = ref_hours * 3600 + ref_minutes * 60 + ref_seconds
                payload = {
                    "mode": "advanced",
                    "age": age,
                    "gender": gender_val,
                    "ref_distance_km": ref_dist_map[ref_dist],
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
                    col.metric(pred["distance"], pred["formatted"], f"{pred['speed_kmh']} km/h")

                st.markdown("---")
                col_left, col_right = st.columns(2)
                with col_left:
                    st.plotly_chart(plot_predictions(predictions), use_container_width=True)
                with col_right:
                    st.plotly_chart(plot_speed_chart(predictions), use_container_width=True)

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
- Modèle Gradient Boosting entraîné sur 2,5M+ résultats de triathlons (Sprint 20km / Olympic 40km / Half 90km / Full 180km)
- Prédit la vitesse moyenne attendue selon votre profil âge/genre
- Précision indicative ±15% (variance individuelle élevée sans temps de référence)

**Mode avancé** — Avec un temps récent :
- Formule Riegel : T₂ = T₁ × (D₂/D₁)^1.06
- Extrapolation à partir de votre temps sur une distance connue
- Niveau déterminé par comparaison à la distribution des 2,5M+ athlètes

**Seuils de niveau (vitesse sur 40km)** :
- Débutant : < 22 km/h
- Intermédiaire : 22–28 km/h
- Avancé : 28–34 km/h
- Expert : > 34 km/h
    """)
