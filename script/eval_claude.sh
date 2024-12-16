#!/bin/bash

# Define the tasks to be executed sequentially
tasks=("code_completion", "history_reorder", "table_sql", "wiki_qa")

# Define the model and random seed
model="claude-3-haiku-20240307"
random_seed_num=8

data_seed_num=$1

if [ -z "$data_seed_num" ]; then
    echo "Usage: $0 <data_seed_num>"
    exit 1
fi

# Loop through each task and execute the command
for task_name in "${tasks[@]}"; do
    echo "Running task: $task_name with data_seed_num: $data_seed_num"
    python -m script.eval $task_name $data_seed_num $random_seed_num $model

    if [ $? -ne 0 ]; then
        echo "Error occurred while running task: $task_name"
        exit 1
    fi
    echo "Task $task_name completed successfully.\n"
done
