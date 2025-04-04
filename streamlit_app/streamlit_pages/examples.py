import streamlit as st
import polars as pl
import pandas as pd
from polars_expr_transformer.process.polars_expr_transformer import simple_function_to_expr


def create_sample_dataframe():
    """Create a sample dataframe for examples"""
    sample_data = {
        "name": ["John Smith", "Jane Doe", "Robert Johnson", "Maria Garcia", "Wei Zhang"],
        "age": [34, 42, 28, 55, 39],
        "city": ["New York", "San Francisco", "Chicago", "Boston", "Seattle"],
        "salary": [75000, 95000, 65000, 120000, 85000],
        "joined_date": ["2020-03-15", "2019-07-22", "2021-01-05", "2018-05-30", "2020-11-11"]
    }
    return pl.DataFrame(sample_data)


def show_examples_page():
    """Show the examples page"""
    st.header("Examples")
    st.write("Learn by example how to use Polars Expression Transformer.")

    # Create and store sample dataframe in session state for persistence
    if 'example_df_polars' not in st.session_state:
        st.session_state.example_df_polars = create_sample_dataframe()
        # Create a pandas version for display
        st.session_state.example_df_pandas = st.session_state.example_df_polars.to_pandas()

    # Show the sample dataframe (using the pandas version for safety)
    st.subheader("Sample DataFrame")
    st.dataframe(st.session_state.example_df_pandas)

    # Create tabs for different example categories
    example_tabs = st.tabs([
        "String Operations",
        "Numeric Operations",
        "Date Operations",
        "Conditional Logic",
        "Combined Examples"
    ])

    # String Operations examples
    with example_tabs[0]:
        st.subheader("String Operations")

        string_examples = {
            "Concatenation": {
                "expr": "concat([name], ' lives in ', [city])",
                "desc": "Combine text from multiple columns"
            },
            "Uppercase": {
                "expr": "uppercase([name])",
                "desc": "Convert text to uppercase"
            },
            "String Contains": {
                "expr": "contains([city], 'o')",
                "desc": "Check if a string contains a specific character or substring"
            },
            "String Length": {
                "expr": "length([name])",
                "desc": "Count the number of characters in a string"
            },
            "String Replacement": {
                "expr": "replace([city], ' ', '-')",
                "desc": "Replace characters in a string"
            }
        }

        display_examples(string_examples)

    # Numeric Operations examples
    with example_tabs[1]:
        st.subheader("Numeric Operations")

        numeric_examples = {
            "Basic Arithmetic": {
                "expr": "[salary] / 12",
                "desc": "Calculate monthly salary"
            },
            "Rounding": {
                "expr": "round([salary] / 1000, 1)",
                "desc": "Round to 1 decimal place (salary in thousands)"
            },
            "Percentage": {
                "expr": "[age] / 100 * 100",
                "desc": "Express age as a percentage"
            },
            "Math Functions": {
                "expr": "sqrt([age])",
                "desc": "Square root function"
            },
            "Comparisons": {
                "expr": "[salary] > 80000",
                "desc": "Boolean comparison"
            }
        }

        display_examples(numeric_examples)

    # Date Operations examples
    with example_tabs[2]:
        st.subheader("Date Operations")

        date_examples = {
            "Extract Year": {
                "expr": "year(to_date([joined_date]))",
                "desc": "Get the year from a date"
            },
            "Extract Month": {
                "expr": "month(to_date([joined_date]))",
                "desc": "Get the month from a date"
            },
            "Date Difference": {
                "expr": "date_diff_days(to_date([joined_date]), to_date('2023-01-01'))",
                "desc": "Calculate days between dates"
            },
            "Add Days": {
                "expr": "add_days(to_date([joined_date]), 30)",
                "desc": "Add 30 days to a date"
            }
        }

        display_examples(date_examples)

    # Conditional Logic examples
    with example_tabs[3]:
        st.subheader("Conditional Logic")

        conditional_examples = {
            "Simple If-Then-Else": {
                "expr": "if [age] > 40 then 'Senior' else 'Junior' endif",
                "desc": "Basic conditional logic"
            },
            "Multiple Conditions": {
                "expr": "if [salary] > 100000 then 'High' elseif [salary] > 80000 then 'Medium' else 'Standard' endif",
                "desc": "Multiple conditions with elseif"
            },
            "Conditional with Functions": {
                "expr": "if contains([city], 'o') then length([city]) else 0 endif",
                "desc": "Combining conditionals with other functions"
            },
            "Boolean Logic": {
                "expr": "[age] > 30 and [salary] < 90000",
                "desc": "Using AND logic"
            }
        }

        display_examples(conditional_examples)

    # Combined examples
    with example_tabs[4]:
        st.subheader("Combined Examples")

        combined_examples = {
            "Salary Category by City": {
                "expr": "concat([city], ': ', if [salary] > 90000 then 'High' else 'Standard' endif)",
                "desc": "Combine string concatenation with conditionals"
            },
            "Tenure and Experience": {
                "expr": "concat('Joined in ', year(to_date([joined_date])), ', Experience: ', 2023 - year(to_date([joined_date])), ' years')",
                "desc": "Combine date functions with arithmetic and concatenation"
            },
            "Salary Range Check": {
                "expr": "[name] + ' - ' + if [salary] < 70000 then 'Range 1' elseif [salary] < 90000 then 'Range 2' else 'Range 3' endif",
                "desc": "Combine string operations with complex conditionals"
            }
        }

        display_examples(combined_examples)


def display_examples(examples):
    """Helper function to display examples with try buttons"""
    for title, example in examples.items():
        with st.expander(title, expanded=False):
            st.write(example["desc"])
            st.code(example["expr"], language="python")

            if st.button(f"Try it", key=f"try_{title}"):
                try:
                    # Create a new clone of the DataFrame for each operation
                    df_clone = st.session_state.example_df_polars.clone()

                    # Apply the expression
                    expr_obj = simple_function_to_expr(example["expr"])
                    result_polars = df_clone.select(expr_obj.alias("result"))

                    # Convert to pandas for display
                    result_pandas = result_polars.to_pandas()

                    st.success("Example successfully applied!")
                    st.dataframe(result_pandas)
                except Exception as e:
                    st.error(f"Error: {str(e)}")


def initialize_session_state():
    """Initialize the session state variables if they don't exist"""
    if 'example_df_polars' not in st.session_state:
        st.session_state.example_df_polars = None
    if 'example_df_pandas' not in st.session_state:
        st.session_state.example_df_pandas = None


if __name__ == "__main__":
    # This allows running this page directly for development
    st.set_page_config(page_title="Examples", layout="wide")
    initialize_session_state()
    show_examples_page()