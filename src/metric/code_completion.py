from .base import NLGMetric
from typing import List
import json
import os
import subprocess
import re
import zipfile

class CompletionMetric(NLGMetric):
    """
    RetrievalMetric class for evaluating the correctness of code-generated responses.

    This class parses the predicted value from the generated response and compares it with the label.
    """
    def run_python_script(self, script_path):
        """
        Executes a Python script and captures its standard output and standard error.
        
        Parameters:
            script_path (str): The path to the Python script to be executed.
        
        Returns:
            tuple: A tuple containing the standard output and standard error.
        """
        try:
            result = subprocess.run(['python', script_path], capture_output=True, text=True)
            stdout = result.stdout
            stderr = result.stderr
            return stdout, stderr
        except Exception as e:
            return str(e), ""
    
    def extract_imports(self, ground_truth):
        """
        Extract the imported libs in the ground_truth program.

        Parameters:
            ground_truth (str): ground truth program for this code completion task

        Returns:
            List[str]: a list of imported libraries
        """
        import_pattern = re.compile(r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)', re.MULTILINE)
        matches = import_pattern.findall(ground_truth)
        
        seen = set()
        imports = []
        for match in matches:
            if ('.' in match):
                match = match.split('.')[0]
            if match not in seen:
                seen.add(match)
                imports.append(match)
        
        return imports
    
    def extract_python_code(self, md_content):
        """
        Extract Python code blocks from Markdown content.

        Args:
            md_content (str): The content of the Markdown file.

        Returns:
            List[str]: A list of extracted Python code blocks.
        """
        # Regular expression to match Python code blocks
        if "```python" in md_content:
            code_block_pattern = re.compile(r'```python\s+(.*?)\s+```', re.DOTALL)
            
            # Find all matches
            code_blocks = code_block_pattern.findall(md_content)
            
            return code_blocks
        else:
            md_content = md_content.replace("Here's the completed code snippet:\n\n", "")
            return [md_content]
    
    def Unmask_Api(self, response_code:str, maskedName:dict) -> str:
        """
        Unmask the response_code with masked api.

        Args:
            response_code (str): The response from llm.
            maskedName (dict): The maskName-realName dictionary.

        Returns:
            None.
        """
        sorted_l = sorted(maskedName.items(), key=lambda x: -len(x[1]))
        for key, item in sorted_l:
            response_code = response_code.replace(item, key)
        
        return response_code

    def loadMaskedName(self, libs:List[str]) -> dict:
        """
        Load the maskName-realName dictionary.

        Args:
            libs: a list of libraries to be loaded.
        
        Returns:
            dict: the maskName-realName dictionary.
        """
        py_path = os.path.abspath(__file__)
        py_dir = os.path.dirname(py_path)
        # dict_dir = os.path.join(py_dir, "maskedApi.zip")

        # maskedName = {}

        # for lib in libs:
        #     lib_path = os.path.join(dict_dir, f"maskedName_{lib}.jsonl")
        #     with open(lib_path, 'r', encoding="utf-8") as f:
        #         maskedName.update(json.load(f))
        maskedName = {}
        zip_path = os.path.join(py_dir, "maskedApi.zip")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for lib in libs:
                with zip_ref.open(f"maskedName_{lib}.jsonl") as f:
                    maskedName.update(json.load(f))
        
        return maskedName   
        
    def _evaluate_pair(self, llm_response: str, labels: List[str], *args, **kwargs) -> float:
        # try:
        label = labels[0]
        libs = self.extract_imports(label)
        
        maskedName = self.loadMaskedName(libs)   
        
        output = self.extract_python_code(llm_response)
        output = output[0]
        output = self.Unmask_Api(output, maskedName)

        py_path = os.path.abspath(__file__)
        py_dir = os.path.dirname(py_path)
        test_dir = os.path.join(py_dir, "code_completion_test")
        os.mkdir(test_dir)
        src_path = os.path.join(test_dir, "src.py")
        with open(src_path, 'w', encoding="utf-8") as f:
            f.write(label)
            f.close()
            expected_out, expected_err = self.run_python_script(src_path)

        with open(src_path, 'w', encoding="utf-8") as f:
            f.write(output)
            f.close()
            actual_out, actual_err = self.run_python_script(src_path)
        os.remove(src_path)
        os.rmdir(test_dir)
        # if not (len(actual_err) == 0):
            # return 0.0
        # print(actual_out)
        # print(actual_err)
        
        expected_out = expected_out.split("\n")
        actual_out = actual_out.split("\n")

        # if (not len(expected_out) == len(actual_out)):
        #     return 0.0
        correct = 0
        valid = len(expected_out)
        for i in range(min(len(actual_out), len(expected_out))):
            if (expected_out[i] == actual_out[i]):
                if (expected_out[i] == "\n"):
                    valid -= 1
                else:
                    correct += 1
        
        return correct / valid
        # except Exception as e:
            # return -1

if __name__ == '__main__':
    answer = ["import re\n\n# Text in which substitution is to happen\ntext = 'There are 123 apples and 456 oranges.'\n\n# Pattern and Replacement to be used for substituting matching text\nsub_pattern = r'\\d+'\nreplacement = 'NUM'\n\n## task: substitute the text with the given `sub_pattern` and `replacement`\nresult_1 = re.sub(sub_pattern, replacement, text)\nprint(result_1)\n\n## task: create `Flags` used during pattern compilation for ASCII character classes.\nflags = re.ASCII\nprint(flags)\n\n# Provide: special_chars: Special characters to be escaped in regex pattern.\n\n# A set of special characters to escape\nspecial_chars = r'[].*?'\n\n## task: Escape special characters\nescaped_chars = re.escape(special_chars)\nprint(special_chars)\n\n# Provide: Number Pattern\nnumber_pattern = re.compile(r'\\d+')\n\n## task: find all the numbers in the text\nall_numbers = number_pattern.findall(text)\nprint(all_numbers)\n\n# Provide: Full string to match\nfullmatch_text = 'onlyletters'\n\n# Provide: Compiled pattern for matching\ncompiled_pattern = re.compile(r'[a-zA-Z]+')\n\n## task: Full-match a pattern in the text\nfull_match = compiled_pattern.fullmatch(fullmatch_text)\nprint(full_match)\n\n# Provide: Searching in the text\nsearch_text = 'Searching for the word \"needle\" in a haystack.'\n\n## task: Perform a search for 'needle' in the text\nsearched_word = re.search('needle', search_text)\nprint(searched_word)\n\n# Provide: String to split\nsplit_text = 'Split,this,string,by,commas.'\n\n## task: Split a string based on a delimiter\nsplit_result = re.split(',', split_text)\nprint(split_result)"]
    llm_response = r"""
```python
import lib_2

# Text in which substitution is to happen
text = 'Thelib_2 alib_2 123 apples and 456 oranges.'

# Pattern and Replacement to be used for substituting matching text
sub_pattern = r'\d+'
lib_2placement = 'NUM'

## task: substitute the text with the given `sub_pattern` and `lib_2placement`
lib_2sult_1 = lib_2.func_10(sub_pattern, lib_2placement, text)
print(lib_2sult_1)

## task: clib_2ate `Flags` used during pattern compilation for ASCII character classes.
flags = lib_2.submodule_2.ASCII
print(flags)

# Provide: special_chars: Special characters to be escaped in lib_2gex pattern.

# A set of special characters to escape
special_chars = r'[].*?'

## task: Escape special characters
escaped_chars = lib_2.func_2(special_chars)
print(escaped_chars)

# Provide: Number Pattern
number_pattern = lib_2.func_1(r'\d+')

## task: find all the numbers in the text
all_numbers = lib_2.func_3(number_pattern, text)
print(all_numbers)

# Provide: Full string to match
fullmatch_text = 'onlyletters'

# Provide: Compiled pattern for matching
compiled_pattern = lib_2.func_1(r'[a-zA-Z]+')

## task: Full-match a pattern in the text
full_match = lib_2.func_5(compiled_pattern, fullmatch_text)
print(full_match)

# Provide: Searching in the text
search_text = 'Searching for the word "needle" in a haystack.'

## task: Perform a search for 'needle' in the text
searched_word = lib_2.func_8(r'needle', search_text)
print(searched_word)

# Provide: String to split
split_text = 'Split,this,string,by,commas.'

## task: Split a string based on a delimiter
split_lib_2sult = lib_2.func_9(r',', split_text)
print(split_lib_2sult)
```
    """
    metric = CompletionMetric()
    print(metric._evaluate_pair(llm_response, answer))
