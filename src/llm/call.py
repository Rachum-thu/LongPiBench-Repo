import os
import tqdm
from openai import OpenAI
from joblib import Memory
from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

# Load environment variables from a .env file 
load_dotenv()

# Set up caching for function results to avoid redundant API calls
memory = Memory(location=".cache", verbose=0)

# Initialize the OpenAI client with API key and base URL
client = OpenAI(api_key=os.environ.get("YOUR_OPENAI_API_KEY"), base_url=os.environ.get("YOUR_OPENAI_API_BASE_URL"))
# client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def retry_callback(retry_state):
    """
    Callback function for retry logic, providing feedback on retry attempts and exceptions.
    """
    print(
        f"Retrying {retry_state.fn.__name__} due to {retry_state.outcome.exception()}."
    )
    print(
        f"Attempt {retry_state.attempt_number} of {retry_state.retry_object.stop.max_attempt_number}."
    )

@retry(
    reraise=True,  # Reraise the last exception if all retries are exhausted
    stop=stop_after_attempt(32),  # Maximum of 32 retry attempts
    wait=wait_exponential(min=16, max=64),  # Exponential backoff between 16 to 64 seconds
    retry=retry_if_exception_type(Exception),  # Retry for any exception
    before_sleep=retry_callback,  # Call the callback function before each retry
)
@memory.cache  # Cache the results of the function to avoid redundant API calls
def llm_single_generate(
    input_dict,
    model="gpt-4o-mini",
    temp=0.1,
    top_p=0.9,
    seed=42,
):
    """
    Generate a single response using the GPT model.

    Args:
        input_dict (Dict[str, str]): Dictionary containing 'system_prompt' and 'user_message'.
        model (str, optional): Name of the model to use. Defaults to "gpt-4o-mini".
        temp (float, optional): Temperature setting for response generation. Defaults to 0.0.
        top_p (float, optional): Nucleus sampling parameter. Defaults to 0.9.

    Returns:
        str: Response generated by the model.
    """
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": input_dict["system_prompt"],
            },
            {
                "role": "user",
                "content": input_dict["user_message"],
            },
        ],
        model=model,
        temperature=temp,
        top_p=top_p,
        seed=seed,
    )
    return chat_completion.choices[0].message.content

def llm_generate(
    inputs,
    model="gpt-4o-mini",
    temp=0.1,
    top_p=0.9,
    mute_tqdm=False,
    seed=42
):
    """
    Generate responses for a list of inputs using the GPT model.

    Args:
        inputs (List[Dict[str, Any]]): List of dictionaries containing 'system_prompt' and 'user_message'.
        model (str, optional): Name of the model to use. Defaults to "gpt-4o-mini".
        temp (float, optional): Temperature setting for response generation. Defaults to 0.0.
        top_p (float, optional): Nucleus sampling parameter. Defaults to 0.9.
        mute_tqdm (bool, optional): Whether to disable the tqdm progress bar. Defaults to False.

    Returns:
        List[str]: List of responses generated by the model.
    """
    responses = []

    for input_dict in tqdm.tqdm(
        inputs,
        disable=mute_tqdm,  # Option to mute the progress bar
        desc=f"Inference {model}",  # Description shown in the progress bar
        leave=False,  # Remove the progress bar after completion
    ):
        response = llm_single_generate(
            input_dict,
            model=model,
            temp=temp,
            top_p=top_p,
            seed=seed,
        )
        responses.append(response)

    return responses

if __name__ == "__main__":
    # Example input list with system and user prompts
    model_name_set = ["gpt-4o-mini", "claude-3-haiku-20240307", "gemini-1.5-flash", "Qwen/Qwen2-7B-Instruct", "llama-3.2-3b-preview"]
    
    input_list = [
        {
            "system_prompt": "You are a helpful assistant.",
            "user_message": "How much is 1+1",
        },
        {
            "system_prompt": "You are a helpful assistant.",
            "user_message": "Kobe and LeBron, who is the better basketball player?",
        },
    ]
    
    for model_name in model_name_set:
        print("model_name: ", model_name)
        
        # Generate responses using the GPT model
        responses = llm_generate(input_list, model=model_name)

        # Print the generated responses
        print(responses)
