import os

from dotenv import load_dotenv
import pdfplumber
from llama_index.core import Document
from llama_index.core.node_parser import (
    SemanticSplitterNodeParser,
)
from llama_index.embeddings.openai import OpenAIEmbedding

from .prompts import create_subtitles_generation_messages
from .llm import run_model

load_dotenv()
embed_model = OpenAIEmbedding()
splitter = SemanticSplitterNodeParser(
    include_metadata=True,
    buffer_size=1, 
    breakpoint_percentile_threshold=95, 
    embed_model=embed_model
)

os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"

def files_from_directory(directory):
    """
    Takes a folder path as input.
    Returns a list of tuples containing the file path and text for all markdown files in the input folder.
    
    Args:
        directory (str): The path to the folder containing markdown files.

    Returns:
        list of tuples: A list of tuples containing the file path (str) and the file content (str) for each markdown file.
    """
    files_data = []

    # Iterate through the files in the directory and its subdirectories
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            
            # Check if the file is a markdown file
            if file_name.endswith('.md'):
                file_path = os.path.join(root, file_name)
                
                # Read the file content
                with open(file_path, "r", encoding="utf-8") as file:
                    file_content = file.read()
                
                # Append the file path and content to the files_data list
                files_data.append((file_path, file_content))
            elif file_name.endswith('.markdown'):
                file_path = os.path.join(root, file_name)
                
                # Read the file content
                with open(file_path, "r", encoding="utf-8") as file:
                    file_content = file.read()
                
                files_data.append((file_path, file_content))
            elif file_name.endswith('.txt'):
                file_path = os.path.join(root, file_name)
                
                # Read the file content
                with open(file_path, "r", encoding="utf-8") as file:
                    file_content = file.read()
                
                # Append the file path and content to the files_data list
                files_data.append((file_path, file_content))
            elif file_name.endswith('.pdf'):
                file_path = os.path.join(root, file_name)
                file_content = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        file_content += page.extract_text() + "\n"  
                        
                files_data.append((file_path, file_content))

    return files_data

def find_highest_markdown_heading_level(lines):
    """
    Takes a list of lines representing a markdown file as input.
    Finds the highest level of heading and returns it as an integer.
    Returns None if the text contains no headings.
    
    Args:
        lines (list of str): A list of lines in the markdown file.

    Returns:
        int or None: The highest heading level as an integer, or None if no headings are found.
    """
    highest_heading_level = None
    code_section = False

    # Iterate through the lines in the markdown file
    for line in lines:
    
        """
        Check code section e.g.:
            ```bash
            # Trace an IP packet between two Pods
            antctl trace-packet -S ns1/pod1 -D ns2/pod2
            # Trace a Service request from a local Pod
            antctl trace-packet -S ns1/pod1 -D ns2/svc2 -f "tcp,tcp_dst=80"
            # Trace the Service reply packet (assuming "ns2/pod2" is the Service backend Pod)
            antctl trace-packet -D ns1/pod1 -S ns2/pod2 -f "tcp,tcp_src=80"
            # Trace an IP packet from a Pod to gateway port
            antctl trace-packet -S ns1/pod1 -D antrea-gw0
            # Trace a UDP packet from a Pod to an IP address
            antctl trace-packet -S ns1/pod1 -D 10.1.2.3 -f udp,udp_dst=1234
            # Trace a UDP packet from an IP address to a Pod
            antctl trace-packet -D ns1/pod1 -S 10.1.2.3 -f udp,udp_src=1234
            # Trace an ARP request from a local Pod
            antctl trace-packet -p ns1/pod1 -f arp,arp_spa=10.1.2.3,arp_sha=00:11:22:33:44:55,arp_tpa=10.1.2.1,dl_dst=ff:ff:ff:ff:ff:ff
            ```
        Here # is a code comment not the md level symbole
        """
        if line.startswith("```"):
            code_section = not code_section
        # Check if the line starts with a heading
        if line.startswith("#") and not code_section:
            
            # Calculate the heading level based on the number of '#' characters
            current_heading_level = len(line.split()[0])
            
            # Update the highest_heading_level if it is None or if the current_heading_level is higher
            if (highest_heading_level is None) or (current_heading_level < highest_heading_level):
                highest_heading_level = current_heading_level

    return highest_heading_level

def chunk_text(text, max_size=8192):
    if len(text) <= max_size:
        return [text]
    
    avg_chunk_size = max_size
    num_chunks = -(-len(text) // avg_chunk_size)  # Ceiling division
    
    for i in range(1, num_chunks + 1):
        chunk_size = len(text) // i
        if chunk_size <= max_size:
            return [text[j:j+chunk_size] for j in range(0, len(text), chunk_size)]
    
    return [text] 

async def split_markdown(text):
    """
    Takes a string representation of a markdown file as input.
    Finds the highest level of heading and splits the text into sections accordingly.
    Returns a list of tuples, each containing the section title and section content.
    
    Args:
        text (str): The content of a markdown file as a single string.

    Returns:
        list of tuples: A list of tuples containing the section title (str) and section content (str).
    """
    try:
        lines = text.split('\n')

        # Remove the title heading (if present) from the text
        if (len(lines) > 0) and (lines[0].startswith('#')):
            lines = lines[1:]

        # Find the highest heading level
        highest_heading_level = find_highest_markdown_heading_level(lines)
        sections = []

        # If there are no headings, print a warning and return an empty list
        if highest_heading_level is None:
            texts = chunk_text(text)
            for text in texts:
                document = Document(text=text)
                nodes = splitter.get_nodes_from_documents([document])
                for node in nodes:
                    messages = create_subtitles_generation_messages(node.text)
                    subtitle = await run_model(messages)
                    sections.append((subtitle, node.text))
            return sections

        # Construct the heading prefix for splitting
        headings_prefix = ("#" * highest_heading_level) + " "

        current_section_title = ''
        current_section = []

        for line in lines:
            # Check if the line starts with the highest heading level prefix
            if line.startswith(headings_prefix):
                # If the current_section is not empty, add it to the sections list
                if len(current_section) > 0:
                    current_section_body = '\n'.join(current_section)
                    sections.append((current_section_title, current_section_body))

                    # Update the current_section_title and clear the current_section
                    current_section_title = line.strip()
                    current_section = []
            else:
                # Add the line to the current_section
                current_section.append(line)

        # Add the last section to the sections list (if not empty)
        if len(current_section) > 0:
            current_section_body = '\n'.join(current_section)
            sections.append((current_section_title, current_section_body))

        return sections
    except Exception as e:
        print(f"ERROR: {e}")
        return []