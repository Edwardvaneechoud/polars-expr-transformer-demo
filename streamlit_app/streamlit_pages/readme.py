import streamlit as st


def show_readme_page():
    """Show the README page with project overview"""

    # Add Flowfile branding at the top
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #00CED1 0%, #6B46C1 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h1 style="color: white; margin: 0; font-size: 2.5rem;">Flowfile Formula Syntax</h1>
        <p style="color: rgba(255,255,255,0.9); margin-top: 0.5rem; font-size: 1.2rem;">
            Write Excel-like formulas that compile to optimized Polars expressions
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Quick example to immediately show what this is
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📝 Write This")
        st.code("""
[price] * [quantity]
IF([status] = 'active', [amount], 0)
ROUND([value] * 1.1, 2)
        """, language="excel")

    with col2:
        st.markdown("### ⚡ Get This")
        st.code("""
pl.col("price") * pl.col("quantity")
pl.when(pl.col("status") == "active").then(pl.col("amount")).otherwise(0)
pl.col("value").mul(1.1).round(2)
        """, language="python")

    st.markdown("---")

    # About section with Flowfile context
    st.header("🚀 Interactive Flowfile Formula Playground")

    st.markdown("""
    This is the official playground for **Flowfile Formula Syntax** - a powerful feature of [Flowfile](https://github.com/edwardvaneechoud/Flowfile) 
    that lets you write intuitive, Excel-like formulas that automatically compile to optimized Polars expressions.

    ### Why Flowfile Formulas?

    Flowfile bridges the gap between business users familiar with Excel and developers using Polars:
    - **📊 Business Users**: Write formulas just like in Excel or Google Sheets
    - **🐍 Developers**: Get optimized Polars expressions automatically
    - **🔄 Seamless Integration**: Use in both Flowfile's visual editor and Python API
    """)

    # Features section with Flowfile branding
    st.header("✨ Features")

    feature_cols = st.columns(3)

    with feature_cols[0]:
        st.markdown("""
        **🔄 Data Transformer**

        Apply Flowfile formulas to real data and see results instantly
        """)

    with feature_cols[1]:
        st.markdown("""
        **📖 Documentation**

        Complete guide to Flowfile formula syntax and functions
        """)

    with feature_cols[2]:
        st.markdown("""
        **🌳 Tree Visualizer**

        See how formulas parse into Polars execution trees
        """)

    # How it works in Flowfile
    st.header("🔧 How It Works in Flowfile")

    st.markdown("""
    In Flowfile, you can use formula syntax in both the visual editor and Python API:
    """)

    # Show both usage contexts
    tab1, tab2 = st.tabs(["Python API", "Visual Editor"])

    with tab1:
        st.code("""
import flowfile as ff

df = ff.FlowFrame(your_data)

# Use Flowfile formulas instead of Polars expressions
df = df.with_columns(
    flowfile_formulas=[
        "[price] * [quantity]",
        "IF([discount] > 0, [price] * (1 - [discount]), [price])",
        "ROUND([total] / [count], 2)"
    ],
    output_column_names=["revenue", "final_price", "average"]
)

# Or in filters
df = df.filter(flowfile_formula="[status] = 'active' AND [amount] > 1000")
        """, language="python")

    with tab2:
        st.info(
            "In Flowfile's visual editor, formula nodes accept this syntax directly in the formula field - no need to write complex Polars expressions!")

    # Links section
    st.header("🔗 Learn More")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <a href="https://github.com/edwardvaneechoud/Flowfile" target="_blank" style="text-decoration: none;">
            <div style="
                background-color: #00CED1;
                color: white;
                padding: 1rem;
                border-radius: 6px;
                text-align: center;
                font-weight: 600;
                transition: transform 0.2s;
            ">
                📦 Flowfile Repository
            </div>
        </a>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <a href="https://github.com/edwardvaneechoud/polars_expr_transformer" target="_blank" style="text-decoration: none;">
            <div style="
                background-color: #6B46C1;
                color: white;
                padding: 1rem;
                border-radius: 6px;
                text-align: center;
                font-weight: 600;
                transition: transform 0.2s;
            ">
                🔧 Formula Parser Library
            </div>
        </a>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <a href="https://edwardvaneechoud.github.io/Flowfile/for-developers/python-api/expressions.html" target="_blank" style="text-decoration: none;">
            <div style="
                background-color: #24292e;
                color: white;
                padding: 1rem;
                border-radius: 6px;
                text-align: center;
                font-weight: 600;
                transition: transform 0.2s;
            ">
                📚 Documentation
            </div>
        </a>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")


if __name__ == "__main__":
    # This allows running this page directly for development
    st.set_page_config(
        page_title="Flowfile Formula Syntax Playground",
        page_icon="📊",
        layout="wide"
    )
    show_readme_page()