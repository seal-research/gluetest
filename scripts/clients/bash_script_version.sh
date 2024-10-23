#!/bin/bash

# File containing the list of repositories which generate by selenium.py
REPO_LIST="/home/root1/projects/clientreadme/collab/task5/clients/clean.csv"
# Output CSV file
OUTPUT_CSV="/home/root1/projects/clientreadme/collab/task5/clients/final_cli.csv"

# Counter to limit to the first 300 URLs
count=0

# Read each line from the CSV file
while IFS=, read -r repo_url; do
    # Break the loop if 300 URLs have been processed, you can modified the number to processed
    # different number of project
    if (( count >= 300 )); then
        break
    fi
    # Increment the counter
    ((count++))

    # Extract repository name from URL
    repo_name=$(basename "$repo_url" .git)

    # Clone the repository
    git clone --depth 1 "$repo_url" "$repo_name"
    
    # Navigate into the repository
    cd "$repo_name" || continue

    # Get the version of commons-csv, you can modfied commons-cli to other, like commons-csv
    version=$(mvn help:effective-pom | grep -A1 '>commons-cli<' | grep version | sed 's/ //g' | sort -u)

    # Write to the output CSV
    if [[ -z "$version" ]]; then
        echo "$repo_url,none" >> "$OUTPUT_CSV"
    else
        echo "$repo_url,$version" >> "$OUTPUT_CSV"
    fi

    # Navigate back to the original directory
    cd ..

    # Optionally, remove the cloned repository to save space
    rm -rf "$repo_name"
done < "$REPO_LIST"
