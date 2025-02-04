// Common Rust Patterns

// Error Handling Pattern
pub fn result_example() -> Result<String, Box<dyn std::error::Error>> {
    let file = File::open("example.txt")?;
    Ok("Success".to_string())
}

// Smart Pointer Pattern
pub struct CustomBox<T>(Box<T>);

impl<T> CustomBox<T> {
    pub fn new(value: T) -> Self {
        CustomBox(Box::new(value))
    }
}

// Thread-safe Pattern
use std::sync::{Arc, Mutex};

pub fn thread_safe_counter() -> Arc<Mutex<i32>> {
    Arc::new(Mutex::new(0))
}

// WASM Integration Pattern
#[wasmedge_bindgen]
pub fn wasm_function(input: i32) -> i32 {
    input * 2
}