"""Script for LLM task evaluation with concise structure."""

import sys
import json
from src.llm.call import llm_generate
from src.metric.code_completion import CompletionMetric
from src.metric.table_sql import SQLMetric
from src.metric.history_reorder import HistoryReorderMetric
from src.metric.wiki_retrieval import WikiQAMetric

def parse_args():
    """Parse command-line arguments."""
    task_name = sys.argv[1]
    seed_num = int(sys.argv[2])
    random_sd_num = int(sys.argv[3])
    model_name = sys.argv[4]
    return task_name, seed_num, random_sd_num, model_name

def generate_random_seeds(base, count):
    """Generate a list of random seeds starting from a base value."""
    return [base + i for i in range(count)]

def load_json(file_path):
    """Load a JSON file and return its content."""
    with open(file_path) as f:
        return json.load(f)

def filter_data(data, target_level, target_seed, token_level):
    """Filter data based on level, seed, and token level."""
    return [
        datum for datum in data
        if datum['level'] in target_level and datum['seed_id'] in target_seed and datum['token_level'] == token_level
    ]

def prepare_input_list(data):
    """Prepare input list for LLM inference."""
    inputs = []
    for datum in data:
        inputs.append({
            'system_prompt': datum['default_prompt']['system_prompt'],
            'user_message': datum['default_prompt']['user_message'].format(
                context=datum['context'], query=datum['question']
            )
        })
    return inputs

def get_metric(task_name):
    """Return the appropriate metric class based on task name."""
    metrics = {
        'code_completion': CompletionMetric,
        'table_sql': SQLMetric,
        'history_reorder': HistoryReorderMetric,
        'wiki_qa': WikiQAMetric
    }
    return metrics.get(task_name, lambda: None)()

def evaluate(data, outputs, metric, task_name):
    """Evaluate outputs and print results."""
    res_list = []
    for input_instance, output_instance in zip(data, outputs):
        res = (
            metric._evaluate_pair(output_instance, input_instance['answers'])
            if task_name != 'history_reorder'
            else metric._evaluate_pair(output_instance, input_instance['answers'], input_instance['question'])
        )
        res_instance = {}
        res_instance['seed_id'] = input_instance['seed_id']
        res_instance['level'] = input_instance['level']
        res_instance['type'] = input_instance['type']
        res_instance['token_level'] = input_instance['token_level']
        res_instance['llm_output'] = output_instance
        res_instance['metric_result'] = res
        res_list.append(res_instance)
    return res_list

def main():
    
    """Main function to execute the script."""
    task_name, seed_num, random_sd_num, model_name = parse_args()
    random_sd_list = generate_random_seeds(42, random_sd_num)
    
    # save dir
    save_dir = f'res/{task_name}_{model_name}_dsd{seed_num}_rsd{random_sd_num}'
    # make dir if not exist
    import os
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # File paths
    json_path_absolute = f"data/{task_name}_absolute.json"
    json_path_relative = f"data/{task_name}_relative.json"

    # Load data
    data_absolute = load_json(json_path_absolute)
    data_relative = load_json(json_path_relative)

    # Filter data
    # target_level = [f'level {i}' for i in ('1', '4', '8', '12', '16')]  # debug, for full set, from 1 to 16
    target_level = [f'level {i}' for i in range(1, 17)]
    target_seed = [f'{task_name}_{seed}' for seed in range(1, seed_num + 1)]
    token_level = 32000
    target_data_absolute = filter_data(data_absolute, target_level, target_seed, token_level)
    target_data_relative = filter_data(data_relative, target_level, target_seed, token_level)

    # Prepare inputs
    input_lists_absolute = prepare_input_list(target_data_absolute)
    input_lists_relative = prepare_input_list(target_data_relative)

    # Get metric
    metric = get_metric(task_name)

    # LLM inference and evaluation
    for random_sd in random_sd_list:
        
        specific_save_dir_absolute = f'{save_dir}/rsd_{random_sd}_absolute'
        specific_save_dir_relative = f'{save_dir}/rsd_{random_sd}_relative'
        
        output_lists_absolute = llm_generate(input_lists_absolute, model=model_name, seed=random_sd)
        output_lists_relative = llm_generate(input_lists_relative, model=model_name,seed=random_sd)

        res_absolute = evaluate(target_data_absolute, output_lists_absolute, metric, task_name)
        res_relative = evaluate(target_data_relative, output_lists_relative, metric, task_name)
        
        with open(f'{specific_save_dir_absolute}.json', 'w') as f:
            json.dump(res_absolute, f, indent=4)
        with open(f'{specific_save_dir_relative}.json', 'w') as f:
            json.dump(res_relative, f, indent=4)

if __name__ == "__main__":
    main()
