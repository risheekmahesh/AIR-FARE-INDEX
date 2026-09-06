from pathlib import Path
from app.data import ensure_seed_file

if __name__ == "__main__":
    target = ensure_seed_file(Path(__file__).resolve().parents[1] / "data" / "sample" / "fares.csv")
    print(f"Seeded {target}")
