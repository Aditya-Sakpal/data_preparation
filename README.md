# Question Extractor 🧐

Large language models can be instruction tuned with a set of questions and answers.
However, to further fine-tune a model *on your own data*, you need a large number of questions and answers about your data.
Producing those questions and answers can be a lot of manual work.

This repository lets you use a non-fine-tuned language model (ChatGPT) to extract question/answer pairs automatically from existing textual data, eliminating all manual work.

## Installation Setup

### Clone the repo 
```
git clone https://github.com/Aditya-Sakpal/data_preparation
```

### Install the requirements 
```
pip install -r requirements.txt
```

### Place the OpenAI's API key in question_extractor/llm.py file on line no. 11 and question_extractor/markdown.py on line no. 23

### Place your input files in data/docs directory (make sure it's in markdown format with .md extension)

### Run the question_extractor.py file 
```
python question_extractor.py --input_dir data --output_file output.jsonl
```

## Usage

This script is designed to turn a folder of markdown (`.md`) documents into a `.json` file containing a list of questions, answers and paths to the source documents that were used to produce them.

To run the code, set the relevant file paths in the `question_extractor.py` file (both the input folder and the output path) and insure that your [OpenAI API key](https://platform.openai.com/account/api-keys) is in the environment.
Then run the script with Python:

```
python3 question_extractor.py
```

Once it is done, all questions/answers will be written as a `.json` file in the output path.

## Inner-workings

The code loops on all files, for each file it extracts a list of questions using the following prompt followed by a chunk of text:

```
You are an expert user extracting information to quiz people on documentation. You will be passed a page extracted from the documentation, write a numbered list of questions that can be answered based *solely* on the given text.
```

It then loops on the questions, producing an answer by passing the following prompt followed by a chunk of text and a question:

```
You are an expert user answering questions. You will be passed a page extracted from a documentation and a question. Generate a comprehensive and informative answer to the question based *solely* on the given text.
```

Most of the actual logic of the code is dedicated to processing the files concurrently (for speed) and insuring that text chunks passed to the model are small enough to leave enough tokens for answering.

If a text is too long to be sent to the model, it is split along its highest markdown heading level (the process can be repeated recursively if needed until we get down to single paragraphs).

Performance-wise, this script can process [the full NERSC documentation](https://gitlab.com/NERSC/nersc.gitlab.io/-/tree/main/docs) in 6 minutes[^rate].
Turning 318 markdown files into 8005 questions for $29.

[^rate]: Running at about 93% of the model's rate limit.

## Potential improvements

- make it possible to use GPT4 for the question answering, improving the quality of the answers at the cost of a slower runtime and significantly increased costs
- save intermediate results to be able to restart an interrupted job
- use the OpenAI client directly, instead of Langchain, to reduce dependencies
