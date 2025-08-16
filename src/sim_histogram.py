# A text based histogram class
from typing import List, Any
from debug_config import debug_print

class SimHistogramBin:
    def __init__(self, min_val: int, max_val: int, print_scale_factor: float):
        self.min_val: int = min_val
        self.max_val: int = max_val
        self.print_scale_factor: float = print_scale_factor
        self.count: int = 0
        self.label: str = f"{min_val}-{max_val}"
    def __str__(self):
        column_str = "|" + "█" * int(self.count * self.print_scale_factor)
        return f"{column_str} {self.label}: {self.count}"


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
            self.bins[idx].count += 1

    def print_histogram(self):
        for bin in self.bins:
            print(f"{bin}")

if __name__ == "__main__":
    histogram = SimHistogram([1, 2, 3, 4, 5, 6, 7, 8, 7, 8, 7, 8, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], bin_count=5)
    histogram.print_histogram()
 
