import streamlit as st

def show_reports():
    """Exibe os relatórios em formato Markdown."""
    report_files = {
        "BFS Report": "reports/bfs_report.md",
        "A* Report": "reports/a_star_report.md",
        "Fuzzy Report": "reports/fuzzy_report.md"
    }

    selected_report = st.selectbox("Select Report", list(report_files.keys()))

    with open(report_files[selected_report], "r") as f:
        report_content = f.read()
        st.markdown(report_content, unsafe_allow_html=True)