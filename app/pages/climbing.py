import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Escalade — Sport Predictor", page_icon="🧗", layout="wide")

API_URL = "http://localhost:8008/api/v1/climbing"

LEVEL_COLORS = {
    "Débutant (< 6a)":                "#74C0FC",
    "Intermédiaire bas (6a–6b+)":     "#69DB7C",
    "Intermédiaire (6c–7a+)":         "#FFD43B",
    "Avancé (7b–7c+)":                "#FF922B",
    "Expert (8a+)":                   "#F03E3E",
}

def plot_probabilities(probabilities: dict, predicted_label: str):
    labels = list(probabilities.keys())
    values = [v * 100 for v in probabilities.values()]
    colors = [
        "#1E57B0" if label == predicted_label else "#ADB5BD"
        for label in labels
    ]
    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{v:.1f}%" for v in values],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Probabilité : %{text}<extra></extra>",
    ))
    fig.update_layout(
        title="Distribution des probabilités par niveau",
        xaxis_title="Probabilité (%)",
        xaxis=dict(range=[0, 105]),
        plot_bgcolor="white",
        height=300,
        margin=dict(t=50, b=30, l=200),
        showlegend=False,
    )
    fig.update_xaxes(gridcolor="#f0f0f0")
    return fig

def plot_level_gauge(level_class: int):
    level_names = ["Débutant", "Inter. bas", "Intermédiaire", "Avancé", "Expert"]
    colors_gauge = ["#74C0FC", "#69DB7C", "#FFD43B", "#FF922B", "#F03E3E"]

    fig = go.Figure()
    for i, (name, color) in enumerate(zip(level_names, colors_gauge)):
        fig.add_trace(go.Bar(
            x=[1], y=[name],
            orientation="h",
            marker_color=color if i == level_class else "#E9ECEF",
            marker_line_width=2 if i == level_class else 0,
            marker_line_color="#1E57B0" if i == level_class else "transparent",
            showlegend=False,
            hoverinfo="skip",
        ))
    fig.update_layout(
        title="Niveau prédit",
        barmode="overlay",
        plot_bgcolor="white",
        height=250,
        margin=dict(t=50, b=10, l=10),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
    )
    return fig

# --- UI ---
st.title("🧗 Prédiction Escalade")
st.markdown("Estimez votre niveau en falaise (cotation française) selon votre profil.")
st.markdown("---")

st.info(
    "💡 **Comment ça marche ?** Si vous n'avez jamais grimpé (`années de pratique = 0`), "
    "l'estimation est basée sur votre profil physique. "
    "Si vous avez déjà de l'expérience, un modèle ML prédit votre niveau."
)

with st.form("climbing_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Profil physique")
        age = st.number_input("Âge", min_value=10, max_value=80, value=25)
        gender = st.selectbox("Sexe", ["Homme", "Femme"])
        gender_val = 0 if gender == "Homme" else 1
        height = st.number_input("Taille (cm)", min_value=140, max_value=220, value=175)
        weight = st.number_input("Poids (kg)", min_value=40.0, max_value=130.0, value=68.0, step=0.5)

    with col2:
        st.markdown("##### Expérience & Tests physiques")
        years = st.number_input(
            "Années de pratique escalade",
            min_value=0.0, max_value=50.0, value=0.0, step=0.5,
            help="Mettez 0 si vous n'avez jamais grimpé."
        )
        st.markdown("*Tests optionnels (améliorent la précision en mode débutant) :*")
        dead_hang = st.number_input(
            "Temps de suspension barre (secondes)",
            min_value=0, max_value=300, value=0,
            help="Suspendez-vous à une barre, les bras tendus, et mesurez le temps."
        )
        pullups = st.number_input(
            "Nombre max de tractions",
            min_value=0, max_value=50, value=0
        )

    submitted = st.form_submit_button("Prédire mon niveau", use_container_width=True)

if submitted:
    with st.spinner("Analyse en cours..."):
        try:
            payload = {
                "age": age,
                "gender": gender_val,
                "height_cm": float(height),
                "weight_kg": float(weight),
                "years_climbing": float(years),
                "dead_hang_seconds": dead_hang if dead_hang > 0 else None,
                "max_pullups": pullups if pullups > 0 else None,
            }
            resp = requests.post(f"{API_URL}/predict", json=payload, timeout=10)

            if resp.status_code == 200:
                data = resp.json()

                st.markdown("---")
                st.markdown("## Résultats")

                # Résultat principal
                level_color = LEVEL_COLORS.get(data["level_label"], "#ADB5BD")
                mode_label = "⚗️ Règles physiologiques" if data["mode_used"] == "potential" else "🤖 Modèle ML"
                confidence_labels = {"low": "🟡 Faible", "medium": "🟠 Moyenne", "high": "🟢 Élevée"}

                res_col1, res_col2, res_col3 = st.columns([2, 1, 1])
                with res_col1:
                    st.markdown(
                        f"<div style='background-color:{level_color}; padding:20px; border-radius:10px; text-align:center;'>"
                        f"<h2 style='margin:0; color:#212529;'>{data['level_label']}</h2>"
                        f"<h3 style='margin:5px 0 0 0; color:#495057;'>Fourchette : {data['grade_range']}</h3>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with res_col2:
                    st.metric("Mode utilisé", mode_label)
                with res_col3:
                    st.metric("Fiabilité", confidence_labels.get(data["confidence"], data["confidence"]))

                st.markdown("---")

                # Graphique probabilités (mode ML uniquement)
                if data.get("probabilities"):
                    st.plotly_chart(
                        plot_probabilities(data["probabilities"], data["level_label"]),
                        use_container_width=True
                    )

                if data.get("disclaimer"):
                    st.warning(f"⚠️ {data['disclaimer']}")

            else:
                err = resp.json()
                st.error(f"Erreur API ({resp.status_code}) : {err.get('detail', resp.text)}")

        except requests.exceptions.ConnectionError:
            st.error("❌ L'API n'est pas accessible. Lancez-la avec : `python3 -m uvicorn api.main:app --reload --port 8008`")

st.markdown("---")
with st.expander("ℹ️ Comment fonctionnent les prédictions ?"):
    st.markdown("""
**Mode Potentiel** (années de pratique = 0) :
- Basé sur des règles physiologiques (BMI, dead hang, tractions)
- Retourne une fourchette de potentiel après 1-2 ans de pratique sérieuse
- Fiabilité faible — fortement dépendant de l'entraînement

**Mode ML** (années de pratique ≥ 1) :
- Modèle Gradient Boosting entraîné sur 10 927 grimpeurs (dataset 8a.nu)
- Accuracy exacte : ~38% | Accuracy ±1 classe : **78%**
- Features : sexe, taille, poids, BMI, âge, années de pratique

**Niveaux et cotations :**
| Niveau | Cotation française |
|---|---|
| Débutant | < 6a |
| Intermédiaire bas | 6a → 6b+ |
| Intermédiaire | 6c → 7a+ |
| Avancé | 7b → 7c+ |
| Expert | 8a et + |

**Limite connue** : Le dataset est surreprésenté en grimpeurs avancés.
Les prédictions sont plus fiables au-dessus du niveau 6a.
    """)
