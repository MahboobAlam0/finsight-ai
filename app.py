import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="FinSight AI", layout="wide", page_icon="📈")
st.title("FinSight AI: Narrative Intelligence System")

with st.sidebar:
    company = st.text_input("Company", "Tesla")
    num_articles = st.slider("Articles", 3, 15, 8)
    run = st.button("Run Analysis")

if run:
    with st.spinner("Fetching & analyzing news..."):
        scrape_data = requests.post(
            f"{API_URL}/scrape",
            json={"company": company, "num_articles": num_articles},
            timeout=120
        ).json()
        articles = scrape_data.get("articles", [])

        analyze_data = requests.post(
            f"{API_URL}/analyze",
            json={"articles": articles},
            timeout=120
        ).json()
        articles = analyze_data.get("articles", [])

        st.session_state.articles = articles

if "articles" in st.session_state:
    articles = st.session_state.articles

    tab1, tab2, tab3, tab4 = st.tabs([
        "Structured Report",
        "Sentiment Overview",
        "AI Insight Agent",
        "Raw Data"
    ])

    with tab1:
        for idx, a in enumerate(articles):
            with st.expander(a["title"]):
                st.write(a["summary"])
                st.caption(f"{a['sentiment']} | {a['source']}")
                
                # TTS Button
                if st.button("Listen (Hindi) 🎧", key=f"tts_{idx}"):
                    with st.spinner("Translating & Generating Audio..."):
                        try:
                            resp = requests.post(f"{API_URL}/tts", json={"text": a["summary"]}, timeout=60)
                            if resp.status_code == 200:
                                st.audio(resp.json()["audio_path"])
                            else:
                                st.error("Audio generation failed")
                        except Exception as e:
                            st.error(f"Error: {e}")

    with tab2:
        df = pd.DataFrame(
            [a["sentiment"] for a in articles],
            columns=["Sentiment"]
        )
        fig = px.histogram(df, x="Sentiment")
        st.plotly_chart(fig, width="stretch")

    with tab3:
        if st.button("Run AI Insight Agent"):
            resp = requests.post(
                f"{API_URL}/analyze_llm",
                json=articles,
                timeout=180
            ).json()

            analysis = resp.get("analysis", {})
            st.subheader("Business Takeaway")
            st.success(analysis.get("business_takeaway", "N/A"))

            st.subheader("Risks")
            for r in analysis.get("risk_signals", []):
                st.warning(r)

    with tab4:
        st.json(articles)