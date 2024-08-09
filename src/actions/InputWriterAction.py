
import re
from typing import List
import os
from metagpt.actions import Action
from metagpt.schema import Message
from qa_module import AsyncQA_tutorial, AsyncQA_Ori
import config_path


class InputWriterAction(Action):
    PROMPT_TEMPLATE: str = """
    Your task is {requirement}.
    The similar foamfile is provided as follows:
    {tutorial_file}
    Please take this foamfile as a reference, which may help you to finish your task.
    According to your task, return ```your_code_here ``` with NO other texts,
    your code:
    """
    PROMPT_Find: str = """
        Find the OpenFOAM foamfile that most closely matches the following foamfile:
        {file_name} in {file_folder} of case name: {case_name}
    """
    name: str = "InputWriterAction"

    async def run(self, with_messages:List[Message]=None, **kwargs) -> Message:

        file_list = []

        async_qa_tutorial = AsyncQA_tutorial()
        async_qa = AsyncQA_Ori()
        document_text = self.read_openfoam_tutorials(f"{config_path.Database_PATH}/openfoam_tutorials.txt")
        
        for i in with_messages:
            file_name = self.parse_flie_name(i.content)
            file_list.append(file_name)

            folder_name = self.parse_folder_name(i.content)
            IF_rewrite = self.parse_rewirte(i.content)

            file_path = f"{config_path.Case_PATH}/{folder_name}/{file_name}"
            case_name_true = os.path.basename(config_path.Case_PATH)
            if os.path.exists(file_path) and 'rewrite' not in IF_rewrite:
                print(f"File {file_name} already exists in {folder_name}. Skipping...")
                continue

            case_info = self.read_similar_case(f"{config_path.Case_PATH}/find_tutorial.txt")
            case_name = case_info['case_name']
            case_domain = case_info['case_domain']
            case_category = case_info['case_category']
            case_solver = case_info['case_solver']
            similar_file = f"```input_file_begin: input {file_name} file of case {case_name} (domain: {case_domain}, category: {case_category}, solver:{case_solver})"
            
            tutorial_file = self.find_similar_file(similar_file,document_text)
            print("tutorial_file:",tutorial_file)
            if tutorial_file == "None":
                prompt_find = self.PROMPT_Find.format(file_name=file_name, file_folder=folder_name, case_name = case_name_true)
                rsp = await async_qa_tutorial.ask(prompt_find)
                result = rsp["result"]
                print("find_similar_foamfile:", result)
                doc = rsp["source_documents"]
                tutorial_file = doc[0].page_content
                print("find_tutorial_file:",tutorial_file)

            print(f"File {file_name} is going to be written")
            prompt = self.PROMPT_TEMPLATE.format(requirement=i.content, tutorial_file = tutorial_file)
            rsp = await async_qa.ask(prompt)
            code_text = self.parse_context(rsp)
            print('folder_name',folder_name)
            print('file_name',file_name)
            if folder_name.strip() and file_name.strip():
                self.save_file(file_path, code_context=str(code_text))
            else:
                print("Folder name or file name is empty, skipping save operation.")
        
        return "dummpy message"

    
    @staticmethod
    def parse_flie_name(rsp):
        pattern = r"a OpenFoam (.*) foamfile"
        match = re.search(pattern, rsp, re.DOTALL)
        your_task_flie = match.group(1) if match else ''
        return your_task_flie

    @staticmethod
    def parse_folder_name(rsp):
        pattern = r"foamfile in (.*) folder that"
        match = re.search(pattern, rsp, re.DOTALL)
        your_task_folder = match.group(1) if match else ''
        return your_task_folder
      
    @staticmethod
    def parse_context(rsp):
        pattern = r"(FoamFile.*?)(?:```|$)"
        match = re.search(pattern, rsp, re.DOTALL)
        if match:
            your_task_flie = match.group(1) 
        else:
            match2 = re.search(r'```(?:.*?\n)(.*?)\n```', rsp, re.DOTALL)
            if match2:
                your_task_flie =  match2.group(1) 
            else:
                your_task_flie = rsp
        return your_task_flie
    
    @staticmethod
    def parse_rewirte(rsp):
        pattern = r"to (.*) a OpenFoam"
        match = re.search(pattern, rsp, re.DOTALL)
        your_task_flie = match.group(1) if match else ''
        return your_task_flie
    def find_similar_file(self, start_string, document_text):

        start_pos = document_text.find(start_string)
        if start_pos == -1:
            return "None"
        
        end_pos = document_text.find("input_file_end.", start_pos)
        if end_pos == -1:
            return "None"
        
        return document_text[start_pos:end_pos + len("input_file_end.")]
    def read_similar_case(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # 初始化要读取的字段
                case_info = {
                    'case_name': None,
                    'case_domain': None,
                    'case_category': None,
                    'case_solver': None
                }
                
                for line in file:
                    line = line.strip()
                    if line.startswith('case name:'):
                        case_info['case_name'] = line.split('case name:')[1].strip()
                    elif line.startswith('case domain:'):
                        case_info['case_domain'] = line.split('case domain:')[1].strip()
                    elif line.startswith('case category:'):
                        case_info['case_category'] = line.split('case category:')[1].strip()
                    elif line.startswith('case solver:'):
                        case_info['case_solver'] = line.split('case solver:')[1].strip()

                return case_info
            
        except FileNotFoundError:
            return f"file {file_path} not found"
    
    # def read_similar_case(self, file_path):
    #     try:
    #         with open(file_path, 'r', encoding='utf-8') as file:
    #             # 读取文件的第一行
    #             first_line = file.readline().strip()
                
    #             case_name_pos = first_line.find('case name:')
    #             if case_name_pos == -1:
    #                 return "None"
                
    #             case_name = first_line[case_name_pos + len('case name:'):].strip()
    #             return case_name
        
    #     except FileNotFoundError:
    #         return f"file {file_path} not found"
    def read_openfoam_tutorials(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:

                content = file.read()
                return content
        except FileNotFoundError:
            return f"file {file_path} not found"
        except Exception as e:
            return f"reading file meet error: {e}"
    def save_file(self, file_path: str, code_context: str) -> None:

        directory = os.path.dirname(file_path)
        # Create the folder path if it doesn't exist
        os.makedirs(directory, exist_ok=True)

        with open(file_path, 'w') as file:
            file.write(code_context)  # 将代码写入文件

        print(f"File saved successfully at {file_path}")
