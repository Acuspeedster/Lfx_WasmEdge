```rust
#[cfg(test)]
mod tests {
    use super::*;
    use serde_json;

    #[test]
    fn test_bfs() -> Result<(), BfsError> {
        let mut graph = Graph::new();
        let node_a = Node::new("A");
        
        graph.add_edge(node_a.clone(), Node::new("B"))?;
        graph.add_edge(node_a.clone(), Node::new("C"))?;
        
        let result = bfs(&node_a, &graph).await?;
        assert!(!result.is_empty());
        Ok(())
    }

    #[test]
    #[should_panic(expected = "NodeNotFound")]
    fn test_empty_graph() {
        bfs(&Node::new("A"), &Graph::new()).await;
    }
}
```