
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI

from langchain_community.embeddings.openai import OpenAIEmbeddings
import os

import asyncio
from concurrent.futures import ThreadPoolExecutor
from langchain.chains import RetrievalQA

import asyncio
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
import config_path
from langchain_community.callbacks import get_openai_callback
from Statistics import global_statistics

class AsyncQA_tutorial:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AsyncQA_tutorial, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance
    
    def init_instance(self):
        if not self._initialized:
            self.qa_interface = setup_qa_tutorial()
            self.executor = ThreadPoolExecutor()
            self._initialized = True

    async def ask(self, question):
        loop = asyncio.get_running_loop()

        result, usage_info = await loop.run_in_executor(self.executor, self._execute_with_callback, question)

        global_statistics.total_tokens += usage_info.get('total_tokens', 0)
        global_statistics.prompt_tokens += usage_info.get('prompt_tokens', 0)
        global_statistics.completion_tokens += usage_info.get('completion_tokens', 0)
        return result
    
    def _execute_with_callback(self, question):
        with get_openai_callback() as cb:
            result = self.qa_interface(question)
            usage_info = {
                'total_tokens': cb.total_tokens,
                'prompt_tokens': cb.prompt_tokens,
                'completion_tokens': cb.completion_tokens,
                'total_cost': cb.total_cost,
            }
            return result, usage_info

    def close(self):
        self.executor.shutdown()

class AsyncQA_tutorial_name:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AsyncQA_tutorial_name, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance
    
    def init_instance(self):
        if not self._initialized:
            self.qa_interface = setup_qa_tutorial_name()
            self.executor = ThreadPoolExecutor()
            self._initialized = True

    async def ask(self, question):
        loop = asyncio.get_running_loop()

        result, usage_info = await loop.run_in_executor(self.executor, self._execute_with_callback, question)

        global_statistics.total_tokens += usage_info.get('total_tokens', 0)
        global_statistics.prompt_tokens += usage_info.get('prompt_tokens', 0)
        global_statistics.completion_tokens += usage_info.get('completion_tokens', 0)
        return result
    def _execute_with_callback(self, question):
        with get_openai_callback() as cb:
            result = self.qa_interface(question)
            usage_info = {
                'total_tokens': cb.total_tokens,
                'prompt_tokens': cb.prompt_tokens,
                'completion_tokens': cb.completion_tokens,
                'total_cost': cb.total_cost,
            }
            return result, usage_info

    def close(self):
        self.executor.shutdown()

class AsyncQA_allrun:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AsyncQA_allrun, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance
    
    def init_instance(self):
        if not self._initialized:
            self.qa_interface = setup_qa_allrun()
            self.executor = ThreadPoolExecutor()
            self._initialized = True

    async def ask(self, question):
        loop = asyncio.get_running_loop()
        result, usage_info = await loop.run_in_executor(self.executor, self._execute_with_callback, question)

        global_statistics.total_tokens += usage_info.get('total_tokens', 0)
        global_statistics.prompt_tokens += usage_info.get('prompt_tokens', 0)
        global_statistics.completion_tokens += usage_info.get('completion_tokens', 0)
        return result
    def _execute_with_callback(self, question):
        with get_openai_callback() as cb:
            result = self.qa_interface(question)
            usage_info = {
                'total_tokens': cb.total_tokens,
                'prompt_tokens': cb.prompt_tokens,
                'completion_tokens': cb.completion_tokens,
                'total_cost': cb.total_cost,
            }
            return result, usage_info

    def close(self):
        self.executor.shutdown()

class AsyncQA_command_help:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AsyncQA_command_help, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance
    
    def init_instance(self):
        if not self._initialized:
            self.qa_interface = setup_qa_command_help()
            self.executor = ThreadPoolExecutor()
            self._initialized = True
            
    async def ask(self, question):
        loop = asyncio.get_running_loop()
        # 在线程池中运行同步函数

        result, usage_info = await loop.run_in_executor(self.executor, self._execute_with_callback, question)

        global_statistics.total_tokens += usage_info.get('total_tokens', 0)
        global_statistics.prompt_tokens += usage_info.get('prompt_tokens', 0)
        global_statistics.completion_tokens += usage_info.get('completion_tokens', 0)
        return result
    def _execute_with_callback(self, question):
        with get_openai_callback() as cb:
            result = self.qa_interface(question)
            usage_info = {
                'total_tokens': cb.total_tokens,
                'prompt_tokens': cb.prompt_tokens,
                'completion_tokens': cb.completion_tokens,
                'total_cost': cb.total_cost,
            }
            return result, usage_info

    def close(self):
        self.executor.shutdown()

class AsyncQA_Ori:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AsyncQA_Ori, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance
    
    def init_instance(self):
        if not self._initialized:
            self.qa_interface = setup_qa_ori()
            self.executor = ThreadPoolExecutor()
            self._initialized = True

    async def ask(self, question):
        loop = asyncio.get_running_loop()

        result = await loop.run_in_executor(self.executor, self.qa_interface, question)
        return result

    def close(self):
        self.executor.shutdown()

def setup_qa_ori():
    def get_gpt4o_response(user_msg):

        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_msg
                }
            ],
            model=config_path.model,
            temperature=config_path.temperature
        )
        chat_completion_dict = dict(chat_completion)
        print(chat_completion_dict.keys())
        usage = chat_completion_dict['usage']
        usage = dict(usage)
        total_tokens = usage['total_tokens']
        prompt_tokens = usage['prompt_tokens']
        completion_tokens = usage['completion_tokens']

        global_statistics.total_tokens += total_tokens
        global_statistics.prompt_tokens += prompt_tokens
        global_statistics.completion_tokens += completion_tokens

        return chat_completion.choices[0].message.content

    return get_gpt4o_response

def setup_qa_tutorial():

    persist_directory = f'{config_path.Database_PATH}/openfoam_tutorials'
    vectordb = FAISS.load_local(persist_directory, OpenAIEmbeddings(),allow_dangerous_deserialization=True)
    chat_model = ChatOpenAI(model=config_path.model, temperature=config_path.temperature)
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": config_path.searchdocs})

    qa_interface = RetrievalQA.from_chain_type(
        llm=chat_model,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )


    return qa_interface

def setup_qa_tutorial_name():

    persist_directory = f'{config_path.Database_PATH}/openfoam_tutorials_summary'
    vectordb = FAISS.load_local(persist_directory, OpenAIEmbeddings(),allow_dangerous_deserialization=True)
    chat_model = ChatOpenAI(model=config_path.model, temperature=config_path.temperature)
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": config_path.searchdocs})
    qa_interface = RetrievalQA.from_chain_type(
        llm=chat_model,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    return qa_interface

def setup_qa_allrun():

    persist_directory = f'{config_path.Database_PATH}/openfoam_allrun'
    vectordb = FAISS.load_local(persist_directory, OpenAIEmbeddings(),allow_dangerous_deserialization=True)
    chat_model = ChatOpenAI(model=config_path.model, temperature=config_path.temperature)
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": config_path.searchdocs})
    qa_interface = RetrievalQA.from_chain_type(
        llm=chat_model,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )
    return qa_interface

def setup_qa_command_help():

    persist_directory = f'{config_path.Database_PATH}/openfoam_command_helps'
    vectordb = FAISS.load_local(persist_directory, OpenAIEmbeddings(),allow_dangerous_deserialization=True)
    chat_model = ChatOpenAI(model=config_path.model, temperature=config_path.temperature)
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": config_path.searchdocs})
    qa_interface = RetrievalQA.from_chain_type(
        llm=chat_model,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )
    return qa_interface
