import streamlit as st

from streamlit_pages.data_transform import show_data_transform_page
from streamlit_pages.documentation import show_docs_page
from streamlit_pages.function_overview import show_functions_overview_page
from streamlit_pages.examples import show_examples_page
from streamlit_pages.tree_visualizer import show_tree_visualizer_page
from streamlit_pages.readme import show_readme_page

# Set page configuration
st.set_page_config(
    page_title="Polars Expression Transformer Demo",
    page_icon="🐻‍❄️",
    layout="wide"
)

# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Readme",
    "Data Transformer",
    "Documentation",
    "Examples",
    "Functions Overview",
    "Tree visualizer",
])

with tab1:
    show_readme_page()

with tab2:
    show_data_transform_page()

with tab3:
    show_docs_page()

with tab4:
    show_examples_page()

with tab5:
    show_functions_overview_page()

with tab6:
    show_tree_visualizer_page()

# Apply custom CSS for rounded image and sidebar styling
st.markdown("""
<style>
    .rounded-image {
        border-radius: 50%;
        width: 80px;
        height: 80px;
        object-fit: cover;
        display: inline-block;
        vertical-align: middle;
        margin-right: 10px;
    }

    .author-section {
        display: flex;
        align-items: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .github-link {
        display: inline-block;
        margin-top: 15px;
        padding: 8px 12px;
        background-color: #f0f2f6;
        border-radius: 5px;
        text-decoration: none;
        color: #0e1117;
        font-weight: bold;
    }

    .github-link:hover {
        background-color: #e0e2e6;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with project info
st.sidebar.title("Polars Expression Transformer")

# Project description
st.sidebar.info("""
A Python library that provides a simple way to transform and manipulate data using Polars expressions.

Designed for users familiar with SQL or Tableau who want to leverage the power of Polars for data processing tasks.
""")

# GitHub repository link
st.sidebar.markdown(
    "<a href='https://github.com/edwardvaneechoud/polars_expr_transformer' class='github-link'>View on GitHub</a>",
    unsafe_allow_html=True
)

# Add author section with avatar
st.sidebar.markdown("### Created by")
st.sidebar.markdown(
    f"""
    <div class="author-section">
        <img src="https://avatars.githubusercontent.com/u/41021650?s=400&u=a45869f01c5ef2059669b853bdea8803f876bedd&v=4" 
        class="rounded-image">
        <span><strong>Edward van Eechoud</strong></span>
    </div>
    """,
    unsafe_allow_html=True
)