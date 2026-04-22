import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Tennis — Sport Predictor", page_icon="🎾", layout="wide")

API_URL = "http://localhost:8008/api/v1/tennis"

LEVEL_COLORS = {
    "Joueur de club":          "#74C0FC",
    "Compétiteur régional":    "#69DB7C",
    "Joueur national":         "#FF922B",
    "Expert / Pro":            "#F03E3E",
}

# Stats de référence par niveau (pour affichage comparatif)
REF_STATS_LABELS = {
    "first_serve_pct":      "1ère balle entrée (%)",
    "ace_rate":             "Aces (%)",
    "df_rate":              "Doubles fautes (%)",
    "first_serve_won_pct":  "Pts gagnés sur 1ère balle (%)",
    "second_serve_won_pct": "Pts gagnés sur 2ème balle (%)",
    "bp_saved_pct":         "Balles de break sauvées (%)",
}


def plot_proba_bar(probas: dict):
    labels = list(probas.keys())
    values = [v * 100 for v in probas.values()]
    colors = [LEVEL_COLORS.get(l, "#ADB5BD") for l in labels]

    fig = go.Figure(go.Bar(
        x=labels, y=values,
        text=[f"{v:.1f}%" for v in values],
        textposition="outside",
        marker_color=colors,
        hovertemplate="<b>%{x}</b> : %{text}<extra></extra>",
    ))
    fig.update_layout(
        title="Probabilités par niveau",
        yaxis=dict(title="Probabilité (%)", range=[0, 110]),
        xaxis_title="Niveau",
        showlegend=False,
        plot_bgcolor="white",
        height=320,
        margin=dict(t=50, b=30),
    )
    fig.update_yaxes(gridcolor="#f0f0f0")
    return fig


def plot_radar_comparison(user_stats: dict, ref_stats: dict, level_label: str):
    cats = list(REF_STATS_LABELS.values())
    keys = list(REF_STATS_LABELS.keys())

    user_vals = [user_stats.get(k, 0) for k in keys]
    ref_vals  = [ref_stats.get(k, 0)  for k in keys]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=user_vals + [user_vals[0]], theta=cats + [cats[0]],
        fill="toself", name="Vos stats",
        line=dict(color="#228BE6"), fillcolor="rgba(34,139,230,0.15)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=ref_vals + [ref_vals[0]], theta=cats + [cats[0]],
        fill="toself", name=f"Référence {level_label}",
        line=dict(color="#F03E3E", dash="dash"), fillcolor="rgba(240,62,62,0.10)",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Vos stats vs référence du niveau prédit",
        showlegend=True,
        height=380,
        margin=dict(t=60, b=30),
    )
    return fig


# ─── UI ───────────────────────────────────────────────────────────────────────

st.title("🎾 Prédiction Tennis")
st.markdown("Estimez votre niveau de jeu (équivalent classement national / ATP / WTA).")
st.markdown("---")

mode = st.radio(
    "Mode de prédiction",
    ["🔵 Mode simple (profil + expérience)", "🟢 Mode avancé (statistiques de service)"],
    horizontal=True,
)
is_advanced = mode.startswith("🟢")

st.markdown("---")

with st.form("tennis_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Profil")
        gender    = st.selectbox("Sexe", ["Homme", "Femme"])
        gender_val = 0 if gender == "Homme" else 1

        if not is_advanced:
            age            = st.number_input("Âge", min_value=10, max_value=60, value=25)
            height_cm      = st.number_input("Taille (cm)", min_value=140, max_value=220, value=178)
            years_practice = st.number_input(
                "Années de pratique du tennis",
                min_value=0.0, max_value=40.0, value=5.0, step=0.5,
            )

    with col2:
        if is_advanced:
            st.markdown("##### Vos statistiques de service")
            st.caption("Ces stats peuvent être mesurées lors d'une session d'entraînement ou relevées depuis votre appli de scores.")
            first_serve_pct      = st.slider("1ère balle entrée (%)", 0, 100, 60,
                                              help="Sur 100 points de service, combien de 1ères balles entrent ?")
            ace_rate             = st.slider("Aces (%)", 0.0, 25.0, 5.0, step=0.5,
                                              help="% d'aces parmi vos points de service")
            df_rate              = st.slider("Doubles fautes (%)", 0.0, 20.0, 4.0, step=0.5,
                                              help="% de doubles fautes parmi vos points de service")
            first_serve_won_pct  = st.slider("Pts gagnés sur 1ère balle (%)", 0, 100, 68,
                                              help="Quand votre 1ère balle entre, combien de points gagnez-vous ?")
            second_serve_won_pct = st.slider("Pts gagnés sur 2ème balle (%)", 0, 100, 48,
                                              help="Quand vous jouez 2ème balle, combien de points gagnez-vous ?")
            bp_saved_pct         = st.slider("Balles de break sauvées (%)", 0, 100, 50,
                                              help="% de balles de break que vous sauvez (optionnel — laissez 50 si inconnu)")
        else:
            st.markdown("##### À propos du mode simple")
            st.info(
                "Le modèle GradientBoosting est entraîné sur 7 700+ profils de joueurs "
                "ATP/WTA (2010-2023). Il prédit votre niveau depuis votre âge, taille et "
                "années de pratique. Pour les joueurs amateurs, l'estimation est indicative."
            )

    submitted = st.form_submit_button("Prédire mon niveau", use_container_width=True)


if submitted:
    with st.spinner("Analyse en cours…"):
        try:
            if not is_advanced:
                payload = {
                    "mode": "simple",
                    "age": age,
                    "gender": gender_val,
                    "height_cm": height_cm,
                    "years_practice": years_practice,
                }
                resp = requests.post(f"{API_URL}/predict/simple", json=payload, timeout=10)
            else:
                payload = {
                    "mode": "advanced",
                    "gender": gender_val,
                    "first_serve_pct": first_serve_pct,
                    "ace_rate": ace_rate,
                    "df_rate": df_rate,
                    "first_serve_won_pct": first_serve_won_pct,
                    "second_serve_won_pct": second_serve_won_pct,
                    "bp_saved_pct": bp_saved_pct,
                }
                resp = requests.post(f"{API_URL}/predict/advanced", json=payload, timeout=10)

            if resp.status_code == 200:
                data = resp.json()

                st.markdown("---")
                st.markdown("## Résultats")

                # Niveau prédit
                level  = data["level_label"]
                color  = LEVEL_COLORS.get(level, "#ADB5BD")
                st.markdown(
                    f"<div style='background:{color};padding:14px 20px;border-radius:8px;"
                    f"display:inline-block;margin-bottom:16px'>"
                    f"<span style='font-size:1.3rem;font-weight:700;color:#212529'>"
                    f"🎾 {level}</span></div>",
                    unsafe_allow_html=True,
                )

                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Équivalent classement FR", data["level_equiv"])
                col_b.metric("Équivalent ATP/WTA", data["level_rank_range"])
                confidence_labels = {"low": "🟡 Faible", "medium": "🟠 Moyenne", "high": "🟢 Élevée"}
                col_c.metric("Fiabilité", confidence_labels.get(data["confidence"], data["confidence"]))

                st.markdown("---")

                if is_advanced and data.get("ref_stats"):
                    # Radar : user stats vs référence niveau
                    user_stats_display = {
                        "first_serve_pct":      first_serve_pct,
                        "ace_rate":             ace_rate,
                        "df_rate":              df_rate,
                        "first_serve_won_pct":  first_serve_won_pct,
                        "second_serve_won_pct": second_serve_won_pct,
                        "bp_saved_pct":         bp_saved_pct,
                    }
                    col_left, col_right = st.columns([3, 2])
                    with col_left:
                        st.plotly_chart(
                            plot_radar_comparison(user_stats_display, data["ref_stats"], level),
                            use_container_width=True,
                        )
                    with col_right:
                        st.markdown("##### Statistiques de référence du niveau")
                        ref = data["ref_stats"]
                        ref_df = pd.DataFrame({
                            "Stat":           list(REF_STATS_LABELS.values()),
                            "Vos stats":      [user_stats_display.get(k, "—") for k in REF_STATS_LABELS],
                            f"{level} (moy)": [ref.get(k, "—") for k in REF_STATS_LABELS],
                        })
                        st.dataframe(ref_df, hide_index=True, use_container_width=True)
                else:
                    col_left, col_right = st.columns(2)
                    with col_left:
                        st.plotly_chart(plot_proba_bar(data["probabilities"]),
                                        use_container_width=True)
                    with col_right:
                        if data.get("ref_stats"):
                            st.markdown("##### Statistiques typiques du niveau prédit")
                            ref = data["ref_stats"]
                            ref_df = pd.DataFrame({
                                "Stat":           list(REF_STATS_LABELS.values()),
                                f"{level} (moy)": [ref.get(k, "—") for k in REF_STATS_LABELS],
                            })
                            st.dataframe(ref_df, hide_index=True, use_container_width=True)

                if not is_advanced and data.get("probabilities"):
                    st.markdown("---")
                    st.plotly_chart(plot_proba_bar(data["probabilities"]),
                                    use_container_width=True)

                st.markdown("---")
                st.caption(f"Méthode : {data['method']}")
                if data.get("disclaimer"):
                    st.info(f"ℹ️ {data['disclaimer']}")

            else:
                st.error(f"Erreur API ({resp.status_code}) : {resp.json().get('detail', resp.text)}")

        except requests.exceptions.ConnectionError:
            st.error("❌ L'API n'est pas accessible. Lancez-la avec : `python3 -m uvicorn api.main:app --reload --port 8008`")


st.markdown("---")
with st.expander("ℹ️ Comment fonctionnent les prédictions ?"):
    st.markdown("""
**Mode simple** — Profil physique + expérience :
- Modèle GradientBoosting entraîné sur 7 700+ profils ATP/WTA (2010-2023)
- Features : âge, genre, taille, années de pratique
- Prédit le niveau parmi 4 classes (Joueur de club → Expert/Pro)
- Accuracy : 53% exacte, 94% à ±1 niveau près

**Mode avancé** — Statistiques de service :
- Même architecture entraînée sur les mêmes données
- Features : % 1ère balle, ace %, df %, % pts gagnés sur 1ère/2ème balle, % break sauvés
- Ces stats sont mesurables lors d'une session ou via une app de scores
- Accuracy : 61% exacte, 95% à ±1 niveau près
- Affiche un radar de comparaison avec les moyennes du niveau prédit

**Niveaux et équivalences :**
| Niveau | Classement FR | ATP/WTA |
|---|---|---|
| Joueur de club | 30/1 – 15/1 | > 500 |
| Compétiteur régional | 4/6 – 0 | 201–500 |
| Joueur national | -2/6 – -15 | 51–200 |
| Expert / Pro | -30 et au-delà | ≤ 50 |

**Données** : Jeff Sackmann ATP/WTA Tennis Dataset 2010-2023
([github.com/JeffSackmann](https://github.com/JeffSackmann/tennis_atp))
    """)
