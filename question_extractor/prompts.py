from langchain.schema import HumanMessage, SystemMessage

#----------------------------------------------------------------------------------------
# EXTRACTION

# prompt used to extract questions
extraction_system_prompt="You are an expert in blockchain technology and decentralized systems, emulating the communication style of Vitalik Buterin. Given the provided documentation, generate a numbered list of insightful and thought-provoking questions that a user might pose to an AI agent trained on Vitalik's data. These questions should reflect the depth and breadth of topics Vitalik typically addresses, including but not limited to blockchain scalability, decentralization, and the societal impacts of emerging technologies."

def create_extraction_conversation_messages(text):
    """
    Takes a piece of text and returns a list of messages designed to extract questions from the text.
    
    Args:
        text (str): The input text for which questions are to be extracted.
    
    Returns:
        list: A list of messages that set up the context for extracting questions.
    """
    context_message = SystemMessage(content=extraction_system_prompt)
    input_text_message = HumanMessage(content=text)
    
    return [context_message, input_text_message]

subtitles_generation_prompt = """
You are an expert in blockchain technology and decentralized systems, emulating the communication style of Vitalik Buterin. Given the provided text , generate a title that encapsulates the core message and themes of the content. The title should be engaging, informative, and reflective of the technical and philosophical aspects of the text. Consider the broader implications of the content and aim to create a title that is both descriptive and thought-provoking.
"""
def create_subtitles_generation_messages(text):
    """
    Takes a piece of text and returns a list of messages designed to generate subtitles from the text.
    
    Args:
        text (str): The input text for which subtitles are to be generated.
    
    Returns:
        list: A list of messages that set up the context for generating subtitles.
    """
    context_message = SystemMessage(content=subtitles_generation_prompt)
    input_text_message = HumanMessage(content=text)
    
    return [context_message, input_text_message]


#----------------------------------------------------------------------------------------
# ANSWERING

# prompt used to answer a question
answering_system_prompt="You are an expert in blockchain technology and decentralized systems, emulating the communication style of Vitalik Buterin. Given the provided documentation and the user's question, generate a comprehensive and informative answer that reflects Vitalik's analytical and philosophical approach. Your response should delve into the technical aspects while also considering the broader societal implications, ensuring clarity and accessibility for a diverse audience."


def create_answering_conversation_messages(question, text):
    """
    Takes a question and a text and returns a list of messages designed to answer the question based on the text.
    
    Args:
        question (str): The question to be answered.
        text (str): The text containing information for answering the question.
    
    Returns:
        list: A list of messages that set up the context for answering the question.
    """
    # Create a system message setting the context for the answering task
    context_message = SystemMessage(content=answering_system_prompt)
    
    # Create a human message containing the input text
    input_text_message = HumanMessage(content=text)
    
    # Create a human message containing the question to be answered
    input_question_message = HumanMessage(content=question)
    
    # Return the list of messages to be used in the answering conversation
    return [context_message, input_text_message, input_question_message]
