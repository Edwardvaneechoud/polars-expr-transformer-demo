import streamlit as st
import polars as pl
import networkx as nx
import matplotlib.pyplot as plt
import uuid
from polars_expr_transformer.process.polars_expr_transformer import build_func, simple_function_to_expr


def build_expression_graph(func_obj):
    G = nx.DiGraph()
    node_meta = {}
    root_id = str(uuid.uuid4())
    _build_graph(G, node_meta, func_obj, root_id)
    return G, node_meta, root_id


def _is_pl_lit_wrapper(obj):
    if not hasattr(obj, '__class__') or obj.__class__.__name__ != 'Func':
        return False
    if not hasattr(obj.func_ref, 'val') or obj.func_ref.val != 'pl.lit':
        return False
    if len(obj.args) != 1:
        return False
    return hasattr(obj.args[0], '__class__') and obj.args[0].__class__.__name__ == 'Func'


def _get_unwrapped_obj(obj):
    if _is_pl_lit_wrapper(obj):
        return _get_unwrapped_obj(obj.args[0])
    return obj


def _build_graph(G, node_meta, obj, node_id, parent_id=None, edge_label=None):
    if hasattr(obj, '__class__') and obj.__class__.__name__ == 'TempFunc':
        if hasattr(obj, 'args') and obj.args:
            return _build_graph(G, node_meta, obj.args[0], node_id, parent_id, edge_label)
        else:
            G.add_node(node_id)
            node_meta[node_id] = {'type': 'tempfunc', 'label': 'TempFunc'}
            if parent_id:
                G.add_edge(parent_id, node_id, label=edge_label or '')
            return

    obj = _get_unwrapped_obj(obj)

    if obj is None:
        return

    if hasattr(obj, '__class__'):
        class_name = obj.__class__.__name__
    else:
        class_name = "Unknown"

    if class_name == "Func":
        func_name = obj.func_ref.val if hasattr(obj.func_ref, 'val') else str(obj.func_ref)

        G.add_node(node_id)
        node_meta[node_id] = {
            'type': 'func',
            'label': f"{func_name}",
            'func_name': func_name
        }

        if parent_id:
            G.add_edge(parent_id, node_id, label=edge_label or '')

        for i, arg in enumerate(obj.args):
            arg_id = str(uuid.uuid4())
            arg_label = f"Arg {i + 1}"
            _build_graph(G, node_meta, arg, arg_id, node_id, arg_label)

    elif class_name == "IfFunc":
        G.add_node(node_id)
        node_meta[node_id] = {'type': 'ifunc', 'label': 'If'}

        if parent_id:
            G.add_edge(parent_id, node_id, label=edge_label or '')

        for i, condition_val in enumerate(obj.conditions):
            cond_id = str(uuid.uuid4())
            G.add_node(cond_id)
            node_meta[cond_id] = {'type': 'condition', 'label': f'Cond {i + 1}'}
            G.add_edge(node_id, cond_id, label=f'Condition: {i + 1}')

            if hasattr(condition_val, 'condition') and condition_val.condition:
                expr_id = str(uuid.uuid4())
                G.add_node(expr_id)
                if hasattr(condition_val.condition, 'get_readable_pl_function'):
                    readable_expr = condition_val.condition.get_readable_pl_function()
                    if len(readable_expr) > 15:
                        readable_expr = readable_expr[:12] + "..."
                    node_meta[expr_id] = {'type': 'expr', 'label': readable_expr}
                else:
                    node_meta[expr_id] = {'type': 'expr', 'label': 'Expr'}
                G.add_edge(cond_id, expr_id, label='When')
                _build_graph(G, node_meta, condition_val.condition, expr_id)

            if hasattr(condition_val, 'val') and condition_val.val:
                then_id = str(uuid.uuid4())
                G.add_node(then_id)
                if hasattr(condition_val.val, 'get_readable_pl_function'):
                    readable_then = condition_val.val.get_readable_pl_function()
                    if len(readable_then) > 15:
                        readable_then = readable_then[:12] + "..."
                    node_meta[then_id] = {'type': 'then', 'label': readable_then}
                else:
                    node_meta[then_id] = {'type': 'then', 'label': 'Then'}
                G.add_edge(cond_id, then_id, label='Then')
                _build_graph(G, node_meta, condition_val.val, then_id)

        if obj.else_val:
            else_id = str(uuid.uuid4())
            G.add_node(else_id)
            if hasattr(obj.else_val, 'get_readable_pl_function'):
                readable_else = obj.else_val.get_readable_pl_function()
                if len(readable_else) > 15:
                    readable_else = readable_else[:12] + "..."
                node_meta[else_id] = {'type': 'else', 'label': readable_else}
            else:
                node_meta[else_id] = {'type': 'else', 'label': 'Else'}
            G.add_edge(node_id, else_id, label='else')
            _build_graph(G, node_meta, obj.else_val, else_id)

    elif class_name == "Classifier":
        val = obj.val if hasattr(obj, 'val') else str(obj)
        val_type = obj.val_type if hasattr(obj, 'val_type') else ""

        G.add_node(node_id)

        if val_type in ["number", "string", "boolean"]:
            display_val = f'"{val}"' if val_type == "string" else val
            node_meta[node_id] = {
                'type': 'value',
                'label': f"{display_val}",
                'value': val,
                'value_type': val_type
            }
        else:
            node_meta[node_id] = {
                'type': 'classifier',
                'label': f"{val}",
                'value': val
            }

        if parent_id:
            G.add_edge(parent_id, node_id, label=edge_label or '')

    else:
        display_val = obj.val if hasattr(obj, 'val') else str(obj)
        G.add_node(node_id)
        node_meta[node_id] = {'type': 'other', 'label': f"{display_val}"}

        if parent_id:
            G.add_edge(parent_id, node_id, label=edge_label or '')


def visualize_expression(expr):
    try:
        func_obj = build_func(expr)
        func_obj.get_pl_func()
        G, node_meta, root_id = build_expression_graph(func_obj)

        # Modern color palette
        node_colors = {
            'func': '#F59E0B',  # Amber-500
            'ifunc': '#EC4899',  # Pink-500
            'condition': '#BE185D',  # Pink-800
            'expr': '#8B5CF6',  # Violet-500
            'then': '#3B82F6',  # Blue-500
            'else': '#06B6D4',  # Cyan-500
            'value': '#10B981',  # Emerald-500
            'classifier': '#6366F1',  # Indigo-500
            'other': '#6B7280',  # Gray-500
            'tempfunc': '#9CA3AF'  # Gray-400
        }

        # Compact node sizes
        node_sizes = {
            'func': 1200,
            'ifunc': 1500,
            'condition': 1300,
            'expr': 1100,
            'then': 1100,
            'else': 1100,
            'value': 1000,
            'classifier': 1100,
            'other': 900,
            'tempfunc': 800
        }

        # Create figure with clean background
        plt.figure(figsize=(10, 6), facecolor='white', dpi=100, tight_layout=True)
        ax = plt.gca()
        ax.set_facecolor('white')

        # Layout
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot')

        # Prepare node attributes
        colors = [node_colors.get(node_meta[node]['type'], '#6B7280') for node in G.nodes()]
        sizes = [node_sizes.get(node_meta[node]['type'], 1200) for node in G.nodes()]

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=colors, alpha=0.95,
                               edgecolors='white', linewidths=1.0, node_shape='o')

        # Draw edges
        nx.draw_networkx_edges(G, pos, width=0.9, arrowsize=12, alpha=0.8,
                               edge_color='#94A3B8', arrows=True,
                               connectionstyle='arc3,rad=0.08',
                               min_source_margin=12, min_target_margin=12)

        # Node labels
        labels = {node: node_meta[node]['label'] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=7,
                                font_family='sans-serif', font_weight='normal',
                                font_color='#27272A')

        # Edge labels
        edge_labels = {(u, v): d.get('label', '')
                       for u, v, d in G.edges(data=True) if d.get('label', '')}

        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6,
                                     font_color='#475569', font_weight='normal',
                                     bbox=dict(facecolor='white', edgecolor='none',
                                               alpha=0.7, pad=0.5))

        plt.axis('off')
        plt.title(expr, fontsize=10, loc='center', pad=5, color='#64748B')

        # Remove frame border
        for spine in ax.spines.values():
            spine.set_visible(False)

        return plt

    except Exception as e:
        st.error(f"Error visualizing expression: {str(e)}")
        return None


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


def show_tree_visualizer_page():
    """Main function to show the tree visualizer page"""
    st.header("Expression Tree Visualizer")
    st.write("""
    This tool helps you understand how Polars Expression Transformer works by visualizing 
    the expression tree. Enter an expression below and see its tree structure.
    """)

    # Create tabs for different types of examples
    tab1, tab2 = st.tabs(["Custom Expression", "Example Expressions"])

    # Sample DataFrame for demonstration
    sample_df = create_sample_dataframe()

    with tab1:
        # User can enter a custom expression
        custom_expr = st.text_area(
            "Enter your expression:",
            value="if [age] > 40 then 'Senior' else 'Junior' endif",
            height=100,
            help="Enter a Polars Expression Transformer expression. Use [column_name] for columns."
        )

        # Show sample data
        st.subheader("Sample Data")
        st.dataframe(sample_df, use_container_width=True)

        # Single button to visualize and apply expression
        if st.button("Visualize Expression", type="primary"):
            with st.spinner("Processing expression..."):
                # First visualize the expression tree
                plt = visualize_expression(custom_expr)
                if plt is not None:
                    # Store in session state
                    st.session_state.custom_plt = plt

                    # Try to apply the expression to the sample data
                    try:
                        result_df = apply_expression_to_dataframe(sample_df, custom_expr)
                        if result_df is not None:
                            st.session_state.custom_result = result_df

                            # Get the equivalent Polars code
                            func_obj = build_func(custom_expr)
                            polars_expr = func_obj.get_readable_pl_function()
                            st.session_state.custom_polars = polars_expr
                    except Exception as e:
                        st.warning(f"Could not apply expression to sample data: {str(e)}")

        # Display results if available
        if 'custom_plt' in st.session_state:
            col1, col2 = st.columns([1, 2])

            with col1:
                if 'custom_result' in st.session_state:
                    st.subheader("Expression Result")
                    st.dataframe(st.session_state.custom_result, use_container_width=True)

                    if 'custom_polars' in st.session_state:
                        st.code(
                            f"# Equivalent Polars code\nexpression = {st.session_state.custom_polars}\ndf.select(expression.alias('result'))",
                            language="python")

            with col2:
                st.subheader("Expression Tree")
                st.pyplot(st.session_state.custom_plt)

    with tab2:
        # Predefined example expressions
        example_categories = {
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

        # Create expanders for each category
        for category, examples in example_categories.items():
            with st.expander(category, expanded=category == "Conditional Logic"):
                # Display examples in the category with buttons to visualize
                for example in examples:
                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.code(example, language="python")

                    with col2:
                        if st.button("Visualize", key=f"viz_{hash(example)}"):
                            with st.spinner("Processing expression..."):
                                # Create visualization
                                plt = visualize_expression(example)

                                # Apply expression to sample data
                                result_df = apply_expression_to_dataframe(sample_df, example)

                                # Get the Polars code
                                try:
                                    func_obj = build_func(example)
                                    polars_expr = func_obj.get_readable_pl_function()

                                    # Store everything in session state
                                    st.session_state.current_example = example
                                    st.session_state.current_plt = plt
                                    st.session_state.current_result = result_df
                                    st.session_state.current_polars = polars_expr
                                except Exception as e:
                                    st.warning(f"Error getting Polars code: {str(e)}")

        # Display the currently selected example's visualization and result
        if 'current_example' in st.session_state and 'current_plt' in st.session_state:
            st.markdown("---")
            st.subheader(f"Visualization for: `{st.session_state.current_example}`")

            col1, col2 = st.columns([1, 2])

            with col1:
                st.subheader("Sample Data")
                st.dataframe(sample_df, use_container_width=True)

                if 'current_result' in st.session_state:
                    st.subheader("Expression Result")
                    st.dataframe(st.session_state.current_result, use_container_width=True)

                    # Display the equivalent Polars code if available
                    if 'current_polars' in st.session_state:
                        st.code(
                            f"# Equivalent Polars code\nexpression = {st.session_state.current_polars}\ndf.select(expression.alias('result'))",
                            language="python")

            with col2:
                st.subheader("Expression Tree")
                st.pyplot(st.session_state.current_plt)

    # Add a legend explaining the colors
    st.markdown("---")
    st.subheader("Tree Node Legend")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("🟠 **Function** - Polars function")
        st.markdown("🟣 **If** - Conditional statement")

    with col2:
        st.markdown("🔵 **Then** - Then branch")
        st.markdown("🟢 **Value** - Literal value")

    with col3:
        st.markdown("🔴 **Condition** - Conditional expression")
        st.markdown("🟣 **Expression** - Expression within condition")

    with col4:
        st.markdown("🔵 **Else** - Else branch")
        st.markdown("🟣 **Classifier** - Column reference")


if __name__ == "__main__":
    # This allows running this page directly for development
    st.set_page_config(page_title="Expression Tree Visualizer", layout="wide")
    show_tree_visualizer_page()