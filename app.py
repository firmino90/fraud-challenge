"""
Interface Streamlit — Détection de fraude financière
Hackathon INTELO2026 — interface participant · évaluée par le jury
"""

from pathlib import Path
import streamlit as st
import pandas as pd
from fraud_detection import detect_fraud, load_transactions

SAMPLE_CSV = Path(__file__).parent / "data" / "sample_transactions.csv"

# ── CSS Premium ──────────────────────────────────────────────────────────────
PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

:root {
    --bg:        #050a12;
    --bg2:       #0b1422;
    --bg3:       #101d30;
    --border:    #1e3a5f;
    --accent:    #00e5ff;
    --accent2:   #ff3d71;
    --accent3:   #00e096;
    --text:      #e2eaf4;
    --muted:     #5a7a9a;
    --card:      #0d1928;
    --glow:      0 0 20px rgba(0,229,255,0.15);
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Main background */
.stApp {
    background: var(--bg) !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(0,229,255,0.06) 0%, transparent 60%),
        linear-gradient(180deg, #050a12 0%, #070e1a 100%) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Cards / Metrics */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: var(--glow) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 30px rgba(0,229,255,0.2) !important;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.75rem !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; }
[data-testid="stMetricValue"] { color: var(--accent) !important; font-family: 'Space Mono', monospace !important; font-size: 2rem !important; }
[data-testid="stMetricDelta"] { font-family: 'Space Mono', monospace !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00e5ff22, #00e5ff11) !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
    padding: 12px 28px !important;
    transition: all 0.2s !important;
    box-shadow: 0 0 15px rgba(0,229,255,0.1) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #00e5ff44, #00e5ff22) !important;
    box-shadow: 0 0 25px rgba(0,229,255,0.3) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #ff3d7133, #ff3d7111) !important;
    border-color: var(--accent2) !important;
    color: var(--accent2) !important;
    box-shadow: 0 0 15px rgba(255,61,113,0.2) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 30px rgba(255,61,113,0.4) !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* Selectbox / Inputs */
.stSelectbox > div > div,
.stTextInput > div > div {
    background: var(--bg3) !important;
    border-color: var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--accent) !important;
}

/* Spinner */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* Toggle */
.stToggle label { color: var(--text) !important; }

/* Divider */
hr { border-color: var(--border) !important; }

/* Custom scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* Animated scan line effect on header */
@keyframes scan {
    0% { transform: translateY(-100%); opacity: 0.05; }
    100% { transform: translateY(100vh); opacity: 0.05; }
}
.scan-line {
    position: fixed; top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    animation: scan 4s linear infinite;
    pointer-events: none;
    z-index: 9999;
}

/* Pulse animation for alert badge */
@keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255,61,113,0.4); }
    50% { box-shadow: 0 0 0 8px rgba(255,61,113,0); }
}
.alert-badge {
    display: inline-block;
    background: rgba(255,61,113,0.15);
    border: 1px solid var(--accent2);
    color: var(--accent2);
    border-radius: 20px;
    padding: 3px 12px;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    animation: pulse-red 2s infinite;
}
.ok-badge {
    display: inline-block;
    background: rgba(0,224,150,0.1);
    border: 1px solid var(--accent3);
    color: var(--accent3);
    border-radius: 20px;
    padding: 3px 12px;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
}

/* Score bar */
.score-bar-container {
    background: var(--bg3);
    border-radius: 4px;
    height: 8px;
    overflow: hidden;
    margin-top: 6px;
}
.score-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.8s ease;
}

/* Section headers */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 28px 0 16px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}
.section-header h3 {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    margin: 0 !important;
}
.dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 6px var(--accent);
}

/* Info / success / warning boxes */
.stAlert {
    background: var(--bg3) !important;
    border-color: var(--border) !important;
    border-radius: 10px !important;
}
</style>
<div class="scan-line"></div>
"""

# ── Hero header HTML ─────────────────────────────────────────────────────────
def render_hero():
    st.markdown("""
<div style="padding: 40px 0 20px 0;">
  <div style="display:flex; align-items:center; gap:16px; margin-bottom:8px;">
    <div style="width:48px; height:48px; background:linear-gradient(135deg,#00e5ff22,#00e5ff44);
                border:1px solid #00e5ff; border-radius:12px; display:flex;
                align-items:center; justify-content:center; font-size:24px; box-shadow:0 0 20px rgba(0,229,255,0.2);">
      🛡️
    </div>
    <div>
      <h1 style="margin:0; font-family:'Syne',sans-serif; font-size:2.2rem;
                 font-weight:800; background:linear-gradient(135deg,#e2eaf4,#00e5ff);
                 -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                 letter-spacing:-0.02em;">
        FRAUD SENTINEL
      </h1>
      <p style="margin:0; font-family:'Space Mono',monospace; font-size:0.7rem;
                color:#5a7a9a; letter-spacing:0.12em; text-transform:uppercase;">
        INTELO2026 · Détection de fraude financière · Système IA
      </p>
    </div>
  </div>
  <div style="width:60px; height:2px; background:linear-gradient(90deg,#00e5ff,transparent);
              margin-top:8px;"></div>
</div>
""", unsafe_allow_html=True)


# ── Risk score visual bar ─────────────────────────────────────────────────────
def score_bar(score: float) -> str:
    pct = int(score * 100)
    if score >= 0.7:
        color = "#ff3d71"
    elif score >= 0.5:
        color = "#ffaa00"
    elif score >= 0.3:
        color = "#ffdd00"
    else:
        color = "#00e096"
    return f"""
<div style="font-family:'Space Mono',monospace; font-size:0.8rem; color:#e2eaf4;">
  {score:.2f}
  <div class="score-bar-container">
    <div class="score-bar-fill" style="width:{pct}%; background:{color};
         box-shadow: 0 0 8px {color}88;"></div>
  </div>
</div>"""


# ── KPI Cards ─────────────────────────────────────────────────────────────────
def render_kpis(total, nb_suspects, nb_ok, pct_fraude):
    st.markdown("""
<div class="section-header">
  <div class="dot"></div>
  <h3>Tableau de bord temps réel</h3>
</div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TRANSACTIONS", total, help="Total analysées")
    c2.metric("🔴 ALERTES", nb_suspects,
              delta=f"+{pct_fraude}% du total", delta_color="inverse")
    c3.metric("🟢 VALIDÉES", nb_ok,
              delta=f"{100-pct_fraude:.1f}% sûres", delta_color="normal")
    c4.metric("⚠️ TAUX FRAUDE", f"{pct_fraude}%")


# ── Transaction table ─────────────────────────────────────────────────────────
def render_table(df_affiche):
    st.markdown("""
<div class="section-header" style="margin-top:32px;">
  <div class="dot" style="background:#ff3d71; box-shadow:0 0 6px #ff3d71;"></div>
  <h3>Journal des transactions</h3>
</div>""", unsafe_allow_html=True)

    colonnes = ["transaction_id", "user_id", "amount", "currency",
                "country", "card_present", "fraud_score", "is_suspicious", "reason"]
    cols_ok = [c for c in colonnes if c in df_affiche.columns]

    def colorier(row):
        if row.get("is_suspicious"):
            return ["background-color: rgba(255,61,113,0.08); color:#ffa0b4"] * len(row)
        return ["background-color: rgba(0,224,150,0.05); color:#a0ffd6"] * len(row)

    styled = (
        df_affiche[cols_ok]
        .style
        .apply(colorier, axis=1)
        .format({"fraud_score": "{:.2f}", "amount": "{:.2f}"})
    )
    st.dataframe(styled, use_container_width=True, height=380)
    st.caption(f"↳ {len(df_affiche)} transaction(s) affichée(s)")


# ── Transaction detail ────────────────────────────────────────────────────────
def render_detail(df_affiche):
    st.markdown("""
<div class="section-header" style="margin-top:32px;">
  <div class="dot" style="background:#7b61ff; box-shadow:0 0 6px #7b61ff;"></div>
  <h3>Analyse individuelle</h3>
</div>""", unsafe_allow_html=True)

    ids = df_affiche["transaction_id"].dropna().tolist()
    if not ids:
        st.info("Aucune transaction à afficher.")
        return

    tid = st.selectbox("Sélectionner une transaction", ids, key="detail_select")
    row = df_affiche[df_affiche["transaction_id"] == tid].iloc[0]
    score = float(row.get("fraud_score", 0))
    suspect = bool(row.get("is_suspicious", False))

    badge = '<span class="alert-badge">⚠ SUSPECTE</span>' if suspect else '<span class="ok-badge">✔ VALIDÉE</span>'

    st.markdown(f"""
<div style="background:#0d1928; border:1px solid {'#ff3d71' if suspect else '#1e3a5f'};
            border-radius:14px; padding:24px; margin-top:12px;
            box-shadow: {'0 0 20px rgba(255,61,113,0.1)' if suspect else '0 0 20px rgba(0,229,255,0.05)'};">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:20px;">
    <div>
      <div style="font-family:'Space Mono',monospace; font-size:0.7rem; color:#5a7a9a;
                  text-transform:uppercase; letter-spacing:0.1em;">ID Transaction</div>
      <div style="font-family:'Space Mono',monospace; font-size:1.1rem; color:#00e5ff; margin-top:2px;">
        {row.get('transaction_id','N/A')}
      </div>
    </div>
    {badge}
  </div>

  <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; margin-bottom:20px;">
    <div style="background:#0b1422; border-radius:8px; padding:14px; border:1px solid #1e3a5f;">
      <div style="font-size:0.65rem; color:#5a7a9a; text-transform:uppercase; letter-spacing:0.1em;">Client</div>
      <div style="font-family:'Space Mono',monospace; color:#e2eaf4; margin-top:4px;">{row.get('user_id','N/A')}</div>
    </div>
    <div style="background:#0b1422; border-radius:8px; padding:14px; border:1px solid #1e3a5f;">
      <div style="font-size:0.65rem; color:#5a7a9a; text-transform:uppercase; letter-spacing:0.1em;">Montant</div>
      <div style="font-family:'Space Mono',monospace; color:#e2eaf4; margin-top:4px;">
        {row.get('amount','N/A')} {row.get('currency','')}
      </div>
    </div>
    <div style="background:#0b1422; border-radius:8px; padding:14px; border:1px solid #1e3a5f;">
      <div style="font-size:0.65rem; color:#5a7a9a; text-transform:uppercase; letter-spacing:0.1em;">Pays</div>
      <div style="font-family:'Space Mono',monospace; color:#e2eaf4; margin-top:4px;">{row.get('country','N/A')}</div>
    </div>
  </div>

  <div style="margin-bottom:16px;">
    <div style="font-size:0.65rem; color:#5a7a9a; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;">
      Score de risque — {score:.0%}
    </div>
    {score_bar(score)}
  </div>

  <div style="background:#0b1422; border-radius:8px; padding:14px; border-left:3px solid {'#ff3d71' if suspect else '#00e096'};">
    <div style="font-size:0.65rem; color:#5a7a9a; text-transform:uppercase; letter-spacing:0.1em;">Motif détecté</div>
    <div style="font-family:'Space Mono',monospace; font-size:0.85rem; color:{'#ff8fa3' if suspect else '#00e096'}; margin-top:6px;">
      {row.get('reason','Aucune anomalie détectée')}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Score distribution chart ──────────────────────────────────────────────────
def render_charts(df):
    st.markdown("""
<div class="section-header" style="margin-top:32px;">
  <div class="dot" style="background:#ffaa00; box-shadow:0 0 6px #ffaa00;"></div>
  <h3>Distribution des risques</h3>
</div>""", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        if "fraud_score" in df.columns and not df["fraud_score"].isna().all():
            hist_data = pd.cut(
                df["fraud_score"],
                bins=[0, 0.2, 0.4, 0.5, 0.7, 1.0],
                labels=["0–0.2 ✅", "0.2–0.4 🟡", "0.4–0.5 🟠", "0.5–0.7 🔴", "0.7–1.0 🚨"]
            ).value_counts().sort_index()
            st.bar_chart(hist_data, color="#00e5ff")
            st.caption("Répartition des scores par tranche de risque")

    with col_right:
        if "country" in df.columns:
            country_risk = (
                df.groupby("country")
                .agg(alertes=("is_suspicious", "sum"), total=("is_suspicious", "count"))
                .assign(taux=lambda x: (x["alertes"] / x["total"] * 100).round(1))
                .sort_values("taux", ascending=False)
                .head(8)
                .reset_index()
            )
            if not country_risk.empty:
                st.dataframe(
                    country_risk[["country", "alertes", "total", "taux"]].rename(columns={
                        "country": "Pays", "alertes": "Alertes",
                        "total": "Total", "taux": "Taux %"
                    }),
                    use_container_width=True, hide_index=True
                )
                st.caption("Taux de fraude par pays")


# ── Top risky clients ─────────────────────────────────────────────────────────
def render_top_clients(df):
    st.markdown("""
<div class="section-header" style="margin-top:32px;">
  <div class="dot" style="background:#ff3d71; box-shadow:0 0 6px #ff3d71;"></div>
  <h3>Clients à surveiller</h3>
</div>""", unsafe_allow_html=True)

    if "user_id" not in df.columns:
        return

    top = (
        df[df["is_suspicious"] == True]
        .groupby("user_id")
        .agg(
            alertes=("is_suspicious", "sum"),
            score_max=("fraud_score", "max"),
            montant_total=("amount", "sum")
        )
        .sort_values("alertes", ascending=False)
        .head(10)
        .reset_index()
    )
    if top.empty:
        st.success("🎉 Aucun client à risque détecté dans ce lot.")
        return

    top.columns = ["Client ID", "Nb Alertes", "Score Max", "Montant Total (€)"]
    top["Score Max"] = top["Score Max"].map("{:.2f}".format)
    top["Montant Total (€)"] = top["Montant Total (€)"].map("{:.2f}".format)

    st.dataframe(top, use_container_width=True, hide_index=True)


# ── How it works expander ─────────────────────────────────────────────────────
def render_explainer():
    with st.expander("💡 Comment fonctionne le moteur IA ?", expanded=False):
        st.markdown("""
<div style="font-family:'Syne',sans-serif; line-height:1.8;">

**3 niveaux d'analyse, combinés en un score 0→1 :**

| Niveau | Signal | Impact |
|--------|--------|--------|
| 🔴 **Fondamentaux** | Montant ≤ 0, champs manquants, doublon d'ID | +0.3 à +0.7 |
| 🟠 **Comportemental** | Montant × 10 vs moyenne client, rafale > 3 tx/5min | +0.4 à +0.5 |
| 🟡 **Géographique** | Deux pays différents en < 60 minutes | +0.6 |
| ⚠️ **E-commerce** | Pas de carte physique + montant > 500€ | +0.2 |

**Seuil d'alerte : score ≥ 0.5** → transaction marquée suspecte 🔴

</div>
""", unsafe_allow_html=True)


# ── Main render ───────────────────────────────────────────────────────────────
def render_interface(transactions, results):
    df_tx = pd.DataFrame(transactions)
    df_res = pd.DataFrame(results)
    df = df_tx.merge(df_res, on="transaction_id", how="left")

    total = len(df)
    nb_suspects = int(df["is_suspicious"].sum())
    nb_ok = total - nb_suspects
    pct_fraude = round(nb_suspects / total * 100, 1) if total else 0

    render_kpis(total, nb_suspects, nb_ok, pct_fraude)
    render_explainer()

    st.markdown("""
<div class="section-header" style="margin-top:32px;">
  <div class="dot" style="background:#00e5ff; box-shadow:0 0 6px #00e5ff;"></div>
  <h3>Filtres</h3>
</div>""", unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        filtre_statut = st.selectbox("Statut", ["Toutes", "🔴 Suspectes", "🟢 Validées"])
    with fc2:
        pays_dispo = ["Tous"] + sorted(df["country"].dropna().unique().tolist())
        filtre_pays = st.selectbox("Pays", pays_dispo)
    with fc3:
        clients_dispo = ["Tous"] + sorted(df["user_id"].dropna().unique().tolist())
        filtre_client = st.selectbox("Client", clients_dispo)

    df_f = df.copy()
    if filtre_statut == "🔴 Suspectes":
        df_f = df_f[df_f["is_suspicious"] == True]
    elif filtre_statut == "🟢 Validées":
        df_f = df_f[df_f["is_suspicious"] == False]
    if filtre_pays != "Tous":
        df_f = df_f[df_f["country"] == filtre_pays]
    if filtre_client != "Tous":
        df_f = df_f[df_f["user_id"] == filtre_client]

    render_table(df_f)
    render_detail(df_f)
    render_charts(df)
    render_top_clients(df)

    st.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="Fraud Sentinel — INTELO2026",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("""
<div style="padding:16px 0 8px 0;">
  <div style="font-family:'Space Mono',monospace; font-size:0.65rem;
              color:#5a7a9a; letter-spacing:0.15em; text-transform:uppercase;">
    ▸ FRAUD SENTINEL v2.0
  </div>
  <div style="width:40px; height:1px; background:#1e3a5f; margin-top:8px;"></div>
</div>
""", unsafe_allow_html=True)

        st.markdown("**📂 Source de données**")
        use_sample = st.toggle("Fichier d'exemple", value=True)

        transactions = []
        if use_sample:
            if SAMPLE_CSV.exists():
                transactions = load_transactions(str(SAMPLE_CSV))
                st.success(f"✔ {len(transactions)} transactions chargées")
            else:
                st.warning("Fichier d'exemple introuvable.")
        else:
            uploaded = st.file_uploader("Importer un CSV", type=["csv"])
            if uploaded:
                tmp = Path(".streamlit_upload.csv")
                tmp.write_bytes(uploaded.getvalue())
                transactions = load_transactions(str(tmp))
                tmp.unlink(missing_ok=True)
                st.success(f"✔ {len(transactions)} transactions importées")

        st.divider()
        st.markdown("""
<div style="font-size:0.75rem; color:#5a7a9a; line-height:1.6;">
  <strong style="color:#00e5ff;">Jury INTELO2026</strong><br>
  Évaluez l'ergonomie, la clarté et l'innovation de cette interface.
</div>
""", unsafe_allow_html=True)

    render_hero()

    if not transactions:
        st.markdown("""
<div style="text-align:center; padding:80px 0; color:#5a7a9a;">
  <div style="font-size:3rem; margin-bottom:16px;">🛡️</div>
  <div style="font-family:'Space Mono',monospace; font-size:0.9rem;">
    Chargez des transactions dans la barre latérale
  </div>
</div>
""", unsafe_allow_html=True)
        return

    if st.button("🔍 LANCER L'ANALYSE", type="primary", use_container_width=False):
        with st.spinner("Analyse IA en cours..."):
            try:
                results = detect_fraud(transactions)
            except NotImplementedError:
                st.error("Implémentez d'abord `detect_fraud` dans `fraud_detection.py`.")
                return
            except Exception as exc:
                st.error(f"Erreur : {exc}")
                return
        st.session_state["results"] = results
        st.session_state["transactions"] = transactions
        st.success(f"✔ Analyse terminée — {len(results)} transactions traitées")

    if "results" in st.session_state:
        render_interface(
            st.session_state["transactions"],
            st.session_state["results"],
        )


if __name__ == "__main__":
    main()