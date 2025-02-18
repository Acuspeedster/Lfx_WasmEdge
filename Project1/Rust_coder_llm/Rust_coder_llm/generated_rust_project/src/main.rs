use std::collections::BinaryHeap;
use std::cmp::Reverse;

/// Represents a graph using an adjacency list
struct Graph {
adjacency_list: Vec<Vec<(usize, u32)>>,
num_nodes: usize,
}

impl Graph {
/// Creates a new empty graph with the specified number of nodes
fn new(num_nodes: usize) -> Self {
Self {
adjacency_list: vec![Vec::new(); num_nodes],
num_nodes,
}
}

/// Adds a directed edge with weight between two nodes
fn add_edge(&mut self, from: usize, to: usize, weight: u32) {
self.adjacency_list[from].push((to, weight));
}

/// Dijkstra's algorithm implementation
fn dijkstra(&self, start_node: usize) -> Vec<Option<u32>> {
let mut distances = vec![None; self.num_nodes];
let mut visited = vec![false; self.num_nodes];
let mut priority_queue = BinaryHeap::new();

distances[start_node] = Some(0);
priority_queue.push(Reverse((0, start_node)));

while let Some(Reverse((current_dist, current_node))) = priority_queue.pop() {
if visited[current_node] {
continue;
}

visited[current_node] = true;

for &(neighbor, weight) in &self.adjacency_list[current_node] {
if let Some(dist) = distances[current_node] {
let new_dist = dist + weight;
if distances[neighbor].is_none() || new_dist < distances[neighbor].unwrap() {
distances[neighbor] = Some(new_dist);
priority_queue.push(Reverse((new_dist, neighbor)));
}
}
}
}

distances
}
}

fn main() {
let mut graph = Graph::new(6);

// Example graph setup using adjacency list
graph.add_edge(0, 1, 4);
graph.add_edge(0, 2, 2);
graph.add_edge(1, 3, 5);
graph.add_edge(2, 3, 1);
graph.add_edge(1, 4, 10);
graph.add_edge(3, 4, 2);
graph.add_edge(3, 5, 3);
graph.add_edge(2, 5, 8);
graph.add_edge(4, 5, 6);

println!("Dijkstra's Algorithm Test");
println!("Shortest paths from node 0:");

let distances = graph.dijkstra(0);

for (node, distance) in distances.iter().enumerate() {
if let Some(dist) = distance {
println!("Shortest path from node 0 to node {}: {}", node, dist);
} else {
println!("No path exists from node 0 to node {}", node);
}
}
}