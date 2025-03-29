import polars as pl
from polars_expr_transformer import simple_function_to_expr


tree_visualizer_example_categories = {
    "String Operations": [
        "concat([name], ' from ', [city])",
        "contains([city], 'o')",
        "length([name])",
        "uppercase([name])"
    ],
    "Numeric Operations": [
        "[salary] / 12",
        "round([salary] / 1000, 1)",
        "[age] > 35"
    ],
    "Date Operations": [
        "year(to_date([joined_date]))",
        "date_diff_days(to_date([joined_date]), to_date('2023-01-01'))"
    ],
    "Conditional Logic": [
        "if [age] > 40 then 'Senior' else 'Junior' endif",
        "if [salary] > 100000 then 'High' elseif [salary] > 80000 then 'Medium' else 'Standard' endif",
        "if contains([city], 'o') then length([city]) else 0 endif"
    ],
    "Combined Examples": [
        "concat([city], ': ', if [salary] > 90000 then 'High' else 'Standard' endif)",
        "concat('Joined in ', year(to_date([joined_date])), ', Age: ', [age])"
    ]
}


def create_sample_dataframe():
    """Create a sample DataFrame for demonstration purposes"""
    return pl.DataFrame({
        "name": ["John Smith", "Jane Doe", "Robert Johnson", "Maria Garcia", "Wei Zhang"],
        "age": [34, 42, 28, 55, 39],
        "city": ["New York", "San Francisco", "Chicago", "Boston", "Seattle"],
        "salary": [75000, 95000, 65000, 120000, 85000],
        "joined_date": ["2020-03-15", "2019-07-22", "2021-01-05", "2018-05-30", "2020-11-11"]
    })



def apply_expression_to_dataframe(df, expr):
    """Apply the expression to the DataFrame and return the result"""
    try:
        result = df.select(simple_function_to_expr(expr).alias("result"))
        return result
    except Exception as e:
        st.error(f"Error applying expression: {str(e)}")
        return None
