#!/bin/bash

# Script to process profile simulation detailed files and generate 3 output files
# Usage: ./process_load_results.sh profile_simulation_detailed_files_<date>_<number>.json

if [ $# -ne 1 ]; then
    echo "Usage: $0 profile_simulation_detailed_files_<date>_<number>.json"
    echo "Example: $0 profile_simulation_detailed_files_20250911_114818.json"
    exit 1
fi

INPUT_FILE="$1"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' not found"
    exit 1
fi

# Extract date from filename (assuming format: profile_simulation_detailed_files_YYYYMMDD_HHMMSS.json)
DATE=$(echo "$INPUT_FILE" | sed -E 's/.*profile_simulation_detailed_files_([0-9]{8})_[0-9]+\.json/\1/')

if [ "$DATE" = "$INPUT_FILE" ]; then
    echo "Error: Could not extract date from filename. Expected format: profile_simulation_detailed_files_YYYYMMDD_HHMMSS.json"
    exit 1
fi

echo "Processing file: $INPUT_FILE"
echo "Extracted date: $DATE"

# Generate latency_and_size_<date>.json
echo "Generating latency_and_size_${DATE}.json..."
jq '[to_entries[] | [.value.latency, .value.file_type]]' < "$INPUT_FILE" | sed -E 's/\..*,/,/g' > "latency_and_size_${DATE}.json"

# Generate processing_duration_and_size_<date>.json
echo "Generating processing_duration_and_size_${DATE}.json..."
jq '[to_entries[] | [.value.processing_duration, .value.file_type]]' < "$INPUT_FILE" | sed -E 's/\..*,/,/g' > "processing_duration_and_size_${DATE}.json"

# Generate profile_simulation_<date>_short.json
echo "Generating profile_simulation_${DATE}_short.json..."
jq '[.[]|{file_id,submission_time,file_type,processing_start_time,processing_complete_time}]' < "$INPUT_FILE" | sed -e 's/\.[0-9]*//g' > "profile_simulation_${DATE}_short.json"

echo "Processing complete! Generated files:"
echo "- latency_and_size_${DATE}.json"
echo "- processing_duration_and_size_${DATE}.json"
echo "- profile_simulation_${DATE}_short.json"

# Create analysis file
ANALYSIS_FILE="load_tests_analysis_${DATE}.txt"
echo "Creating analysis file: $ANALYSIS_FILE"

# Add header to analysis file
cat > "$ANALYSIS_FILE" << EOF
Load Test Analysis - $DATE
Generated on: $(date)
Input file: $INPUT_FILE

================================================================================
EOF

# Step 1: Run histogram analysis for processing duration
echo ""
echo "Step 1: Running histogram analysis for processing duration..."
echo "================================================================================" >> "$ANALYSIS_FILE"
echo "PROCESSING DURATION HISTOGRAM" >> "$ANALYSIS_FILE"
echo "================================================================================" >> "$ANALYSIS_FILE"
python -m jobsim.sim_histogram --file "processing_duration_and_size_${DATE}.json" --bins 20 >> "$ANALYSIS_FILE" 2>&1

# Step 2: Run histogram analysis for latency
echo ""
echo "Step 2: Running histogram analysis for latency..."
echo "" >> "$ANALYSIS_FILE"
echo "================================================================================" >> "$ANALYSIS_FILE"
echo "LATENCY HISTOGRAM" >> "$ANALYSIS_FILE"
echo "================================================================================" >> "$ANALYSIS_FILE"
python -m jobsim.sim_histogram --file "latency_and_size_${DATE}.json" --bins 20 >> "$ANALYSIS_FILE" 2>&1

# Step 3: Run job scheduling view
echo ""
echo "Step 3: Running job scheduling view..."
echo "" >> "$ANALYSIS_FILE"
echo "================================================================================" >> "$ANALYSIS_FILE"
echo "JOB SCHEDULING VIEW" >> "$ANALYSIS_FILE"
echo "================================================================================" >> "$ANALYSIS_FILE"
python -m jobsim.job_secheduling_view --file "profile_simulation_${DATE}_short.json" --step 10 >> "$ANALYSIS_FILE" 2>&1

echo ""
echo "Analysis complete! Results saved to: $ANALYSIS_FILE"
