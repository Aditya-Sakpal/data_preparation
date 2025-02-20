import os
import asyncio
import openai
from tenacity import (
    retry,
    wait_random_exponential,
)  
from langchain_openai import ChatOpenAI
from .token_counting import  count_tokens_messages, get_available_tokens

API_KEYS = ["OPENAI_API_KEY"]
api_key_lock = asyncio.Lock()
api_key_index = 0
#---------------------------------------------------------------------------------------------
# QUESTION PROCESSING

# Ensure we do not run too many concurent requests
model_rate_limits = 2000
max_concurent_request = int(model_rate_limits * 0.75)
throttler = asyncio.Semaphore(max_concurent_request)


@retry(
    wait=wait_random_exponential(min=15, max=40),
)
async def run_model(messages):
    """
    Asynchronously runs the chat model with as many tokens as possible on the given messages.
    
    Args:
        messages (list): A list of input messages to be processed by the model.

    Returns:
        str: The model-generated output text after processing the input messages.
    """
    async with api_key_lock:  # Ensure that the rotation is thread-safe
        global api_key_index
        os.environ['OPENAI_API_KEY'] = API_KEYS[api_key_index]
        api_key_index = (api_key_index + 1) % len(API_KEYS)
    # Count the number of tokens in the input messages
    num_tokens_in_messages = count_tokens_messages(messages)

    # Calculate the number of tokens available for processing
    num_tokens_available = get_available_tokens(num_tokens_in_messages)

    # Create an instance of the ChatOpenAI model with minimum imagination (temperature set to 0)
    model = ChatOpenAI(temperature=0.0, max_tokens=num_tokens_available)

    try:
        # Use a semaphore to limit the number of simultaneous calls
        async with throttler:
            # Asynchronously run the model on the input messages
            output = await model._agenerate(messages)
    except openai.error.RateLimitError as e:
        print(f"ERROR ({e}): Rate limit exceeded, retrying.")
        raise  # Re-raise the exception to allow tenacity to handle the retry
    except openai.error.APIConnectionError as e:
        print(f"ERROR ({e}): Could not connect, retrying.")
        raise  # Re-raise the exception to allow tenacity to handle the retry
    except Exception as e:
        print(f"ERROR ({e}): Could not generate text for an input.")
        return 'ERROR'
    
    # Extract and return the generated text from the model output
    return output.generations[0].text.strip()