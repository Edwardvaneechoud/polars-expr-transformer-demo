import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import uuid
import re


def build_expression_graph(expr):
    """Build a graph representation of the expression"""
    G = nx.DiGraph()
    node_meta = {}
    root_id = str(uuid.uuid4())

    # Parse the expression and build graph
    if "if" in expr.lower() and "then" in expr.lower():
        # Conditional expression
        G.add_node(root_id)
        node_meta[root_id] = {'type': 'ifunc', 'label': 'If'}

        # Extract condition
        condition_match = re.search(r'if\s+(.*?)\s+then', expr, re.IGNORECASE)
        if condition_match:
            condition_text = condition_match.group(1)
            cond_id = str(uuid.uuid4())
            G.add_node(cond_id)
            node_meta[cond_id] = {'type': 'condition',
                                  'label': condition_text[:15] + '...' if len(condition_text) > 15 else condition_text}
            G.add_edge(root_id, cond_id, label='Condition')

            # Parse the condition further if it has comparison operators
            if any(op in condition_text for op in ['>', '<', '==', '!=', '>=', '<=']):
                parts = re.split(r'(\>|\<|\=\=|\!\=|\>\=|\<\=)', condition_text)
                if len(parts) >= 3:
                    left_id = str(uuid.uuid4())
                    op_id = str(uuid.uuid4())
                    right_id = str(uuid.uuid4())

                    G.add_node(left_id)
                    G.add_node(op_id)
                    G.add_node(right_id)

                    left_text = parts[0].strip()
                    if '[' in left_text and ']' in left_text:
                        node_meta[left_id] = {'type': 'classifier', 'label': left_text}
                    else:
                        node_meta[left_id] = {'type': 'value', 'label': left_text}

                    node_meta[op_id] = {'type': 'func', 'label': parts[1].strip()}

                    right_text = parts[2].strip()
                    if right_text.isdigit() or (right_text.replace('.', '', 1).isdigit() and right_text.count('.') < 2):
                        node_meta[right_id] = {'type': 'value', 'label': right_text}
                    elif right_text.startswith("'") or right_text.startswith('"'):
                        node_meta[right_id] = {'type': 'value', 'label': right_text}
                    else:
                        node_meta[right_id] = {'type': 'other', 'label': right_text}

                    G.add_edge(cond_id, op_id)
                    G.add_edge(op_id, left_id, label='Arg 1')
                    G.add_edge(op_id, right_id, label='Arg 2')

        # Extract 'then' part
        then_match = re.search(r'then\s+(.*?)(\s+else|\s+endif)', expr, re.IGNORECASE)
        if then_match:
            then_text = then_match.group(1)
            then_id = str(uuid.uuid4())
            G.add_node(then_id)
            node_meta[then_id] = {'type': 'then', 'label': then_text[:15] + '...' if len(then_text) > 15 else then_text}
            G.add_edge(root_id, then_id, label='Then')

        # Extract 'else' part
        else_match = re.search(r'else\s+(.*?)\s+endif', expr, re.IGNORECASE)
        if else_match:
            else_text = else_match.group(1)
            else_id = str(uuid.uuid4())
            G.add_node(else_id)
            node_meta[else_id] = {'type': 'else', 'label': else_text[:15] + '...' if len(else_text) > 15 else else_text}
            G.add_edge(root_id, else_id, label='Else')

    elif "concat" in expr.lower():
        # Concatenation expression
        G.add_node(root_id)
        node_meta[root_id] = {'type': 'func', 'label': 'concat'}

        # Extract arguments
        args_match = re.search(r'concat\((.*?)\)', expr, re.IGNORECASE)
        if args_match:
            args_text = args_match.group(1)
            # Split by commas, respecting string literals
            in_string = False
            current_arg = ""
            args = []

            for char in args_text:
                if char in ['"', "'"]:
                    in_string = not in_string
                    current_arg += char
                elif char == ',' and not in_string:
                    args.append(current_arg.strip())
                    current_arg = ""
                else:
                    current_arg += char

            if current_arg:
                args.append(current_arg.strip())

            # Add argument nodes
            for i, arg in enumerate(args):
                arg_id = str(uuid.uuid4())
                G.add_node(arg_id)

                if '[' in arg and ']' in arg:
                    node_meta[arg_id] = {'type': 'classifier', 'label': arg}
                elif arg.startswith("'") or arg.startswith('"'):
                    node_meta[arg_id] = {'type': 'value', 'label': arg}
                else:
                    node_meta[arg_id] = {'type': 'other', 'label': arg}

                G.add_edge(root_id, arg_id, label=f'Arg {i + 1}')

    # Simple column reference
    elif '[' in expr and ']' in expr:
        G.add_node(root_id)
        node_meta[root_id] = {'type': 'classifier', 'label': expr}

    # Generic expression
    else:
        G.add_node(root_id)
        node_meta[root_id] = {'type': 'other', 'label': expr}

    return G, node_meta, root_id


def visualize_expression(expr):
    """Visualize an expression tree using NetworkX and Matplotlib with hierarchical layout"""
    try:
        G, node_meta, root_id = build_expression_graph(expr)

        # Modern, vibrant color palette with higher contrast
        node_colors = {
            'func': '#FF6B00',  # Vivid orange
            'ifunc': '#FF1493',  # Deep pink
            'condition': '#C71585',  # Medium violet red
            'expr': '#9400D3',  # Dark violet
            'then': '#1E90FF',  # Dodger blue
            'else': '#00CED1',  # Dark turquoise
            'value': '#00CC66',  # Spring green
            'classifier': '#4B0082',  # Indigo
            'other': '#555555',  # Dark gray
            'tempfunc': '#888888'  # Medium gray
        }

        # Node sizes - larger for better visibility
        node_sizes = {
            'func': 1500,
            'ifunc': 1800,
            'condition': 1600,
            'expr': 1400,
            'then': 1400,
            'else': 1400,
            'value': 1300,
            'classifier': 1400,
            'other': 1200,
            'tempfunc': 1000
        }

        # Create a crisp, modern figure with taller aspect ratio for hierarchical display
        plt.figure(figsize=(12, 10), facecolor='white', dpi=120, tight_layout=True)
        ax = plt.gca()
        ax.set_facecolor('#FAFAFA')  # Very light gray background

        # Add subtle grid lines to emphasize the hierarchical structure
        ax.grid(True, linestyle='--', alpha=0.1, zorder=0)

        # Force a strictly hierarchical layout
        try:
            # First try graphviz's dot algorithm which creates excellent hierarchical layouts
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        except:
            # If graphviz is not available, create our own hierarchical positioning
            # Identify layers based on distance from root
            layers = {}
            for node in G.nodes():
                # Calculate distance from root
                try:
                    dist = nx.shortest_path_length(G, root_id, node)
                except:
                    dist = 0  # For disconnected nodes or the root itself

                if dist not in layers:
                    layers[dist] = []
                layers[dist].append(node)

            # Position nodes in layers
            pos = {}
            max_layer_size = max(len(nodes) for nodes in layers.values())
            for layer_idx, nodes in layers.items():
                y_pos = 1.0 - (layer_idx * 0.2)  # Layer y-position, starting from top

                # Position nodes horizontally in their layer
                for i, node in enumerate(nodes):
                    # Calculate x position to center nodes in each layer
                    if len(nodes) > 1:
                        x_pos = (i / (len(nodes) - 1) - 0.5) * 0.8 + 0.5
                    else:
                        x_pos = 0.5

                    pos[node] = (x_pos, y_pos)

        # Prepare node styling
        colors = [node_colors.get(node_meta[node]['type'], '#888888') for node in G.nodes()]
        sizes = [node_sizes.get(node_meta[node]['type'], 1200) for node in G.nodes()]

        # Enhanced node rendering
        nx.draw_networkx_nodes(G, pos,
                               node_size=sizes,
                               node_color=colors,
                               alpha=0.9,
                               edgecolors='white',
                               linewidths=2.0,
                               node_shape='o')

        # Draw edges in a strict top-to-bottom flow for hierarchical appearance
        nx.draw_networkx_edges(G, pos,
                               width=1.5,
                               arrowsize=15,
                               alpha=0.8,
                               edge_color='#444444',
                               arrows=True,
                               # Less aggressive curve for cleaner hierarchical look
                               connectionstyle='arc3,rad=0.1',
                               min_source_margin=15,
                               min_target_margin=15)

        # Clear, bold node labels
        labels = {node: node_meta[node]['label'] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos,
                                labels=labels,
                                font_size=9,
                                font_family='sans-serif',
                                font_weight='bold',
                                font_color='white')

        # Edge labels with improved visibility
        edge_labels = {(u, v): d.get('label', '')
                       for u, v, d in G.edges(data=True) if d.get('label', '')}

        nx.draw_networkx_edge_labels(G, pos,
                                     edge_labels=edge_labels,
                                     font_size=8,
                                     font_color='#333333',
                                     font_weight='bold',
                                     bbox=dict(facecolor='white',
                                               edgecolor='lightgray',
                                               alpha=0.8,
                                               boxstyle='round,pad=0.3'))

        # Clean styling
        plt.axis('off')
        plt.title(expr, fontsize=12, fontweight='bold', loc='center', pad=20, color='#333333')

        # Remove border
        for spine in ax.spines.values():
            spine.set_visible(False)

        return plt

    except Exception as e:
        st.error(f"Error visualizing expression: {str(e)}")
        return None


def create_sample_dataframe():
    """Create a sample DataFrame for demonstration purposes"""
    return {
        "name": ["John Smith", "Jane Doe", "Robert Johnson", "Maria Garcia", "Wei Zhang"],
        "age": [34, 42, 28, 55, 39],
        "city": ["New York", "San Francisco", "Chicago", "Boston", "Seattle"],
        "salary": [75000, 95000, 65000, 120000, 85000],
        "joined_date": ["2020-03-15", "2019-07-22", "2021-01-05", "2018-05-30", "2020-11-11"]
    }


def apply_expression_to_dataframe(data, expr):
    """Simulate applying the expression to data"""
    # This is a placeholder for the actual expression evaluation
    return {"result": ["Result " + str(i + 1) for i in range(len(data["name"]))]}


def show_tree_visualizer_page():
    """Main function to show the tree visualizer page"""
    st.header("Expression Tree Visualizer")
    st.write("""
    This tool helps you understand expressions by visualizing them as hierarchical trees.
    Enter an expression below to see its structure with a clear top-to-bottom flow.
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
            help="Enter an expression. Use [column_name] for columns."
        )

        # Show sample data
        with st.expander("View Sample Data", expanded=False):
            st.dataframe(sample_df, use_container_width=True)

        # Button to visualize expression
        if st.button("Visualize Expression", type="primary", use_container_width=True):
            with st.spinner("Processing expression..."):
                # Visualize the expression tree
                plt = visualize_expression(custom_expr)
                if plt is not None:
                    # Store in session state
                    st.session_state.custom_plt = plt

                    # Simulate applying expression
                    result = apply_expression_to_dataframe(sample_df, custom_expr)
                    st.session_state.custom_result = result

        # Display results if available
        if 'custom_plt' in st.session_state:
            st.subheader("Expression Tree")
            st.pyplot(st.session_state.custom_plt)

            if 'custom_result' in st.session_state:
                with st.expander("View Simulated Results", expanded=False):
                    st.dataframe(st.session_state.custom_result, use_container_width=True)

    with tab2:
        # Predefined example expressions
        example_categories = {
            "String Operations": [
                "concat([name], ' from ', [city])",
                "contains([city], 'o')",
                "length([name])"
            ],
            "Numeric Operations": [
                "[salary] / 12",
                "[age] > 35"
            ],
            "Conditional Logic": [
                "if [age] > 40 then 'Senior' else 'Junior' endif",
                "if [salary] > 100000 then 'High' else 'Standard' endif",
                "if contains([city], 'o') then length([city]) else 0 endif"
            ]
        }

        # Display examples in a more compact way
        selected_category = st.selectbox("Select category", list(example_categories.keys()))
        selected_example = st.selectbox("Select example", example_categories[selected_category])

        if st.button("Visualize Selected Example", type="primary", use_container_width=True):
            with st.spinner("Processing expression..."):
                # Create visualization
                plt = visualize_expression(selected_example)

                # Store in session state
                st.session_state.example_plt = plt
                st.session_state.current_example = selected_example

                # Simulate applying expression
                result = apply_expression_to_dataframe(sample_df, selected_example)
                st.session_state.example_result = result

        # Display visualization if available
        if 'example_plt' in st.session_state:
            st.subheader(f"Visualization for: `{st.session_state.current_example}`")
            st.pyplot(st.session_state.example_plt)

            if 'example_result' in st.session_state:
                with st.expander("View Sample Data and Results", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Sample Data")
                        st.dataframe(sample_df, use_container_width=True)
                    with col2:
                        st.subheader("Results")
                        st.dataframe(st.session_state.example_result, use_container_width=True)

    # Add a colorful legend explaining the node types
    with st.expander("Node Type Legend", expanded=False):
        cols = st.columns(3)

        with cols[0]:
            st.markdown("🟠 **Function** - Operations like concat")
            st.markdown("🟣 **Condition** - Comparison expressions")
            st.markdown("🟢 **Value** - Literal values")

        with cols[1]:
            st.markdown("🔵 **Then** - Then branch")
            st.markdown("🟣 **If** - Conditional statement")
            st.markdown("🟣 **Classifier** - Column reference")

        with cols[2]:
            st.markdown("🔵 **Else** - Else branch")
            st.markdown("🟣 **Expression** - Nested expressions")
            st.markdown("⚪ **Other** - Other elements")


if __name__ == "__main__":
    st.set_page_config(page_title="Expression Tree Visualizer", layout="wide")
    show_tree_visualizer_page()