from collections import defaultdict
import sys
import streamlit as st
import networkx as nx
import plotly.graph_objects as go

class Graph:
    """Simple undirected weighted graph."""

    def __init__(self):
        self.edges = defaultdict(list)
        self.weights = {}

    def add_edge(self, from_node, to_node, weight):
        """Add an undirected, weighted edge."""
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.weights[(from_node, to_node)] = int(weight)
        self.weights[(to_node, from_node)] = int(weight)


def load_graph_from_file(filename):
    """Load a graph from a tab-delimited file with: node1, node2, weight."""
    graph = Graph()
    with open(filename, "r") as infile:
        for line in infile:
            parts = line.strip().split("\t")
            if len(parts) != 3:
                continue  # skip malformed lines
            node1, node2, weight = parts
            graph.add_edge(node1, node2, weight)
    return graph


def dijkstra(graph, start, end):
    """Return the shortest path and total weight between two nodes using Dijkstra’s algorithm."""
    if start not in graph.edges or end not in graph.edges:
        return None, f"One or both nodes not found: {start}, {end}"

    shortest_paths = {start: (None, 0)}
    visited = set()
    current_node = start

    while current_node != end:
        visited.add(current_node)
        destinations = graph.edges[current_node]
        current_weight = shortest_paths[current_node][1]

        for next_node in destinations:
            weight = graph.weights[(current_node, next_node)] + current_weight
            if next_node not in shortest_paths or shortest_paths[next_node][1] > weight:
                shortest_paths[next_node] = (current_node, weight)

        next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
        if not next_destinations:
            return None, f"There is no path between {start} and {end}"

        current_node = min(next_destinations, key=lambda k: next_destinations[k][1])

    # reconstruct path
    path = []
    while current_node is not None:
        path.append(current_node)
        current_node = shortest_paths[current_node][0]
    path = path[::-1]

    total_weight = shortest_paths[path[-1]][1]
    return path, total_weight


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python run.py <filename> <start_node> <end_node>")
        sys.exit(1)

    filename = sys.argv[1]
    start_node = sys.argv[2]
    end_node = sys.argv[3]

    graph = load_graph_from_file(filename)
    path, result = dijkstra(graph, start_node, end_node)

    if path is None:
        print(result)
    else:
        print(f"Shortest path between {start_node} and {end_node}: {path}")
        print(f"Total weight: {result}")


# -------- Plotly Visualization --------
def plot_graph(graph, path=None):
    G = nx.Graph()
    for (node1, node2), weight in graph.weights.items():
        if G.has_edge(node1, node2):
            continue
        G.add_edge(node1, node2, weight=weight)

    pos = nx.spring_layout(G, seed=42)

    edge_x, edge_y, edge_text = [], [], []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        edge_text.append(f"{edge[0]}-{edge[1]}: {edge[2]['weight']}")

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='text',
        text=edge_text,
        mode='lines'
    )

    node_x, node_y, node_text, node_color = [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        if path and node in path:
            node_color.append('orange')
        else:
            node_color.append('lightblue')

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(size=20, color=node_color, line=dict(width=2)),
        text=node_text,
        hoverinfo='text',
        textposition="top center"
    )

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='Graph Visualization (Shortest Path Highlighted)',
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    ))

    st.plotly_chart(fig, use_container_width=True)

# -------- Streamlit App --------
st.title("GIR: Graph Interaction Resolver (Interactive)")
st.markdown("Upload a weighted graph and visualize the shortest path interactively.")

uploaded_file = st.file_uploader("Upload tab-delimited graph file (node1, node2, weight)", type=["txt", "lst"])
if uploaded_file:
    graph = load_graph_from_file(uploaded_file)
    nodes = list(graph.edges.keys())
    start_node = st.selectbox("Select start node", nodes)
    end_node = st.selectbox("Select end node", nodes)

    if st.button("Compute Shortest Path"):
        path, result = dijkstra(graph, start_node, end_node)
        if path is None:
            st.warning(result)
        else:
            st.success(f"Shortest path: {' -> '.join(path)}")
            st.info(f"Total weight: {result}")
            plot_graph(graph, path)