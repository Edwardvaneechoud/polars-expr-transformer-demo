import streamlit as st
import polars as pl
import uuid

from streamlit_agraph import agraph, Node, Edge, Config

from polars_expr_transformer.process.polars_expr_transformer import build_func, simple_function_to_expr
from polars_expr_transformer.visualize import generate_visualization



def build_expression_graph(func_obj):
    """
    Build nodes and edges for agraph visualization from a function object.

    Args:
        func_obj: The function object to visualize

    Returns:
        tuple: A tuple of (nodes, edges) lists for agraph
    """
    nodes = []
    edges = []
    node_ids = {}  # Keep track of created node IDs to avoid duplicates

    # Function to generate a unique ID for nodes
    def get_node_id(prefix, name=None):
        # Make the first node have a consistent ID to ensure it's handled as the root
        if not nodes:
            if name:
                return f"root_{name}"
            return "root_node"

        # Use the node name if provided
        if name:
            # Clean up the name to make it a valid ID (remove spaces, quotes, etc.)
            clean_name = str(name).replace(' ', '_').replace('"', '').replace("'", "")
            clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
            node_id = f"{prefix}_{clean_name}"

            # Add a unique suffix if this ID already exists
            counter = 1
            original_id = node_id
            while node_id in node_ids:
                node_id = f"{original_id}_{counter}"
                counter += 1

            node_ids[node_id] = True
            return node_id

        # Fallback to a shorter random ID
        node_id = f"{prefix}_{str(uuid.uuid4())[:4]}"
        return node_id

    # Function to generate structured elements recursively
    def _build_graph(obj, parent_id=None, edge_label=None):
        if obj is None:
            return None

        # Skip TempFunc and unwrap pl.lit wrappers
        if hasattr(obj, '__class__') and obj.__class__.__name__ == 'TempFunc':
            if hasattr(obj, 'args') and obj.args:
                return _build_graph(obj.args[0], parent_id, edge_label)
            else:
                node_id = get_node_id("temp")
                nodes.append(Node(id=node_id,
                                  label="TempFunc",
                                  color="#9CA3AF",  # Gray-400
                                  size=15,
                                  shape="dot"))

                if parent_id:
                    edges.append(Edge(source=parent_id,
                                      target=node_id,
                                      label=edge_label or ""))
                return node_id

        # Unwrap pl.lit wrapper objects
        if (hasattr(obj, '__class__') and obj.__class__.__name__ == 'Func' and
                hasattr(obj, 'func_ref') and hasattr(obj.func_ref, 'val') and
                obj.func_ref.val == 'pl.lit' and len(obj.args) == 1):
            # Check if we're wrapping an expression (as in get_readable_pl_function)
            if hasattr(obj.args[0], 'get_pl_func') and isinstance(obj.args[0].get_pl_func(), pl.expr.Expr):
                return _build_graph(obj.args[0], parent_id, edge_label)
            else:
                # Otherwise, keep the pl.lit wrapper and process its argument
                return _build_graph(obj.args[0], parent_id, edge_label)

        if hasattr(obj, '__class__'):
            class_name = obj.__class__.__name__
        else:
            class_name = "Unknown"

        if class_name == "Func":
            func_name = obj.func_ref.val if hasattr(obj.func_ref, 'val') else str(obj.func_ref)

            node_id = get_node_id("func")
            nodes.append(Node(id=node_id,
                              label=func_name,
                              color="#F59E0B",  # Amber-500
                              size=20,
                              shape="dot"))

            # Connect to parent if exists
            if parent_id:
                edges.append(Edge(source=parent_id,
                                  target=node_id,
                                  label=edge_label or ""))

            # Process arguments
            for i, arg in enumerate(obj.args):
                arg_label = f"Arg {i + 1}"
                _build_graph(arg, node_id, arg_label)

            return node_id

        elif class_name == "IfFunc":
            # Add the if node
            node_id = get_node_id("if")
            nodes.append(Node(id=node_id,
                              label="If",
                              color="#EC4899",  # Pink-500
                              size=25,
                              shape="dot"))

            # Connect to parent if exists
            if parent_id:
                edges.append(Edge(source=parent_id,
                                  target=node_id,
                                  label=edge_label or ""))

            # Process conditions
            for i, condition_val in enumerate(obj.conditions):
                cond_id = get_node_id("cond")
                nodes.append(Node(id=cond_id,
                                  label=f"Cond {i + 1}",
                                  color="#BE185D",  # Pink-800
                                  size=18,
                                  shape="dot"))

                edges.append(Edge(source=node_id,
                                  target=cond_id,
                                  label=f"Condition: {i + 1}"))

                # Process condition expression
                if hasattr(condition_val, 'condition') and condition_val.condition:
                    # Get readable expression if available
                    expr_label = "Expr"
                    if hasattr(condition_val.condition, 'get_readable_pl_function'):
                        readable_expr = condition_val.condition.get_readable_pl_function()
                        if len(readable_expr) > 25:
                            expr_label = readable_expr[:22] + "..."
                        else:
                            expr_label = readable_expr

                    expr_id = get_node_id("expr")
                    nodes.append(Node(id=expr_id,
                                      label=expr_label,
                                      color="#8B5CF6",  # Violet-500
                                      size=18,
                                      shape="dot"))

                    edges.append(Edge(source=cond_id,
                                      target=expr_id,
                                      label="When"))

                    _build_graph(condition_val.condition, expr_id)

                # Process 'then' value
                if hasattr(condition_val, 'val') and condition_val.val:
                    # Get readable 'then' if available
                    then_label = "Then"
                    if hasattr(condition_val.val, 'get_readable_pl_function'):
                        readable_then = condition_val.val.get_readable_pl_function()
                        if len(readable_then) > 25:
                            then_label = readable_then[:22] + "..."
                        else:
                            then_label = readable_then

                    then_id = get_node_id("then")
                    nodes.append(Node(id=then_id,
                                      label=then_label,
                                      color="#3B82F6",  # Blue-500
                                      size=18,
                                      shape="dot"))

                    edges.append(Edge(source=cond_id,
                                      target=then_id,
                                      label="Then"))

                    _build_graph(condition_val.val, then_id)

            # Process 'else' value
            if obj.else_val:
                # Get readable 'else' if available
                else_label = "Else"
                if hasattr(obj.else_val, 'get_readable_pl_function'):
                    readable_else = obj.else_val.get_readable_pl_function()
                    if len(readable_else) > 25:
                        else_label = readable_else[:22] + "..."
                    else:
                        else_label = readable_else

                else_id = get_node_id("else")
                nodes.append(Node(id=else_id,
                                  label=else_label,
                                  color="#06B6D4",  # Cyan-500
                                  size=18,
                                  shape="dot"))

                edges.append(Edge(source=node_id,
                                  target=else_id,
                                  label="Else"))

                _build_graph(obj.else_val, else_id)

            return node_id

        elif class_name == "Classifier":
            val = obj.val if hasattr(obj, 'val') else str(obj)
            val_type = obj.val_type if hasattr(obj, 'val_type') else ""

            # Format value display based on type
            if val_type == "string":
                display_val = f'"{val}"'
            else:
                display_val = str(val)

            # Determine node color and characteristics based on classifier type
            if val_type in ["number", "string", "boolean"]:
                node_id = get_node_id("value")
                nodes.append(Node(id=node_id,
                                  label=display_val,
                                  color="#10B981",  # Emerald-500
                                  size=15,
                                  shape="dot"))
            else:
                node_id = get_node_id("classifier")
                nodes.append(Node(id=node_id,
                                  label=str(val),
                                  color="#6366F1",  # Indigo-500
                                  size=15,
                                  shape="dot"))

            # Connect to parent if exists
            if parent_id:
                edges.append(Edge(source=parent_id,
                                  target=node_id,
                                  label=edge_label or ""))

            return node_id

        else:
            # Handle other types
            display_val = obj.val if hasattr(obj, 'val') else str(obj)

            node_id = get_node_id("other")
            nodes.append(Node(id=node_id,
                              label=str(display_val),
                              color="#6B7280",  # Gray-500
                              size=15,
                              shape="dot"))

            # Connect to parent if exists
            if parent_id:
                edges.append(Edge(source=parent_id,
                                  target=node_id,
                                  label=edge_label or ""))

            return node_id

    # Start the recursive build
    _build_graph(func_obj)

    return nodes, edges


def visualize_expression(expr):
    """
    Visualize the given expression tree using streamlit-agraph

    Args:
        expr: String expression to visualize

    Returns:
        tuple: (nodes, edges) for the graph, text_visualization
    """
    try:
        # Build the function object from the expression
        func_obj = build_func(expr)
        if isinstance(func_obj.args[0].get_pl_func(), pl.expr.Expr):
            func_obj = func_obj.args[0]

        # Access the inner function object if wrapped in TempFunc
        if hasattr(func_obj, '__class__') and func_obj.__class__.__name__ == 'TempFunc' and func_obj.args:
            func_obj = func_obj.args[0]

        # Validate by getting the Polars function
        func_obj.get_pl_func()

        # Build the nodes and edges for the visualization
        nodes, edges = build_expression_graph(func_obj)

        # Generate the text visualization
        text_viz = generate_visualization(expr)

        return nodes, edges, text_viz
    except Exception as e:
        st.error(f"Error visualizing expression: {str(e)}")
        return [], [], ""


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
    st.write("""
    This tool helps you understand how Polars Expression Transformer works by visualizing 
    the expression tree. Enter an expression below and see its tree structure.
    """)

    # Sample DataFrame for demonstration
    sample_df = create_sample_dataframe()

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

    # Visualize button
    if st.button("Visualize Expression", type="primary"):
        with st.spinner("Processing expression..."):
            # Visualize the expression tree
            nodes, edges, text_viz = visualize_expression(custom_expr)
            if nodes:
                st.session_state.custom_nodes = nodes
                st.session_state.custom_edges = edges
                st.session_state.text_viz = text_viz

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
    if 'custom_nodes' in st.session_state and 'custom_edges' in st.session_state:
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

            # Create the graph configuration with tree-like hierarchical layout
            config = Config(
                width=700,
                height=400,  # Reduced height
                directed=True,
                physics=False,  # Disable physics for more stable tree layout
                hierarchical=True,
                # Hierarchical layout options
                hierarchical_sort_method="directed",  # direct the graph flow from top to bottom
                hierarchical_direction="UD",  # Top to bottom layout
                hierarchical_node_spacing=75,  # Reduced spacing
                hierarchical_level_separation=150,  # Control vertical spacing
                hierarchical_edge_minimization=True,
                # Root node positioning - force the first node to be at the top
                hierarchical_sortmethod="directed",  # Ensure proper root node detection
                # Improve the user experience
                node_margin=8,
                node_font_size=12,
                edge_width=1.5,
                edge_curved=False,  # Straight lines for cleaner tree appearance
                # More emphasis on layout structure
                layout={
                    "improvedLayout": True,
                    "hierarchical": {
                        "enabled": True,
                        "direction": "UD",
                        "sortMethod": "directed",
                        "nodeSpacing": 75,
                        "treeSpacing": 200
                    }
                }
            )
            with st.expander("Expression Tree", expanded=True):

                # Use agraph to display the visualization
                # Wrap in a container with fixed height to prevent large graphs from expanding too much
                with st.container(height=450):
                    return_value = agraph(
                        nodes=st.session_state.custom_nodes,
                        edges=st.session_state.custom_edges,
                        config=config
                    )

            # Add an expander for the text visualization
            with st.expander("Text Visualization", expanded=True):
                st.code(st.session_state.text_viz, language="text")

    # Add a legend explaining the node colors
    st.markdown("---")
    st.subheader("Tree Node Legend")

    legend_items = [
        ("🟠 Function", "#F59E0B", "Polars function"),
        ("🟣 If", "#EC4899", "Conditional statement"),
        ("🔴 Condition", "#BE185D", "Conditional expression"),
        ("🟣 Expression", "#8B5CF6", "Expression within condition"),
        ("🔵 Then", "#3B82F6", "Then branch"),
        ("🔵 Else", "#06B6D4", "Else branch"),
        ("🟢 Value", "#10B981", "Literal value"),
        ("🟣 Classifier", "#6366F1", "Column reference")
    ]

    # Create a 4-column layout for the legend
    cols = st.columns(4)
    for i, (label, color, desc) in enumerate(legend_items):
        col_index = i % 4
        with cols[col_index]:
            st.markdown(f"<div style='display:flex;align-items:center;'>"
                        f"<div style='width:15px;height:15px;background-color:{color};border-radius:50%;margin-right:8px;'></div>"
                        f"<div><strong>{label.split(' ')[1]}</strong> - {desc}</div>"
                        f"</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    # This allows running this page directly for development
    st.set_page_config(page_title="Expression Tree Visualizer", layout="wide")
    show_tree_visualizer_page()