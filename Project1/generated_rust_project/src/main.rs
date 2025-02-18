//! A simple hello world program demonstrating Rust best practices

use thiserror::Error;

#[derive(Debug, Error)]
pub enum HelloError {
    #[error("Parse error: {0}")]
    ParseError(String),
}

fn greet(name: &str) -> Result<String, HelloError> {
    if name.chars().all(char::is_alphabetic) {
        Ok(format!("Hello, {}!", name))
    } else {
        Err(HelloError::ParseError(
            "Name should only contain alphabetic characters".to_string(),
        ))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_greet() {
        assert_eq!(
            greet("Alice").unwrap(),
            "Hello, Alice!".to_string()
        );
        
        assert!(matches!(
            greet("Alice1"),
            Err(HelloError::ParseError(_))
        ));
    }
}

fn main() {
    match greet("World") {
        Ok(message) => println!("{}", message),
        Err(e) => eprintln!("Error: {}", e),
    }
}