import streamlit as st
import polars as pl
import os
import pandas as pd
from polars_expr_transformer.process.polars_expr_transformer import simple_function_to_expr, build_func


def load_sample_data():
    """Load sample data from CSV or create a sample DataFrame if the file doesn't exist"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    file_path = os.path.join(data_dir, 'sample_data.csv')

    try:
        if os.path.exists(file_path):
            df = pl.read_csv(file_path)
            # Convert directly to pandas for safer Streamlit handling
            return df
        else:
            # Create a sample DataFrame if the file doesn't exist
            df = pl.DataFrame({
                "customer_id": [1001, 1002, 1003, 1004, 1005],
                "customer_name": ["John Smith", "Jane Doe", "Robert Johnson", "Maria Garcia", "Wei Zhang"],
                "age": [34, 42, 28, 55, 39],
                "city": ["New York", "San Francisco", "Chicago", "Boston", "Seattle"],
                "purchase_amount": [125.50, 245.30, 89.99, 342.15, 127.45],
                "purchase_date": ["2023-01-15", "2023-01-20", "2023-02-05", "2023-02-12", "2023-03-01"],
                "is_member": [True, False, True, True, False]
            })
            return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pl.DataFrame()


def show_data_transform_page():
    """Show the data transformation page"""
    st.header("Data Transformer")
    st.write("Apply Polars Expression Transformer to real-world data.")

    # Load the data - store both Polars and Pandas versions
    if 'df_original_polars' not in st.session_state:
        st.session_state.df_original_polars = load_sample_data()
        # Keep a pandas copy for display
        st.session_state.df_original_pandas = st.session_state.df_original_polars.to_pandas()

    # Use session state to keep track of the DataFrame
    if 'df_transformed_polars' not in st.session_state:
        st.session_state.df_transformed_polars = st.session_state.df_original_polars.clone()
        st.session_state.df_transformed_pandas = st.session_state.df_transformed_polars.to_pandas()

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
            # Create a fresh clone of the DataFrame to avoid mutable borrowing issues
            df_clone = st.session_state.df_transformed_polars.clone()

            # Apply the expression and add as a new column
            expr_obj = simple_function_to_expr(expression)
            result_polars = df_clone.with_columns(expr_obj.alias(col_name))

            # Get the Polars code for display
            func_obj = build_func(expression)
            func_obj.get_pl_func()  # Validate the expression
            polars_expr = func_obj.get_readable_pl_function()

            # Update both the Polars and Pandas versions
            st.session_state.df_transformed_polars = result_polars
            st.session_state.df_transformed_pandas = result_polars.to_pandas()

            # Show the equivalent Polars code
            st.code(
                "#Polars code \nexpression = " + polars_expr + "\ndf.with_columns(expression.alias('" + col_name + "'))",
                language="python")

        except Exception as e:
            st.error(f"Error applying expression: {str(e)}")

    # Display the current data using Pandas DataFrame (safer for Streamlit)
    st.dataframe(st.session_state.df_transformed_pandas)

    # Reset button
    if st.button("Reset Data"):
        # Make a fresh clone from the original data
        st.session_state.df_transformed_polars = st.session_state.df_original_polars.clone()
        st.session_state.df_transformed_pandas = st.session_state.df_transformed_polars.to_pandas()
        st.experimental_rerun()  # Use experimental_rerun for more consistent behavior


def initialize_session_state():
    """Initialize the session state variables if they don't exist"""
    if 'df_original_polars' not in st.session_state:
        st.session_state.df_original_polars = None
    if 'df_original_pandas' not in st.session_state:
        st.session_state.df_original_pandas = None
    if 'df_transformed_polars' not in st.session_state:
        st.session_state.df_transformed_polars = None
    if 'df_transformed_pandas' not in st.session_state:
        st.session_state.df_transformed_pandas = None


if __name__ == "__main__":
    # This allows running this page directly for development
    st.set_page_config(page_title="Data Transformer", layout="wide")
    initialize_session_state()
    show_data_transform_page()