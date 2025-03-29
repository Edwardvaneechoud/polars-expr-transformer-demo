import streamlit as st


def show_readme_page():
    """Show the README page with project overview"""
    st.header("About Polars Expression Transformer")

    # README content
    st.markdown("""
    An interactive Streamlit application for exploring and working with Polars Expression Transformer, making data transformation in Polars more accessible and visual.

    ## Features

    * **Data Transformer**: Apply expressions to real data and see results instantly
    * **Documentation**: Comprehensive guide to expression syntax and usage
    * **Examples**: Learn from practical examples across different types of operations
    * **Functions Overview**: Browse all available functions in the library
    * **Tree Visualizer**: See how expressions are parsed into execution trees

    ## About Polars Expression Transformer

    [Polars Expression Transformer](https://github.com/edwardvaneechoud/polars_expr_transformer) is a powerful library that allows you to write simple string expressions that get converted into optimized [Polars](https://pola.rs/) operations. It's ideal for:

    * Users coming from SQL or spreadsheet backgrounds
    * Creating dynamic data transformations
    * Simplifying complex Polars expressions

    ## Contributing

    Contributions are welcome! Please feel free to submit a Pull Request.

    ## Contact

    """)

    # Add GitHub button
    st.markdown("""
    <a href="https://github.com/edwardvaneechoud/polars-expr-transformer-demo" target="_blank" style="text-decoration: none;">
        <div style="
            display: inline-flex;
            align-items: center;
            background-color: #24292e;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 600;
            margin-top: 1rem;
        ">
            <svg style="margin-right: 0.5rem;" height="20" width="20" viewBox="0 0 16 16" fill="currentColor">
                <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
            </svg>
            View on GitHub
        </div>
    </a>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    # This allows running this page directly for development
    st.set_page_config(page_title="README", layout="wide")
    show_readme_page()