```rust
use thiserror::Error;

/// Custom error type for BFS-related operations
#[derive(Debug, Error)]
pub enum BfsError {
    #[error("Graph is empty")]
    EmptyGraph,
    #[error("Invalid node ID")]
    InvalidNodeId,
}

/// Represents a graph using an adjacency list
pub type Graph = Vec<Vec<i32>>;

/// Creates a sample graph with 5 nodes
pub fn create_sample_graph() -> Graph {
    vec![
        vec![1, 2],    // Node 0
        vec![0, 3],    // Node 1
        vec![0, 4],    // Node 2
        vec![1],       // Node 3
        vec![2],       // Node 4
    ]
}

/// Performs BFS starting from the given node
pub fn bfs(graph: &Graph, start_node: i32) -> Result<Vec<Vec<i32>>, BfsError> {
    if graph.is_empty() {
        return Err(BfsError::EmptyGraph);
    }

    let node_count = graph.len() as i32;
    if start_node < 0 || start_node >= node_count {
        return Err(BfsError::InvalidNodeId);
    }

    let mut visited = vec![false; node_count as usize];
    let mut result = Vec::new();
    let mut queue = Vec::new();

    visited[start_node as usize] = true;
    queue.push(start_node);

    while !queue.is_empty() {
        let mut current_level = Vec::new();
        let level_size = queue.len();
        
        for _ in 0..level_size {
            let node = queue.remove(0);
            current_level.push(node);
        }

        result.push(current_level);

        // Add all unvisited neighbors to the queue
        for node in &current_level {
            for neighbor in &graph[*node as usize] {
                if !visited[*neighbor as usize] {
                    visited[*neighbor as usize] = true;
                    queue.push(*neighbor);
                }
            }
        }
    }

    Ok(result)
}
```