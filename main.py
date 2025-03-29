import networkx as nx
import random
from pyvis.network import Network
import os
import webbrowser
import tkinter as tk
from tkinter import ttk
# List of 50 unique locations
locations = [f"Location {i+1}" for i in range(500)]

# Graph size options
graph_sizes = {"small": 10, "medium": 25, "large": 50}

def generate_graph(size, max_degree=5):
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
        if random.random() < 0.3:  
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
        adj_list[v].append((u, weight))  # Undirected graph

    return adj_list


def print_degree_distribution(G):
    """Prints the distribution of node degrees in the graph."""
    degree_count = {}

    # Count occurrences of each degree
    for node in G.nodes():
        degree = G.degree[node]
        degree_count[degree] = degree_count.get(degree, 0) + 1

    # Print sorted results
    for degree in sorted(degree_count):
        print(f"{degree_count[degree]} nodes have {degree} edges")


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

# UI Function
def generate_and_show_graph():
    global current_graph
    size = size_var.get()
    current_graph = generate_graph(size)
    visualize_graph(current_graph)

    # Update the starting node dropdown with available nodes
    starting_node_dropdown["values"] = list(current_graph.nodes())
    starting_node_var.set("")  # Reset selection

# Function to set the starting node
def set_starting_node():
    node = starting_node_var.get()
    if node in current_graph.nodes:
        visualize_graph(current_graph, starting_node=node)

class AutocompleteCombobox(ttk.Combobox):
    def set_completion_list(self, completion_list):
        """Sets up autocomplete for the given list."""
        self._completion_list = sorted(completion_list)  # Sort for better UX
        self._hits = []
        self._hit_index = 0
        self._typed = ""
        self['values'] = self._completion_list
        self.bind('<KeyRelease>', self._on_keyrelease)

    def _on_keyrelease(self, event):
        """Handles key releases for autocomplete."""
        if event.keysym in ("BackSpace", "Delete"):
            self._typed = self.get()
        else:
            self._typed = self.get() + event.char

        if self._typed == "":
            self['values'] = self._completion_list
            return

        # Filter suggestions based on input
        self._hits = [item for item in self._completion_list if item.lower().startswith(self._typed.lower())]

        if self._hits:
            self['values'] = self._hits
            self.event_generate('<Down>')  # Open dropdown


# Create UI using Tkinter
root = tk.Tk()
root.title("Graph Visualization UI")
root.geometry("300x250")

# Dropdown for graph size
tk.Label(root, text="Select Graph Size:").pack(pady=5)
size_var = tk.StringVar(value="small")
size_dropdown = ttk.Combobox(root, textvariable=size_var, values=list(graph_sizes.keys()), state="readonly")
size_dropdown.pack(pady=5)

# Button to generate graph
generate_button = tk.Button(root, text="Generate Graph", command=generate_and_show_graph)
generate_button.pack(pady=10)

# Dropdown for selecting starting node
tk.Label(root, text="Select Starting Node:").pack(pady=5)
starting_node_var = tk.StringVar(value="")
starting_node_dropdown = AutocompleteCombobox(root, textvariable=starting_node_var, state="normal")
starting_node_dropdown.pack(pady=5)

# Button to set the starting node
starting_node_button = tk.Button(root, text="Set Starting Node", command=set_starting_node)
starting_node_button.pack(pady=10)

# Run UI
root.mainloop()
