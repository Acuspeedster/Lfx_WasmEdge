```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum BfsError {
    #[error("Node {0} not found in graph")]
    NodeNotFound(Node),

    #[error("Graph is empty")]
    EmptyGraph,

    #[error("Invalid edge connection")]
    InvalidEdge,
}
```