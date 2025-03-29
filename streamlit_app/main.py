import streamlit as st

from streamlit_pages.data_transform import show_data_transform_page
from streamlit_pages.documentation import show_docs_page
from streamlit_pages.function_overview import show_functions_overview_page
from streamlit_pages.examples import show_examples_page
from streamlit_pages.tree_visualizer import show_tree_visualizer_page

# Set page configuration
st.set_page_config(
    page_title="Polars Expression Transformer Demo",
    page_icon="🐻‍❄️",
    layout="wide"
)

# Main title
st.title("Polars Expression Transformer Demo")
st.write("An interactive demo of the Polars Expression Transformer library")

# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Data Transformer",
    "Documentation",
    "Examples",
    "Functions Overview",
    "Tree visualizer",
])

# Content for each tab
with tab1:
    show_data_transform_page()

with tab2:
    show_docs_page()

with tab3:
    show_examples_page()

with tab4:
    show_functions_overview_page()

with tab5:
    show_tree_visualizer_page()

# Sidebar with general info
st.sidebar.title("About")
st.sidebar.info("""
## Polars Expression Transformer

Polars Expression Transformer is a Python library that provides a simple way to transform and manipulate data using Polars expressions.

It is designed for users who are familiar with SQL or Tableau and want to leverage the power of Polars for data processing tasks.

### [View on GitHub](https://github.com/edwardvaneechoud/polars-expr-transformer)
""")