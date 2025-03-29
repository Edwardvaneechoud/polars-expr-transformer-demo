import streamlit as st
from pages import data_transform, documentation, function_overview, examples, tree_visualizer

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
    data_transform.show_data_transform_page()

with tab2:
    documentation.show_docs_page()
#
with tab3:
    examples.show_examples_page()
#
with tab4:
    function_overview.show_functions_overview_page()

with tab5:
    tree_visualizer.show_tree_visualizer_page()

# Sidebar with general info
st.sidebar.title("About")
st.sidebar.info("""
## Polars Expression Transformer

Polars Expression Transformer is a Python library that provides a simple way to transform and manipulate data using Polars expressions.

It is designed for users who are familiar with SQL or Tableau and want to leverage the power of Polars for data processing tasks.

### [View on GitHub](https://github.com/yourusername/polars-expr-transformer)
""")