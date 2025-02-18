```rust
//! The main entry point for the BFS example program
use bfs::BfsError;
use tokio;

#[tokio::main]
async fn main() -> Result<(), BfsError> {
    // Create a sample graph as an adjacency list
    let graph = bfs::create_sample_graph();
    
    // Run BFS from node 0
    let result = bfs::bfs(&graph, 0)?;
    
    println!("Breadth-First Search Result:");
    for (level, nodes) in result.iter().enumerate() {
        println!("Level {}: {:?}", level, nodes);
    }
    
    Ok(())
}
```