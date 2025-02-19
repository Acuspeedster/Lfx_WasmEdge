import requests
from pathlib import Path
import tarfile

def download_snapshots():
    base_url = "https://huggingface.co/datasets/gaianet/learn-rust/resolve/main"
    snapshots = {
        "rpl-rbe-dar.snapshot.tar.gz": "RPL + RBE + DAR books",
        "rust-qa.snapshot.tar.gz": "Rust QA examples",
        "rpl.snapshot.tar.gz": "The Rust Programming Language",
        "rbe.snapshot.tar.gz": "Rust by Example",
        "rust-books.snapshot.tar.gz": "RPL + RBE combo",
        "learn-rust.snapshot.tar.gz": "Complete knowledge base"
    }

    # Create snapshots directory
    snapshots_dir = Path(__file__).parent / "qdrant_snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    for snapshot_file, description in snapshots.items():
        try:
            print(f"Downloading {description}...")
            response = requests.get(f"{base_url}/{snapshot_file}", stream=True)
            if response.status_code == 200:
                snapshot_path = snapshots_dir / snapshot_file
                
                # Save snapshot file
                with open(snapshot_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extract snapshot
                with tarfile.open(snapshot_path) as tar:
                    tar.extractall(path=snapshots_dir)
                
                print(f"Successfully downloaded and extracted {description}")
            else:
                print(f"Failed to download {snapshot_file}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"Error processing {snapshot_file}: {str(e)}")

if __name__ == "__main__":
    download_snapshots()
