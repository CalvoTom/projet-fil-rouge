import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Running — Sport Predictor", page_icon="🏃", layout="wide")

API_URL = "http://localhost:8008/api/v1/running"

def seconds_to_display(s):
    s = int(s)
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    if h > 0:
        return f"{h}h {m:02d}m {sec:02d}s"
    return f"{m}m {sec:02d}s"

def format_pace(seconds, distance_km):
    pace_sec = seconds / distance_km
    m = int(pace_sec // 60)
    s = int(pace_sec % 60)
    return f"{m}:{s:02d} /km"

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
        marker_color=["#4C9BE8", "#3A7BD5", "#2E6AC7", "#1E57B0"],
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
    data = []
    distance_km = {"5km": 5, "10km": 10, "Semi-marathon": 21.0975, "Marathon": 42.195}
    for p in predictions:
        dist = distance_km.get(p["distance"])
        if dist:
            pace = p["seconds"] / dist
            data.append({"Distance": p["distance"], "Allure (sec/km)": pace,
                         "Allure": format_pace(p["seconds"], dist)})
    df = pd.DataFrame(data)
    fig = px.line(df, x="Distance", y="Allure (sec/km)", text="Allure",
                  markers=True, title="Allure par distance")
    fig.update_traces(
        textposition="top center",
        line=dict(color="#4C9BE8", width=2),
        marker=dict(size=10, color="#1E57B0"),
    )
    fig.update_layout(
        plot_bgcolor="white", height=300,
        yaxis=dict(autorange="reversed", gridcolor="#f0f0f0"),
        margin=dict(t=50, b=30),
    )
    return fig

# --- UI ---
st.title("🏃 Prédiction Running")
st.markdown("Obtenez une estimation de vos temps de course sur toutes les distances.")
st.markdown("---")

mode = st.radio(
    "Mode de prédiction",
    ["🔵 Mode simple (profil physiologique)", "🟢 Mode avancé (temps de référence)"],
    horizontal=True,
)
is_advanced = mode.startswith("🟢")

st.markdown("---")

with st.form("running_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Profil")
        age = st.number_input("Âge", min_value=15, max_value=85, value=30)
        gender = st.selectbox("Sexe", ["Homme", "Femme"])
        gender_val = 0 if gender == "Homme" else 1

    with col2:
        if not is_advanced:
            st.markdown("##### Données physiologiques")
            resting_hr = st.number_input("FC repos (bpm)", min_value=30, max_value=100, value=60,
                                          help="Mesurez votre fréquence cardiaque au repos le matin.")
            max_hr = st.number_input("FC max (bpm) — optionnel", min_value=0, max_value=220, value=0,
                                      help="Laissez à 0 si inconnue. Sera estimée via 220-âge.")
        else:
            st.markdown("##### Temps de référence récent")
            ref_type = st.selectbox("Distance de référence", ["5 km", "10 km"])
            ref_minutes = st.number_input("Minutes", min_value=10, max_value=200, value=22)
            ref_seconds = st.number_input("Secondes", min_value=0, max_value=59, value=0)

    submitted = st.form_submit_button("Prédire mes temps", use_container_width=True)

if submitted:
    with st.spinner("Calcul en cours..."):
        try:
            if not is_advanced:
                payload = {
                    "mode": "simple",
                    "age": age,
                    "gender": gender_val,
                    "resting_hr": resting_hr,
                    "max_hr": max_hr if max_hr > 0 else None,
                }
                resp = requests.post(f"{API_URL}/predict/simple", json=payload, timeout=10)
            else:
                total_sec = ref_minutes * 60 + ref_seconds
                if ref_type == "5 km":
                    payload = {"mode": "advanced", "age": age, "gender": gender_val,
                               "recent_5k_seconds": total_sec}
                else:
                    payload = {"mode": "advanced", "age": age, "gender": gender_val,
                               "recent_10k_seconds": total_sec}
                resp = requests.post(f"{API_URL}/predict/advanced", json=payload, timeout=10)

            if resp.status_code == 200:
                data = resp.json()
                predictions = data["predictions"]

                st.markdown("---")
                st.markdown("## Résultats")

                # Niveau
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

                # Temps par distance
                cols = st.columns(4)
                for col, pred in zip(cols, predictions):
                    col.metric(pred["distance"], pred["formatted"])

                st.markdown("---")

                col_left, col_right = st.columns(2)
                with col_left:
                    st.plotly_chart(plot_predictions(predictions), use_container_width=True)
                with col_right:
                    st.plotly_chart(plot_pace_chart(predictions), use_container_width=True)

                # Infos supplémentaires
                st.markdown("---")
                info_cols = st.columns(3)
                if data.get("vo2max_estimated"):
                    info_cols[0].metric("VO2max estimé", f"{data['vo2max_estimated']} ml/kg/min")
                info_cols[1].metric("Méthode", data["method"].split(" (")[0])
                confidence_labels = {"low": "🟡 Faible", "medium": "🟠 Moyenne", "high": "🟢 Élevée"}
                info_cols[2].metric("Fiabilité", confidence_labels.get(data["confidence"], data["confidence"]))

                if data.get("disclaimer"):
                    st.info(f"ℹ️ {data['disclaimer']}")

            else:
                try:
                    detail = resp.json().get("detail", resp.text)
                except Exception:
                    detail = resp.text or "Erreur inconnue"
                st.error(f"Erreur API ({resp.status_code}) : {detail}")

        except requests.exceptions.ConnectionError:
            st.error("❌ L'API n'est pas accessible. Lancez-la avec : `python3 -m uvicorn api.main:app --reload --port 8008`")

st.markdown("---")
with st.expander("ℹ️ Comment fonctionnent les prédictions ?"):
    st.markdown("""
**Mode simple** — Sans temps de course de référence :
- Estimation du VO2max depuis la fréquence cardiaque (formule Uth et al.)
- Conversion en temps marathon via tables VDOT (Jack Daniels)
- Extrapolation des autres distances via formule Riegel
- Précision indicative ±15-20%

**Mode avancé** — Avec un temps récent :
- Modèle Gradient Boosting entraîné sur 79 638 finishers du Boston Marathon (2015-2017)
- MAE : ~14 minutes sur marathon | MAPE : ~5.8%
- Extrapolation des autres distances via formule Riegel

**Limite connue** : Le dataset Boston Marathon contient des coureurs qualifiés (temps minimum requis).
Les prédictions pour des temps > 4h30 sont moins fiables.
    """)
