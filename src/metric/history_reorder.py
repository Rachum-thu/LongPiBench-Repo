import re
from .base import NLGMetric
from typing import List

from scipy.stats import spearmanr
from scipy.stats import kendalltau

def sequence_similarity_spearman(gt_list, pred_list):
    # 首先确保两个列表的元素集相同，如果不同可能需要根据任务需求处理
    # 假设元素集合相同且都是独特元素：
    # 为每个元素在真实序列中找到其排名（索引）
    pos_map_gt = {elem: i for i, elem in enumerate(gt_list)}
    pos_gt = []
    pos_pred = []
    
    for elem in pred_list:
        # 将预测序列中的元素位置映射到真实序列中的排名
        pos_gt.append(pos_map_gt[elem])
    # 预测序列本身的索引即为预测排名
    pos_pred = list(range(len(pred_list)))  
    
    # 计算Spearman相关系数
    correlation, _ = spearmanr(pos_gt, pos_pred)
    return correlation


def parse_and_sort_events(llm_response, query):
    # 解析 query，将其转换为 {idx: stripped_string} 的形式
    events = {}
    for line in query.split(';'):
        if not line.strip():
            continue
        idx, content = line.split(':', 1)
        idx = int(idx.strip())
        events[idx] = content.strip()

    # 检索每个字符串在 llm_response 中的位置
    positions = []
    for idx, event_string in events.items():
        position = llm_response.find(event_string)
        positions.append((position, idx))

    # 根据位置排序，从前到后
    sorted_positions = sorted(positions)

    # 返回按顺序的 idx 列表
    sorted_indices = [str(idx) for _, idx in sorted_positions]
    return sorted_indices


def remove_letters_and_strip(input_str: str) -> str:
    """
    Remove all non-numeric, non-comma, and non-space characters from the input string and strip leading and trailing whitespace.

    Parameters:
    input_str (str): The input string to be cleaned.

    Returns:
    str: The cleaned string with only numbers, commas, and spaces.
    """
    # Use regex to remove all characters except digits, commas, and spaces
    cleaned_str = re.sub(r'[^0-9, ]', '', input_str)
    
    # Strip leading and trailing whitespace
    cleaned_str = cleaned_str.strip()
    
    # Additional step: replace multiple spaces with a single space
    cleaned_str = re.sub(r'\s+', ' ', cleaned_str)
    
    return cleaned_str

from scipy.stats import spearmanr

def sequence_similarity_spearman(gt_list, pred_list):
    # 首先确保两个列表的元素集相同，如果不同可能需要根据任务需求处理
    # 假设元素集合相同且都是独特元素：
    # 为每个元素在真实序列中找到其排名（索引）
    pos_map_gt = {elem: i for i, elem in enumerate(gt_list)}
    pos_gt = []
    pos_pred = []
    
    for elem in pred_list:
        # 将预测序列中的元素位置映射到真实序列中的排名
        pos_gt.append(pos_map_gt[elem])
    # 预测序列本身的索引即为预测排名
    pos_pred = list(range(len(pred_list)))  
    
    # 计算Spearman相关系数
    correlation, _ = spearmanr(pos_gt, pos_pred)
    return correlation


class HistoryReorderMetric(NLGMetric):

    def _evaluate_pair(self, llm_response: str, labels: List[str], query: str) -> float:
        """
        Calculate the History Reorder metric for a single pair of generated text and a list of labels.

        Args:
            llm_response (str): The generated text to evaluate.
            labels (List[str]): A list of reference texts. In this task, the list contains a single string with a comma-separated list of indices of the events in the correct order.

        Returns:
            float: The History Reorder metric value between 0.0 and 1.0, representing the proportion of correctly ordered events.
        """
        prefix = llm_response.find('[')
        suffix = llm_response.find(']')
        cut_llm_response = llm_response[prefix:suffix+1]
        if not cut_llm_response:
            cut_llm_response = llm_response

        ground_truth_order_list = labels[0].split(", ")
        
        llm_response_order_list = parse_and_sort_events(cut_llm_response, query)
        if llm_response_order_list == ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            # try this
            try:
                raw_llm_response_order_list = eval(cut_llm_response)
                llm_response_order_list = [str(i) for i in raw_llm_response_order_list]
            except:
                pass

        # remove all the elem in llm that is not in gt
        try:
            tau1, _ = kendalltau(ground_truth_order_list, llm_response_order_list)
            return tau1
        except:
            return 0.0
        
        
        # if len(ground_truth_order_list) != len(llm_response_order_list):
        #     # If the number of events in the ground truth and the generated response are different, return 0.0
        #     return 0.0

        # num_events_to_reorder = len(ground_truth_order_list)
        # num_correct_indices = 0
        # for i in range(num_events_to_reorder):
        #     if ground_truth_order_list[i] == llm_response_order_list[i]:
        #         num_correct_indices += 1
        # breakpoint()
        # return float(num_correct_indices / num_events_to_reorder)


if __name__ == "__main__":
    # Test the HistoryReorderMetric with provided cases
    llm_response = "Here are the events reordered in chronological order:\n\n3: The signing of the Treaty of Greenwater ends the War of the Roses.;  \n0: The unification of the Kingdom of Aedoria was achieved through the Edict of Unison.;  \n5: The fictional Great Reformation of the Church of Light heralded a new era of spiritual practices.;  \n8: The fictional Upheaval of the Red Monarchy.;  \n1: The Aerial Flight of the Albatross, the first recorded successful manned flight.;  \n2: The discovery of the Cerulean Mineral significantly advanced technological progress.;  \n4: The discovery of the lost city of Subterracopia changed historical narratives.;  \n6: The foundation of the fictional City of Harmony symbolized a new era of urban planning and societal integration.;  \n7: The landmark decision from the Court of Harmony transformed civil rights.;  \n9: The radical filmmaker Arman Dorset premiered his highly controversial movie, 'The Last Hope'."
    labels = ['3, 0, 5, 8, 1, 2, 9, 7, 4, 6']
    query = "0: The unification of the Kingdom of Aedoria was achieved through the Edict of Unison.; 1: The Aerial Flight of the Albatross, the first recorded successful manned flight.; 2: The discovery of the Cerulean Mineral significantly advanced technological progress.; 3: The signing of the Treaty of Greenwater ends the War of the Roses.; 4: The discovery of the lost city of Subterracopia changed historical narratives.; 5: The fictional Great Reformation of the Church of Light heralded a new era of spiritual practices.; 6: The foundation of the fictional City of Harmony symbolized a new era of urban planning and societal integration.; 7: The landmark decision from the Court of Harmony transformed civil rights.; 8: The fictional Upheaval of the Red Monarchy.; 9: The radical filmmaker Arman Dorset premiered his highly controversial movie, 'The Last Hope'."

    metric = HistoryReorderMetric()
    results = metric._evaluate_pair(llm_response, labels, query)
    print(results) # Expected output: [0.0, 0.3333333333333333, 0.0]
