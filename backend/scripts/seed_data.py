"""
Backend Forwarder / Runner for Community Food Rescue Network Synthetic Seeder.
Invokes the canonical seeder in the root scripts/ directory.
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.seed_data import (
    seed_synthetic_data,
    clean_synthetic_data,
    ALL_SYNTHETIC_EMAILS,
    SYNTHETIC_DONORS,
    SYNTHETIC_NGOS,
    SYNTHETIC_VOLUNTEERS,
)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed synthetic data for Community Food Rescue Network.")
    parser.add_argument("--clean", action="store_true", help="Remove only the synthetic demo data from MySQL.")
    parser.add_argument("--refresh", action="store_true", help="Clean and re-seed fresh synthetic data.")
    args = parser.parse_args()

    if args.clean:
        clean_synthetic_data()
    elif args.refresh:
        clean_synthetic_data()
        seed_synthetic_data()
    else:
        seed_synthetic_data()
