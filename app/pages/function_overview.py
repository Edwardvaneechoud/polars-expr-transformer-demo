import streamlit as st
from polars_expr_transformer import get_expression_overview


def show_functions_overview_page():
    """Show the functions overview page with all available functions from Polars Expression Transformer"""
    st.header("Functions Overview")
    st.write("Browse all available functions in Polars Expression Transformer.")

    # Get the expression overview data directly from the library
    expressions_overview = [c for c in get_expression_overview() if len(c.expressions) > 0]

    # Display categories in tabs
    categories = [overview.expression_type.title() for overview in expressions_overview]
    category_tabs = st.tabs(categories)
    for i, tab in enumerate(category_tabs):
        with tab:
            category = expressions_overview[i]

            st.write(f"**{len(category.expressions)} functions available**")

            for expr in category.expressions:
                with st.expander(expr.name):
                    st.markdown(f"**Function:** `{expr.name}`")

                    if expr.doc:
                        st.markdown(f"**Description:**\n{expr.doc.strip()}")
                    else:
                        st.markdown("*No description available*")


if __name__ == "__main__":
    # This allows running this page directly for development
    st.set_page_config(page_title="Functions Overview", layout="wide")
    show_functions_overview_page()