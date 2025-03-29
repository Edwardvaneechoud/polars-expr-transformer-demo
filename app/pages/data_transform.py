import streamlit as st
import polars as pl
import os
from polars_expr_transformer.process.polars_expr_transformer import simple_function_to_expr, build_func


def load_sample_data():
    """Load sample data from CSV or create a sample DataFrame if the file doesn't exist"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    file_path = os.path.join(data_dir, 'sample_data.csv')

    try:
        if os.path.exists(file_path):
            return pl.read_csv(file_path)
        else:
            # Create a sample DataFrame if the file doesn't exist
            return pl.DataFrame({
                "customer_id": [1001, 1002, 1003, 1004, 1005],
                "customer_name": ["John Smith", "Jane Doe", "Robert Johnson", "Maria Garcia", "Wei Zhang"],
                "age": [34, 42, 28, 55, 39],
                "city": ["New York", "San Francisco", "Chicago", "Boston", "Seattle"],
                "purchase_amount": [125.50, 245.30, 89.99, 342.15, 127.45],
                "purchase_date": ["2023-01-15", "2023-01-20", "2023-02-05", "2023-02-12", "2023-03-01"],
                "is_member": [True, False, True, True, False]
            })
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pl.DataFrame()


def show_data_transform_page():
    """Show the data transformation page"""
    st.header("Data Transformer")
    st.write("Apply Polars Expression Transformer to real-world data.")

    # Load the data
    df = load_sample_data()

    # Use session state to keep track of the DataFrame
    if 'df_transformed' not in st.session_state:
        st.session_state.df_transformed = df

    # Simple expression input
    col1, col2 = st.columns([3, 1])

    with col1:
        expression = st.text_input(
            "Expression",
            value='concat([customer_name], " from ", [city])',
            help="Enter a Polars Expression Transformer expression. Use [column_name] for columns."
        )

    with col2:
        col_name = st.text_input(
            "Output Column",
            value="result",
            help="Name for the output column"
        )

    # Calculate button
    if st.button("Calculate", key="calculate_btn"):
        try:
            # Apply the expression and add as a new column
            result = st.session_state.df_transformed.with_columns(
                simple_function_to_expr(expression).alias(col_name)
            )
            f = build_func(expression)
            f.get_pl_func()
            polars_expr = build_func(expression).get_readable_pl_function()
            st.session_state.df_transformed = result
            st.code("#Polars code \nexpression = "+polars_expr + "\ndf.with_columns(expression)", language="python")

        except Exception as e:
            st.error(f"Error applying expression: {e}")

    # Display the current data - moved after the button logic
    st.dataframe(st.session_state.df_transformed)

    # Reset button
    if st.button("Reset Data"):
        st.session_state.df_transformed = df
        st.rerun()  # Use st.rerun() consistently


if __name__ == "__main__":
    # This allows running this page directly for development
    st.set_page_config(page_title="Data Transformer", layout="wide")
    show_data_transform_page()