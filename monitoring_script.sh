#!/bin/bash

# Configuration
AB_CMD="ab"
AB_URL="http://91.123.202.165"  # Replace with your server URL
CONCURRENCY=10
CPU_THRESHOLD=85
MEMORY_THRESHOLD=85
INTERVAL=60  # Time interval (in seconds) between checks
MAX_REQUESTS=10000  # Maximum number of requests to simulate

# Output file
SUMMARY_FILE="benchmark_summary.txt"

# Function to get CPU and memory utilization from the server
get_utilization() {
    local server_ip=$1
    # Replace 'user' with your actual SSH username
    cpu_usage=$(ssh -o StrictHostKeyChecking=no user@$server_ip "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\([0-9.]*\)%* id.*/\1/' | awk '{print 100 - $1}'")
    mem_usage=$(ssh -o StrictHostKeyChecking=no user@$server_ip "free | grep Mem | awk '{print ($3/$2) * 100.0}'")
    echo "$cpu_usage $mem_usage"
}

# Function to check if utilization exceeds thresholds
check_utilization() {
    local cpu_usage=$1
    local mem_usage=$2
    
    if (( $(echo "$cpu_usage >= $CPU_THRESHOLD" | bc -l) )) && \
       (( $(echo "$mem_usage >= $MEMORY_THRESHOLD" | bc -l) )); then
        return 0  # Threshold exceeded
    else
        return 1  # Threshold not exceeded
    fi
}

# Function to calculate mean and standard deviation from Apache Benchmark results
calculate_mean_and_sd() {
    local results_file=$1
    # Adjust grep and awk commands based on the actual output format
    mean=$(grep "Time per request" $results_file | grep "(mean)" | awk '{print $4}')
    sd=$(grep "Time per request" $results_file | grep "(mean, across all concurrent requests)" | awk '{print $7}')
    echo "$mean $sd"
}

# Initialize the summary file
echo "N,C,Mean(msec),SD(msec),CPU(%),Memory(%)" > $SUMMARY_FILE

# Main script
while true; do
    echo "Starting benchmark with $CONCURRENCY concurrent connections..."
    
    # Run Apache Benchmark with increasing number of requests
    for requests in $(seq 1000 $CONCURRENCY $MAX_REQUESTS); do
        echo "Simulating $requests requests with $CONCURRENCY concurrent connections"
        $AB_CMD -n $requests -c $CONCURRENCY $AB_URL > benchmark_temp_results.txt

        # Calculate mean and standard deviation
        mean_sd=$(calculate_mean_and_sd benchmark_temp_results.txt)
        mean=$(echo $mean_sd | awk '{print $1}')
        sd=$(echo $mean_sd | awk '{print $2}')

        echo "Checking CPU and memory utilization..."
        server_ips=$(openstack server list -f value -c Networks | awk -F"'" '{print $2}' | cut -d',' -f1 | sed "s/^\[\(.*\)\]$/\1/")
        
        for server_ip in $server_ips; do
            # Remove potential extra quotes or brackets
            server_ip=$(echo $server_ip | tr -d "'[]")
            utilization=$(get_utilization $server_ip)
            cpu_usage=$(echo $utilization | awk '{print $1}')
            mem_usage=$(echo $utilization | awk '{print $2}')
            
            echo "$requests,$CONCURRENCY,$mean,$sd,$cpu_usage,$mem_usage" >> $SUMMARY_FILE

            if check_utilization $cpu_usage $mem_usage; then
                echo "CPU or memory utilization has reached or exceeded $CPU_THRESHOLD%. Stopping benchmark."
                exit 0
            fi
        done

        # Wait before the next iteration
        echo "Waiting for $INTERVAL seconds before next iteration..."
        sleep $INTERVAL
    done
done
