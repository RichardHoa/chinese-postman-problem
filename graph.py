import networkx as nx
import random
from pyvis.network import Network
import os
import itertools
from collections import defaultdict
from networkx.algorithms.matching import min_weight_matching

# List of 50 unique locations
locations = [f"Location {i+1}" for i in range(50)]

# Graph size options
graph_sizes = {"small": 10, "medium": 25, "large": 50}

CHANCES = 0.5

MAX_DEGREE = 5

def generate_weight_for_node():
    return round(random.uniform(1.0, 10.0), 1)

def generate_graph(size, max_degree=MAX_DEGREE):
    # Generates a connected graph with controlled max degree.
    num_nodes = graph_sizes[size]
    # Get unique names
    selected_locations = random.sample(locations, num_nodes)

    # Create an empty graph and add nodes
    G = nx.Graph()
    G.add_nodes_from(selected_locations)

    # Step 1: Create a spanning tree (ensures connectivity)
    remaining_nodes = set(selected_locations)
    current_node = remaining_nodes.pop()
    
    while remaining_nodes:
        next_node = random.choice(list(remaining_nodes))
        weight = generate_weight_for_node()
        G.add_edge(current_node, next_node, weight=weight)
        current_node = next_node
        remaining_nodes.remove(next_node)

    # Step 2: Add more edges while ensuring degree varies randomly
    nodes = list(G.nodes())
    random.shuffle(nodes)

    for node in nodes:
        if random.random() < CHANCES:  
            max_possible_edges = int(max_degree - G.degree[node])
            if max_possible_edges > 0:
                num_extra_edges = random.randint(1, max_possible_edges)
                possible_nodes = [n for n in nodes if n != node and G.degree[n] < max_degree]

                for _ in range(num_extra_edges):
                    if not possible_nodes:
                        break
                    neighbor = random.choice(possible_nodes)
                    weight = generate_weight_for_node()
                    G.add_edge(node, neighbor, weight=weight)
                    possible_nodes.remove(neighbor)

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


def get_best_matching(G, odd_vertices):
    # Step 1: Build complete graph of odd vertices with shortest path weights
    complete_graph = nx.Graph()
    # basically is C(n,2), u and v are names of vertices
    for u, v in itertools.combinations(odd_vertices, 2):
        try:
            # find the shortest length between two vertices 
            shortest_length = nx.dijkstra_path_length(G, u, v, weight='weight')
            # add the length to the graph
            complete_graph.add_edge(u, v, weight=shortest_length)
        except nx.NetworkXNoPath:
            continue  # skip disconnected pairs

    #  Step 2: pair up all the odd-degree nodes into k/2 
    #   pairs such that the total cost (shortest path lengths) is as small as possible.
    matching = min_weight_matching(complete_graph)
    return list(matching)

def print_postman_chinese_solution(G,start_node):
    original_total_weight = sum(data['weight'] for u, v, data in G.edges(data=True))
    print(f"Original graph total weight: {original_total_weight}")

    # Step 1: Find odd-degree vertices
    odd_vertices = [v for v in G.nodes() if G.degree[v] % 2 == 1]
    print("Odd vertices:", odd_vertices)

    if len(odd_vertices) == 0:
        print("✅ Graph already has all even-degree vertices → Eulerian circuit exists!")
        try:
            circuit = list(nx.eulerian_circuit(G))
            if not circuit:
                print("⚠️ No Eulerian circuit found.")
                return
            route = [circuit[0][0]] + [v for _, v in circuit]
            print("\n🗺️ Eulerian Circuit:")
            print(" → ".join(route))
            print(f"Total cost: {original_total_weight}")
        except nx.NetworkXError as e:
            print("⚠️ Error finding Eulerian circuit:", e)
        return

    # Step 2: Get best matching using Edmonds' algorithm
    # return shortest matching between two odd vertices
    best_matching = get_best_matching(G, odd_vertices)

    # Step 3–4: Compute shortest paths for the matching
    min_total_weight = 0
    best_paths = []

    for u, v in best_matching:
        try:
            length = nx.dijkstra_path_length(G, u, v, weight='weight')
            path = nx.dijkstra_path(G, u, v, weight='weight')
            min_total_weight += length
            best_paths.append((u, v, path, length))
        except nx.NetworkXNoPath:
            print(f"❌ No path found between {u} and {v}")
            print("❌ Matching is invalid.")
            return

    print("\n Best matching with minimum total added weight:")
    for u, v, path, length in best_paths:
        print(f"  Path from {u} to {v}: length {length}; {path}")
    print(f"Total added weight: {min_total_weight}")

    # Step 5: Add shortest paths as multiedges
    G_aug = nx.MultiGraph(G)
    for u, v, path, _ in best_paths:
        for i in range(len(path) - 1):
            u1, v1 = path[i], path[i + 1]
            if G_aug.has_edge(u1, v1):
                weight = G[u1][v1]['weight']
                # Add duplicate for existing edge
                G_aug.add_edge(u1, v1, weight=weight)
            else:
                print(f"⚠️ Trying to add a non-existent edge: {u1} — {v1}")


    # Print degree distribution to make sure we have valid eulerian graph
    print("\nDegree distribution: ")
    print_degree_distribution(G_aug)
    # Step 6: Compute total cost
    chinese_postman_total_cost = original_total_weight + min_total_weight

    print(f"\nChinese Postman Route original total weight: {original_total_weight}")
    print(f"Chinese Postman Route total cost: {chinese_postman_total_cost}")

    # Step 7: Find Eulerian circuit in augmented graph
    # Assume `start_node` is passed in
    try:
        circuit = list(nx.eulerian_circuit(G_aug, source=start_node))
        if not circuit:
            print("⚠️ No Eulerian circuit found in the augmented graph.")
            return
        route = [circuit[0][0]] + [v for _, v in circuit]
        print("\n🗺️ Chinese Postman Route (Eulerian Circuit):")
        print(" → ".join(route))
        print(f"We traverse {len(route)} times")
        visualize_graph(G_aug,route,start_node)
    except nx.NetworkXError as e:
        print("⚠️ Error finding Eulerian circuit:", e)

# Function to visualize the graph
def visualize_graph(G, route=None, starting_node=None):
    net = Network(notebook=False, directed=True)
    net.force_atlas_2based(
        gravity=-100,             # Node repulsion strength (negative = repel)
        central_gravity=0.005,   # How strongly nodes are pulled to center
        spring_length=100,        # Ideal distance between nodes
        spring_strength=0.08,     # Strength of spring force
        damping=0.4,              # Slows down movement (0 to 1)
        overlap=0                 # Prevents node overlap (0 = no overlap)
    )
    net.toggle_physics(True)
    net.show_buttons(filter_=['physics'])

    # Add nodes
    for node in G.nodes():
        color = "red" if node == starting_node else "#1f78b4"
        net.add_node(node, label=str(node), color=color)

    if(route):
        print("We have a route")

    # Add base edges WITH weight labels
    for u, v, data in G.edges(data=True):
        weight = data["weight"]
        edge_length = max(10, weight * 5)
        net.add_edge(
            u, v,
            title=f"Weight: {weight}",
            label=str(weight),
            length=edge_length,
            physics=False,
            smooth=False,
            color="#999"  # gray base edge
        )

    output_file = "graph_with_weights_and_route.html"
    net.save_graph(output_file)

    file_path = f"file://{os.path.abspath(output_file)}"
    chrome_path = "open -a 'Firefox'" if os.name == "posix" else "start Firefox"
    os.system(f"{chrome_path} {file_path}")
