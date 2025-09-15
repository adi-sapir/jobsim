# A text based histogram class
import argparse
import json
import sys
from typing import List, Any, Tuple

# Handle relative import when run as script vs module
try:
    from .debug_config import debug_print
except ImportError:
    # When run directly as script, debug_print is not available
    def debug_print(*args, **kwargs):
        pass

class SimHistogramBin:
    def __init__(self, min_val: int, max_val: int, print_scale_factor: float, total_data_points_count: int):
        self.min_val: int = min_val
        self.max_val: int = max_val
        self.print_scale_factor: float = print_scale_factor
        self.total_count: int = 0
        self.count_by_types: dict[str, int] = {}
        self.total_data_points_count = total_data_points_count
    def __str__(self):
        column_str = "|" + "█" * int(self.total_count * self.print_scale_factor)
        label_str = f"{self.min_val}-{self.max_val}: {self.total_count} ({self.total_count / self.total_data_points_count * 100:.0f}%)"
        if (len(self.count_by_types) > 0):
            label_str += " " + " ".join([f"({k} {v})" for k, v in self.count_by_types.items()])
        return f"{column_str} {label_str}"
    
    def add_data_point(self, data_type: str) -> None:
      self.total_count += 1
      self.count_by_types[data_type] = self.count_by_types.get(data_type, 0) + 1

class SimHistogram:
    def __init__(self, data: List[Any], bin_count=10):
        self.min_val = min(data)
        self.max_val = max(data)
        self.data_points_count = len(data)
        self.bin_print_max_val = 20
        self.bin_width = int((self.max_val - self.min_val) / bin_count + 1)
        self.bins = [SimHistogramBin(
            self.min_val + i * self.bin_width,
            self.min_val + (i+1) * self.bin_width - 1,
            self.bin_print_max_val / len(data) if len(data) > 0 else 0,
            self.data_points_count) for i in range(bin_count)]
        for val in data:
            idx = int((val - self.min_val) / self.bin_width)
            self.bins[idx].total_count += 1

    def print_histogram(self):
        for bin in self.bins:
            print(f"{bin}")

class SimHistogramStacked:
    def __init__(self, data: List[Tuple[Any, str]], bin_count=10):
        key_values = [item[0] for item in data]
        self.min_val = min(key_values)
        self.max_val = max(key_values)
        self.data_points_count = len(data)
        self.bin_print_max_val = 20
        self.bin_width = int((self.max_val - self.min_val) / bin_count + 1)
        self.bins = [SimHistogramBin(
            self.min_val + i * self.bin_width,
            self.min_val + (i+1) * self.bin_width - 1,
            self.bin_print_max_val / len(data) if len(data) > 0 else 0,
            self.data_points_count) for i in range(bin_count)]
        for val in data:
            idx = int((val[0] - self.min_val) / self.bin_width)
            self.bins[idx].add_data_point(val[1])

    def print_histogram(self):
        for bin in self.bins:
            print(f"{bin}")

def load_data_from_file(filename: str) -> List[Any]:
    """Load data from a JSON file. Supports both simple arrays and arrays of tuples."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("File must contain a JSON array")
        
        return data
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{filename}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading file '{filename}': {e}", file=sys.stderr)
        sys.exit(1)

def is_stacked_data(data: List[Any]) -> bool:
    """Check if data contains tuples (for stacked histogram)."""
    return len(data) > 0 and isinstance(data[0], (list, tuple)) and len(data[0]) == 2

def main():
    parser = argparse.ArgumentParser(description='Generate text-based histograms from data')
    parser.add_argument('--file', '-f', type=str, help='Load data from JSON file')
    parser.add_argument('--bins', '-b', type=int, default=10, help='Number of histogram bins (default: 10)')
    
    args = parser.parse_args()
    
    if args.file:
        # Load data from file
        data = load_data_from_file(args.file)
        
        if is_stacked_data(data):
            # Create stacked histogram
            print(f"Creating stacked histogram from '{args.file}' with {args.bins} bins:")
            stacked_histogram = SimHistogramStacked(data, bin_count=args.bins)
            stacked_histogram.print_histogram()
        else:
            # Create simple histogram
            print(f"Creating histogram from '{args.file}' with {args.bins} bins:")
            histogram = SimHistogram(data, bin_count=args.bins)
            histogram.print_histogram()
    else:
        # Default example data
        print("No file specified, using example data:")
        histogram = SimHistogram([1, 2, 3, 4, 5, 6, 7, 8, 7, 8, 7, 8, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], bin_count=5)
        histogram.print_histogram()
        print("\nStacked histogram example:")
        stacked_histogram = SimHistogramStacked([(1, "A"), (2, "B"), (3, "A"), (4, "B"), (5, "A"), (6, "B"), (7, "A"), (8, "B"), (9, "A"), (10, "B")], bin_count=5)
        stacked_histogram.print_histogram()

if __name__ == "__main__":
    main()
 
