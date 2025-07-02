from pyvis.network import Network
import os
import streamlit as st # Added for Streamlit components

# Output file for graph visualization (will be relative to where the app runs)
GRAPH_HTML_FILE = "knowledge_graph_output.html"

def _initialize_pyvis_network():
    """Initializes and returns a Pyvis Network object with default settings."""
    # Changed notebook=True for Streamlit compatibility
    return Network(height="700px", width="100%", directed=True,
                    notebook=True, bgcolor="#222222", font_color="white")

def _add_nodes_to_network(net: Network, nodes: list):
    """Adds nodes to the Pyvis network."""
    for node in nodes:
        try:
            net.add_node(str(node.id), label=str(node.id), title=str(node.type), group=str(node.type))
        except Exception as e:
            st.warning(f"Warning: Could not add node {node.id}: {e}")

def _add_edges_to_network(net: Network, relationships: list):
    """Adds edges to the Pyvis network."""
    for rel in relationships:
        try:
            net.add_edge(str(rel.source.id), str(rel.target.id), label=str(rel.type).lower())
        except Exception as e:
            st.warning(f"Warning: Could not add edge {rel.source.id}-{rel.target.id} ({rel.type}): {e}")

def _configure_pyvis_physics(net: Network):
    """Sets the physics options for the Pyvis network."""
    net.set_options("""
        {
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -100,
                    "centralGravity": 0.01,
                    "springLength": 200,
                    "springConstant": 0.08
                },
                "minVelocity": 0.75,
                "solver": "forceAtlas2Based"
            }
        }
    """)

def visualize_graph(graph_documents):
    """Visualizes the extracted knowledge graph using Pyvis and displays it in Streamlit."""
    if not graph_documents or not graph_documents[0].nodes:
        st.info("No graph documents or nodes to visualize.")
        return

    net = _initialize_pyvis_network()

    nodes = graph_documents[0].nodes
    relationships = graph_documents[0].relationships

    # Add all nodes, then add edges
    _add_nodes_to_network(net, nodes)
    _add_edges_to_network(net, relationships)
    _configure_pyvis_physics(net)

    # Save to a temporary HTML file and display in Streamlit
    try:
        net.save_graph(GRAPH_HTML_FILE)
        # Use st.components.v1.html for embedding in Streamlit
        with open(GRAPH_HTML_FILE, 'r', encoding='utf-8') as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=720) # Adjusted height for better viewing in web app
        os.remove(GRAPH_HTML_FILE) # Clean up the temporary file after displaying
        st.success("Graph visualization generated and displayed.")
    except Exception as e:
        st.error(f"Error generating or displaying graph: {e}")