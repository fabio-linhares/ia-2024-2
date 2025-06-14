import streamlit as st
import re
import os

def show_reports():
    """Exibe os relatórios em formato Markdown."""
    report_files = {
        "BFS Report": "reports/bfs_report.md",
        "A* Report": "reports/a_star_report.md",
        "Fuzzy Report": "reports/fuzzy_report.md"
    }

    selected_report = st.selectbox("Select Report", list(report_files.keys()))

    with open(report_files[selected_report], "r", encoding="utf-8") as f:
        report_content = f.read()
        
        # Verificar se há uma seção de notas com a tag details
        details_pattern = re.compile(r'<details>\s*<summary>(.*?)</summary>(.*?)</details>', re.DOTALL)
        details_match = details_pattern.search(report_content)
        
        if details_match:
            # Dividir o conteúdo em partes: antes, durante e depois da seção de notas
            full_match = details_match.group(0)
            summary = details_match.group(1)
            details_content = details_match.group(2)
            
            # Dividir o conteúdo em partes
            parts = report_content.split(full_match)
            before_details = parts[0]
            after_details = parts[1] if len(parts) > 1 else ""
            
            # Renderizar o conteúdo anterior ao expander
            st.markdown(before_details, unsafe_allow_html=True)
            
            # Criar um expander nativo do Streamlit para as notas
            with st.expander(summary):
                st.markdown(details_content, unsafe_allow_html=True)
                
            # Renderizar o conteúdo após o expander
            st.markdown(after_details, unsafe_allow_html=True)
        else:
            # Se não houver seção de notas com tag details, renderizar todo o conteúdo normalmente
            st.markdown(report_content, unsafe_allow_html=True)

def display_report_viewer(report_name):
    """
    Exibe um relatório específico em formato Markdown.
    
    Args:
        report_name: Nome do arquivo de relatório (ex: "dfs_report.md")
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    report_path = os.path.join(base_dir, "reports", report_name)
    
    if not os.path.exists(report_path):
        st.warning(f"Relatório não encontrado: {report_path}")
        return
        
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
            
            # Verificar se há uma seção de notas com a tag details
            details_pattern = re.compile(r'<details>\s*<summary>(.*?)</summary>(.*?)</details>', re.DOTALL)
            details_match = details_pattern.search(report_content)
            
            if details_match:
                # Dividir o conteúdo em partes: antes, durante e depois da seção de notas
                full_match = details_match.group(0)
                summary = details_match.group(1)
                details_content = details_match.group(2)
                
                # Dividir o conteúdo em partes
                parts = report_content.split(full_match)
                before_details = parts[0]
                after_details = parts[1] if len(parts) > 1 else ""
                
                # Renderizar o conteúdo anterior ao expander
                st.markdown(before_details, unsafe_allow_html=True)
                
                # Criar um expander nativo do Streamlit para as notas
                with st.expander(summary):
                    st.markdown(details_content, unsafe_allow_html=True)
                    
                # Renderizar o conteúdo após o expander
                st.markdown(after_details, unsafe_allow_html=True)
            else:
                # Se não houver seção de notas com tag details, renderizar todo o conteúdo normalmente
                st.markdown(report_content, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erro ao carregar o relatório: {str(e)}")