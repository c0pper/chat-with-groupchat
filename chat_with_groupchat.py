# -*- coding: utf-8 -*-
"""chat-with-groupchat.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_5POsmQrbkv5hLIIH1X-5ZjNmYTskmpr
"""

import os
from pathlib import Path
from langchain.document_loaders import TextLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import MarkdownTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain
import chromadb
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import textwrap
from langchain.prompts import PromptTemplate


# loader = TextLoader("/content/drive/MyDrive/data/all-messages.txt")
# docs = loader.load()

# with open('/content/drive/MyDrive/data/all-messages.txt') as f:
#     all_messages = f.read()

# markdown_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=0)

# docs = markdown_splitter.create_documents([all_messages])


def init_chromadb():
    client_settings = chromadb.config.Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=persist_directory,
        anonymized_telemetry=False
    )

    vectorstore = Chroma(
        collection_name="langchain_store",
        embedding_function=embeddings,
        client_settings=client_settings,
        persist_directory=persist_directory,
    )

    if os.path.exists(persist_directory) and os.path.isdir(persist_directory):
        print("Directory 'db' exists. Using existing vectordb")
    # pass
    else:
        print("Directory 'db' does not exist. Creating new vectordb")
    #     vectorstore.add_documents(documents=docs, embedding=embeddings)
    #     vectorstore.persist()
    
    return vectorstore

def query_chromadb(vectorstore, query):
    result = vectorstore.similarity_search_with_score(query=query, k=4)
    print(result)
    return result

def wrap_text_preserve_newlines(text, width=110):
    # Split the input text into lines based on newline characters
    lines = text.split('\n')

    # Wrap each line individually
    wrapped_lines = [textwrap.fill(line, width=width) for line in lines]

    # Join the wrapped lines back together using newline characters
    wrapped_text = '\n'.join(wrapped_lines)

    return wrapped_text

def process_llm_response(llm_response):
    print(wrap_text_preserve_newlines(llm_response['result']))
    print('\n\nSources:')
    for source in llm_response["source_documents"]:
        print(source.page_content, end="\n----\n")

    return wrap_text_preserve_newlines(llm_response['result'])


embeddings = HuggingFaceEmbeddings(model_name="efederici/sentence-BERTino")

persist_directory = Path("data/lorenzodb")
# vectorstore = init_chromadb()
vectorstore = Chroma(collection_name="langchain_store", persist_directory=str(persist_directory),
                     embedding_function=embeddings)


prompt_template = """Usa i seguenti testi estratti da messaggi di Lorenzo Valitutto per rispondere alla domanda posta. Attieniti strettamente alle informazioni presenti nei messaggi di seguito, non inventare risposte.
Rispondi solo a domande del tipo "Cosa sappiamo su...?", "Chi era...?", "Cosa puoi dirmi su...?". Se la domanda ha un impostazione diversa, ad esempio "Perchè...?", "Come...?", rispondi "Non lo so, fammi domande su Lorenzo."

Messaggi:
{context}

Domanda: {question}
Risposta in italiano:"""
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

chain_type_kwargs = {"prompt": PROMPT}
qa_chain = RetrievalQA.from_chain_type(llm=OpenAI(),
                                  chain_type="stuff",
                                  retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
                                  return_source_documents=True,
                                  chain_type_kwargs=chain_type_kwargs)


if __name__ == '__main__':
    # cosa sai sul principe della foresta?
    # cosa mi puoi dire su Bamba?
    # Lorenzo menziona spesso il personaggio di Agata. Cosa sappiamo su di lei?
    # cosa sappiamo di Giacomo Orco?
    # cosa sappiamo di Luigia manzella?
    # cosa sappiamo di Rosanna Opromolla?
    # cosa sai su Lucio Mandia ?
    # cosa mi sai dire su originalcomic?
    query = "Perché non posso dire bugie agli amici di sempre?"
    ans = query_chromadb(vectorstore, query)

    llm_response = qa_chain(query)
    process_llm_response(llm_response)