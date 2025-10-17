#!/usr/bin/env python3
"""
Block Time Distribution Plotter
Creates text-based plots showing how many transactions take how long
"""

import json
import os
from datetime import datetime
import statistics

def load_latest_data(data_dir="data"):
    """Load the latest test data"""
    files = os.listdir(data_dir)
    test_files = [f for f in files if f.startswith('p2s_performance_test_')]
    
    if not test_files:
        print("No test data found")
        return None
    
    latest_file = max(test_files)
    with open(f"{data_dir}/{latest_file}", 'r') as f:
        return json.load(f)

def percentile(data, percentile):
    """Calculate percentile"""
    sorted_data = sorted(data)
    index = int(len(sorted_data) * percentile / 100)
    return sorted_data[min(index, len(sorted_data) - 1)]

def create_text_plots(data):
    """Create text-based block time distribution plots"""
    p2s_times = [tx['total_duration'] for tx in data['p2s_raw_data']]
    pos_times = [tx['total_duration'] for tx in data['pos_raw_data']]
    
    print("=" * 80)
    print("BLOCK TIME DISTRIBUTION ANALYSIS")
    print("=" * 80)
    
    # Time ranges for analysis
    time_ranges = [
        (0, 0.5, 'Very Fast (<0.5s)'),
        (0.5, 1.0, 'Fast (0.5-1.0s)'),
        (1.0, 1.5, 'Medium (1.0-1.5s)'),
        (1.5, 2.0, 'Slow (1.5-2.0s)'),
        (2.0, 3.0, 'Very Slow (2.0-3.0s)'),
        (3.0, float('inf'), 'Extremely Slow (>3.0s)')
    ]
    
    print(f"\n📊 TRANSACTION COUNT BY BLOCK TIME RANGE")
    print("-" * 60)
    print(f"{'Time Range':<25} {'PoS Count':<12} {'P2S Count':<12} {'Difference':<12}")
    print("-" * 60)
    
    for min_time, max_time, label in time_ranges:
        pos_count = sum(1 for t in pos_times if min_time <= t < max_time)
        p2s_count = sum(1 for t in p2s_times if min_time <= t < max_time)
        diff = p2s_count - pos_count
        
        print(f"{label:<25} {pos_count:<12} {p2s_count:<12} {diff:+d}")
    
    # Create text histogram
    print(f"\n📈 BLOCK TIME DISTRIBUTION HISTOGRAM")
    print("-" * 60)
    
    max_time = max(max(p2s_times), max(pos_times))
    bins = 20
    bin_size = max_time / bins
    
    print(f"PoS Distribution:")
    for i in range(bins):
        bin_start = i * bin_size
        bin_end = (i + 1) * bin_size
        count = sum(1 for t in pos_times if bin_start <= t < bin_end)
        bar = "█" * min(count, 20)  # Limit bar length
        print(f"{bin_start:.2f}-{bin_end:.2f}s: {bar} ({count})")
    
    print(f"\nP2S Distribution:")
    for i in range(bins):
        bin_start = i * bin_size
        bin_end = (i + 1) * bin_size
        count = sum(1 for t in p2s_times if bin_start <= t < bin_end)
        bar = "█" * min(count, 20)  # Limit bar length
        print(f"{bin_start:.2f}-{bin_end:.2f}s: {bar} ({count})")
    
    # Statistical summary
    print(f"\n📊 STATISTICAL SUMMARY")
    print("-" * 60)
    print(f"PoS Statistics:")
    print(f"  Mean: {statistics.mean(pos_times):.3f}s")
    print(f"  Median: {statistics.median(pos_times):.3f}s")
    print(f"  Min: {min(pos_times):.3f}s")
    print(f"  Max: {max(pos_times):.3f}s")
    print(f"  Std Dev: {statistics.stdev(pos_times):.3f}s")
    
    print(f"\nP2S Statistics:")
    print(f"  Mean: {statistics.mean(p2s_times):.3f}s")
    print(f"  Median: {statistics.median(p2s_times):.3f}s")
    print(f"  Min: {min(p2s_times):.3f}s")
    print(f"  Max: {max(p2s_times):.3f}s")
    print(f"  Std Dev: {statistics.stdev(p2s_times):.3f}s")
    
    # Performance comparison
    mean_diff = statistics.mean(p2s_times) - statistics.mean(pos_times)
    mean_diff_pct = (mean_diff / statistics.mean(pos_times)) * 100
    
    print(f"\n⚡ PERFORMANCE COMPARISON")
    print("-" * 60)
    print(f"Mean Block Time Difference: {mean_diff:+.3f}s ({mean_diff_pct:+.1f}%)")
    print(f"P2S is {'slower' if mean_diff > 0 else 'faster'} than PoS")
    
    # Percentile analysis
    print(f"\n📈 PERCENTILE ANALYSIS")
    print("-" * 60)
    percentiles = [50, 75, 90, 95, 99]
    
    print(f"{'Percentile':<12} {'PoS (s)':<12} {'P2S (s)':<12} {'Difference':<12}")
    print("-" * 60)
    
    for p in percentiles:
        pos_p = percentile(pos_times, p)
        p2s_p = percentile(p2s_times, p)
        diff = p2s_p - pos_p
        print(f"{p}th{'':<8} {pos_p:<12.3f} {p2s_p:<12.3f} {diff:+.3f}s")

def main():
    """Main function"""
    data = load_latest_data()
    
    if data:
        create_text_plots(data)
        
        # Save to file
        os.makedirs('plots', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"plots/block_time_distribution_{timestamp}.txt"
        
        # Capture the output
        import sys
        from io import StringIO
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        create_text_plots(data)
        
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # Save to file
        with open(filename, 'w') as f:
            f.write(output)
        
        print(f"\n[SAVE] Text plot saved to {filename}")
    else:
        print("No data available for plotting")

if __name__ == "__main__":
    main()