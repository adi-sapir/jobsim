# A text based histogram class
from typing import List, Any, Tuple
from debug_config import debug_print

class SimHistogramBin:
    def __init__(self, min_val: int, max_val: int, print_scale_factor: float):
        self.min_val: int = min_val
        self.max_val: int = max_val
        self.print_scale_factor: float = print_scale_factor
        self.total_count: int = 0
        self.count_by_types: dict[str, int] = {}
    def __str__(self):
        column_str = "|" + "█" * int(self.total_count * self.print_scale_factor)
        label_str = f"{self.min_val}-{self.max_val}: {self.total_count}"
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
        self.bin_print_max_val = 20
        self.bin_width = int((self.max_val - self.min_val) / bin_count + 1)
        self.bins = [SimHistogramBin(
            self.min_val + i * self.bin_width,
            self.min_val + (i+1) * self.bin_width - 1,
            self.bin_print_max_val / len(data) if len(data) > 0 else 0) for i in range(bin_count + 1)]
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
        self.bin_print_max_val = 20
        self.bin_width = int((self.max_val - self.min_val) / bin_count + 1)
        self.bins = [SimHistogramBin(
            self.min_val + i * self.bin_width,
            self.min_val + (i+1) * self.bin_width - 1,
            self.bin_print_max_val / len(data) if len(data) > 0 else 0) for i in range(bin_count + 1)]
        for val in data:
            idx = int((val[0] - self.min_val) / self.bin_width)
            self.bins[idx].add_data_point(val[1])

    def print_histogram(self):
        for bin in self.bins:
            print(f"{bin}")

if __name__ == "__main__":
    histogram = SimHistogram([1, 2, 3, 4, 5, 6, 7, 8, 7, 8, 7, 8, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], bin_count=5)
    histogram.print_histogram()
    stacked_histogram = SimHistogramStacked([(1, "A"), (2, "B"), (3, "A"), (4, "B"), (5, "A"), (6, "B"), (7, "A"), (8, "B"), (9, "A"), (10, "B")], bin_count=5)
    stacked_histogram.print_histogram()
 
