"""
5_Executive_Briefing.py
Displays the latest GenAI-generated executive briefing, with a
button to generate a fresh one on demand.
"""

import sys
import os
import glob
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "genai"))

st.set_page_config(page_title="Executive Briefing", layout="wide")
st.title("📋 Executive Briefing")

reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "..", "reports")
briefing_files = sorted(glob.glob(os.path.join(reports_dir, "executive_briefing_*.md")), reverse=True)

if st.button("🔄 Generate New Briefing"):
    with st.spinner("Aggregating data and calling the model..."):
        from generate_briefing import generate_briefing, save_briefing
        briefing_text, _ = generate_briefing()
        save_briefing(briefing_text)
    st.success("New briefing generated!")
    st.rerun()

st.divider()

if briefing_files:
    latest = briefing_files[0]
    st.caption(f"Showing: {os.path.basename(latest)}")
    with open(latest, "r", encoding="utf-8") as f:
        st.markdown(f.read())
else:
    st.info("No briefing generated yet. Click the button above to create one.")

if len(briefing_files) > 1:
    st.divider()
    with st.expander(f"View {len(briefing_files) - 1} older briefing(s)"):
        for filepath in briefing_files[1:]:
            st.caption(os.path.basename(filepath))
            with open(filepath, "r", encoding="utf-8") as f:
                st.markdown(f.read())
            st.divider()