import tkinter as tk
import networkx as nx
from tkinter import ttk
import graph


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


def main():
    global current_graph
    current_graph = nx.Graph()
    # UI Function
    def generate_and_show_graph():
        global current_graph
        size = size_var.get()
        current_graph = graph.generate_graph(size)
        graph.visualize_graph(current_graph)

        # Update the starting node dropdown with available nodes
        node_list = list(current_graph.nodes())
        starting_node_dropdown.set_completion_list(node_list)  # Properly set autocomplete list
        starting_node_var.set("")  # Reset selection

        print("Adjacency list:")
        graph.graph_to_adjacency_list(current_graph)

        print("-" * 20)
        print("-" * 20)
        print("Degree distritbution")
        graph.print_degree_distribution(current_graph)



    # Function to set the starting node
    def set_starting_node():
        node = starting_node_var.get()
        if node in current_graph.nodes:
            graph.visualize_graph(current_graph, starting_node=node)

    # Create UI using Tkinter
    root = tk.Tk()
    root.title("Post man problem")
    root.geometry("300x250")

    # Dropdown for graph size
    tk.Label(root, text="Select Graph Size:").pack(pady=5)
    size_var = tk.StringVar(value="small")
    size_dropdown = ttk.Combobox(root, textvariable=size_var, values=list(graph.graph_sizes.keys()), state="readonly")
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

main()
