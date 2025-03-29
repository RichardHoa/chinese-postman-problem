import networkx as nx
import random
from pyvis.network import Network
import os

# List of 50 unique locations
locations = [f"Location {i+1}" for i in range(500)]

# Graph size options
graph_sizes = {"small": 10, "medium": 25, "large": 50,"gigantic":500}

CHANCES = 0.9

MAX_DEGREE = 500

def generate_graph(size, max_degree=MAX_DEGREE):
    """Generates a connected graph with controlled max degree."""
    num_nodes = graph_sizes[size]
    selected_locations = random.sample(locations, num_nodes)  # Unique names

    # Create an empty graph and add nodes
    G = nx.Graph()
    G.add_nodes_from(selected_locations)

    # Step 1: Create a spanning tree (ensures connectivity)
    remaining_nodes = set(selected_locations)
    current_node = remaining_nodes.pop()
    
    while remaining_nodes:
        next_node = random.choice(list(remaining_nodes))
        weight = round(random.uniform(1.0, 10.0), 1)
        G.add_edge(current_node, next_node, weight=weight)
        current_node = next_node
        remaining_nodes.remove(next_node)

    # Step 2: Add more edges while ensuring degree varies randomly
    nodes = list(G.nodes())
    random.shuffle(nodes)

    for node in nodes:
        if random.random() < CHANCES:  
            max_possible_edges = int(max_degree - G.degree[node])
            if max_possible_edges > 0:  # Only proceed if node can have more edges
                num_extra_edges = random.randint(1, max_possible_edges)
                possible_nodes = [n for n in nodes if n != node and G.degree[n] < max_degree]

                for _ in range(num_extra_edges):
                    if not possible_nodes:
                        break
                    neighbor = random.choice(possible_nodes)
                    weight = round(random.uniform(1.0, 10.0), 1)
                    G.add_edge(node, neighbor, weight=weight)
                    possible_nodes.remove(neighbor)  # Avoid exceeding max degree

    return G

def graph_to_adjacency_list(G):
    """Converts NetworkX graph to an adjacency list."""
    adj_list = {node: [] for node in G.nodes()}
    for u, v, data in G.edges(data=True):
        weight = data["weight"]
        adj_list[u].append((v, weight))
        adj_list[v].append((u, weight))


    for node, neighbors in adj_list.items():
        print(f"{node}: {', '.join(f'{neighbor}({weight})' for neighbor, weight in neighbors)}")


def print_degree_distribution(G):
    """Prints the distribution of node degrees in the graph, including percentages."""
    degree_count = {}
    total_nodes = len(G.nodes())

    # Count occurrences of each degree
    for node in G.nodes():
        degree = G.degree[node]
        degree_count[degree] = degree_count.get(degree, 0) + 1

    # Print sorted results with percentage
    for degree in sorted(degree_count):
        count = degree_count[degree]
        percentage = round((count / total_nodes) * 100)  # Round up percentage
        print(f"{count} nodes have {degree} edges ({percentage}%)")


# Function to visualize the graph
def visualize_graph(G, starting_node=None):
    """Visualizes the graph using Pyvis and ensures the HTML opens correctly."""
    net = Network(notebook=False)

    # Spacing control
    net.force_atlas_2based(gravity=-100, central_gravity=0.0015)

    # Disable physics for fixed edge lengths
    net.toggle_physics(False)

    net.show_buttons(filter_=['physics'])

    # Add nodes
    for node in G.nodes():
        color = "red" if node == starting_node else "#1f78b4"
        net.add_node(node, label=node, color=color)

    # Add edges
    for u, v, data in G.edges(data=True):
        weight = data["weight"]
        edge_length = max(10, weight * 5)  # Scale length, ensuring a minimum value
        net.add_edge(u, v, title=f"Length: {weight}", label=str(weight), length=edge_length, physics=False, smooth=False)

    output_file = "graph.html"
    net.save_graph(output_file)

    # Get absolute path
    file_path = f"file://{os.path.abspath(output_file)}"

    # Open in Chrome
    chrome_path = "open -a 'Google Chrome'" if os.name == "posix" else "start chrome"
    os.system(f"{chrome_path} {file_path}")

