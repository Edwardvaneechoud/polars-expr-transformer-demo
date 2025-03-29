import streamlit as st


def show_docs_page():
    """Show the documentation page with syntax and usage patterns"""
    st.header("Polars Expression Transformer Syntax Guide")
    st.write(
        "Learn how to write expressions with Polars Expression Transformer. For a complete list of available functions, see the Functions Overview tab.")

    # Create tabs for different documentation sections
    doc_tabs = st.tabs([
        "Basic Syntax",
        "Column References",
        "Conditional Logic",
        "Expression Examples",
        "Best Practices"
    ])

    # Basic Syntax
    with doc_tabs[0]:
        st.subheader("Basic Syntax")

        st.markdown("""
        ## Introduction

        Polars Expression Transformer allows you to write expressions as strings that will be converted to Polars expressions.
        This makes it easy to perform complex data transformations without having to write Python code.

        ## Expression Structure

        A basic expression follows this pattern:

        ```
        function_name(parameter1, parameter2, ...)
        ```

        For example:
        ```
        concat([first_name], " ", [last_name])
        ```

        ## Operators

        You can use common operators in your expressions:

        | Operator | Description | Example |
        | --- | --- | --- |
        | `+` | Addition or concatenation | `[value1] + [value2]` or `"Hello " + "World"` |
        | `-` | Subtraction | `[price] - [discount]` |
        | `*` | Multiplication | `[quantity] * [price]` |
        | `/` | Division | `[total] / [count]` |
        | `and` | Logical AND | `[age] > 18 and [subscribed] == true` |
        | `or` | Logical OR | `[status] == "active" or [status] == "pending"` |
        | `==` | Equality | `[status] == "active"` |
        | `!=` | Inequality | `[status] != "inactive"` |
        | `<` | Less than | `[value] < 100` |
        | `>` | Greater than | `[age] > 18` |
        | `<=` | Less than or equal | `[quantity] <= 0` |
        | `>=` | Greater than or equal | `[rating] >= 4.5` |

        ## Comments

        You can add comments to your expressions using `//`. Everything after `//` on a line is ignored.

        ```
        [price] * 0.9  // Apply 10% discount
        ```
        """)

    # Column References
    with doc_tabs[1]:
        st.subheader("Column References")

        st.markdown("""
        ## Referencing Columns

        To reference a column in your DataFrame, use square brackets around the column name:

        ```
        [column_name]
        ```

        For example, if your DataFrame has columns named "age", "name", and "city", you can reference them as:

        ```
        [age]
        [name]
        [city]
        ```

        ## Column Names with Special Characters

        If a column name contains spaces or special characters, you can still reference it using square brackets:

        ```
        [First Name]
        [Order #]
        [Price ($)]
        [Column.with.dots]
        [Column-with-dashes]
        ```

        ## Using Column References in Expressions

        Column references can be used anywhere in your expressions:

        ```
        // Arithmetic operations
        [price] * [quantity]

        // String operations
        concat([first_name], " ", [last_name])

        // Conditions
        [age] >= 18

        // Multiple columns
        [revenue] - [cost]
        ```

        ## Dynamic Column References

        You can use the same column multiple times in an expression:

        ```
        // Calculate a discount based on quantity
        [price] - ([price] * 0.1 * [quantity])
        ```
        """)

    # Conditional Logic
    with doc_tabs[2]:
        st.subheader("Conditional Logic")

        st.markdown("""
        ## If-Then-Else Statements

        You can use conditional logic with `if`, `then`, `else`, and `endif` keywords:

        ```
        if [condition] then [value_if_true] else [value_if_false] endif
        ```

        For example:

        ```
        if [age] >= 18 then "Adult" else "Minor" endif
        ```

        ## Multiple Conditions with Elseif

        For more complex conditions, you can use `elseif`:

        ```
        if [condition1] then
            [value1]
        elseif [condition2] then
            [value2]
        elseif [condition3] then
            [value3]
        else
            [default_value]
        endif
        ```

        For example:

        ```
        if [score] >= 90 then
            "A"
        elseif [score] >= 80 then
            "B"
        elseif [score] >= 70 then
            "C"
        elseif [score] >= 60 then
            "D"
        else
            "F"
        endif
        ```

        ## Nested Conditions

        You can nest conditional statements:

        ```
        if [outer_condition] then
            if [inner_condition] then
                [value1]
            else
                [value2]
            endif
        else
            [value3]
        endif
        ```

        ## Combining Conditions

        Use `and` and `or` to combine conditions:

        ```
        if [age] >= 18 and [has_id] == true then
            "Can enter"
        else
            "Cannot enter"
        endif
        ```

        ```
        if [status] == "gold" or [lifetime_value] > 1000 then
            "Premium"
        else
            "Standard"
        endif
        ```
        """)

    # Expression Examples
    with doc_tabs[3]:
        st.subheader("Expression Examples")

        st.markdown("""
        ## Common Expression Patterns

        ### String Formatting

        ```
        // Combine first and last name
        concat([first_name], " ", [last_name])

        // Create a formatted address
        concat([street], ", ", [city], ", ", [state], " ", [zip])

        // Create a greeting
        concat("Hello, ", [name], "! Your order #", to_string([order_id]), " has shipped.")
        ```

        ### Numeric Calculations

        ```
        // Calculate total price
        [quantity] * [price]

        // Calculate discount
        [price] * (1 - [discount_percentage] / 100)

        // Calculate profit margin
        ([revenue] - [cost]) / [revenue] * 100

        // Apply tiered pricing
        if [quantity] > 100 then
            [quantity] * [price] * 0.8  // 20% bulk discount
        elseif [quantity] > 50 then
            [quantity] * [price] * 0.9  // 10% discount
        else
            [quantity] * [price]  // Regular price
        endif
        ```

        ### Classification

        ```
        // Age groups
        if [age] < 18 then
            "Minor"
        elseif [age] < 65 then
            "Adult"
        else
            "Senior"
        endif

        // Customer segments based on purchase frequency and amount
        if [purchase_frequency] > 10 and [average_purchase] > 100 then
            "VIP"
        elseif [purchase_frequency] > 5 or [average_purchase] > 100 then
            "Premium"
        else
            "Standard"
        endif
        ```

        ### Date Formatting and Calculations

        ```
        // Format date as Month Day, Year
        concat(to_string(month(to_date([purchase_date]))), " ", to_string(day(to_date([purchase_date]))), ", ", to_string(year(to_date([purchase_date]))))
        // Calculate days since purchase
        date_diff_days(today(), to_date([purchase_date]))

        // Calculate age from birth date
        year(today()) - year(to_date([birth_date]))
        ```
        """)

    # Best Practices
    with doc_tabs[4]:
        st.subheader("Best Practices")

        st.markdown("""
        ## Tips for Writing Expressions

        ### 1. Use Parentheses for Clarity

        Even when not strictly required, parentheses can make your expressions easier to read and understand:

        ```
        // Less clear
        [price] * [quantity] + [shipping]

        // More clear
        ([price] * [quantity]) + [shipping]
        ```

        ### 2. Break Complex Expressions into Smaller Parts

        Instead of creating one complex expression, you can often create multiple simpler expressions and combine them:

        1. First, calculate the subtotal: `[price] * [quantity]`
        2. Then, calculate the tax: `subtotal * 0.07`
        3. Finally, calculate the total: `subtotal + tax`

        ### 3. Add Comments for Clarity

        Use comments to explain complex logic:

        ```
        if [days_since_purchase] <= 30 then
            "Recent"  // Within last 30 days
        elseif [days_since_purchase] <= 90 then
            "Medium"  // 1-3 months ago
        else
            "Old"  // More than 3 months ago
        endif
        ```

        ### 4. Check for Edge Cases

        Consider what happens with null values, zeros, or extreme values:

        ```
        // Check if a value is empty before using it
        if is_empty([discount]) then
            [price]
        else
            [price] * (1 - [discount])
        endif

        // Avoid division by zero
        if [total] == 0 then
            0
        else
            [count] / [total]
        endif
        ```

        ### 5. Test Incrementally

        When building complex expressions, test each part separately:

        1. Test basic column references: `[column_name]`
        2. Test simple calculations: `[price] * [quantity]`
        3. Test conditions: `[age] >= 18`
        4. Combine into more complex expressions

        ### 6. Use Descriptive Output Column Names

        When creating new columns, use descriptive names:

        ```
        // Instead of "result"
        full_name = concat([first_name], " ", [last_name])

        // Instead of "calculation"
        price_with_tax = [price] * 1.07
        ```
        """)


if __name__ == "__main__":
    # This allows running this page directly for development
    st.set_page_config(page_title="Documentation", layout="wide")
    show_docs_page()