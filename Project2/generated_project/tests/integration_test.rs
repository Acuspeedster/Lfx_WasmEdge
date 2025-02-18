```rust
#[Cfg(test)]
mod integration_tests {
    use super::*;

    #[test]
    fn test_bfs() -> Result<(), BfsError> {
        let graph = create_sample_graph();
        
        // Test BFS starting from node 0
        let result = bfs(&graph, 0)?;
        assert_eq!(result.len(), 3);
        assert_eq!(result[0], vec![0]);
        assert_eq!(result[1], vec![1, 2]);
        assert_eq!(result[2], vec![3, 4]);
        
        // Test error handling - empty graph
        let empty_result = bfs(&vec![], 0);
        assert!(matches!(empty_result, Err(BfsError::EmptyGraph)));
        
        // Test error handling - invalid node ID
        let invalid_node_result = bfs(&graph, 10);
        assert!(matches!(invalid_node_result, Err(BfsError::InvalidNodeId)));
        
        Ok(())
    }
}
```