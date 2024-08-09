

import re
from typing import List
import os

from metagpt.actions import Action
from metagpt.schema import Message

from qa_module import AsyncQA_Ori
import config_path
import sys
import glob
from Statistics import global_statistics

class ReviewerAction(Action):
    PROMPT_TEMPLATE1: str = """
    {command} has been executed in openfoam10, and got the following error:
    {error}
    The corresponding input file {file_name} is:
    {file_text}
    Please analyze whether the error is related to this input file,
    If the error is related to {file_name}, generate this exact response:
    ``` Yes ``` with NO other texts.
    If the error is not related to {file_name},generate this exact response:
    ``` No ``` with NO other texts.
    """
    PROMPT_TEMPLATE2: str = """
    to rewrite a OpenFoam {file_name} foamfile in {folder_names} folder that could solve the error:
    {error}
    Note that the original {file_name} file encounter the error when {command} has been executed in openfoam10,
    The text of original {file_name} file is:
    {file_text}
    Note that you need to return the entire modified file, never return a single modified fragment, because I want to save and run the file directly, making sure there are no other characters
    """
    PROMPT_TEMPLATE3: str = """
    {command} has been executed in openfoam10, and got the following error:
    {error}
    The corresponding input file list is:
    {file_names}
    The corresponding directories are:
    {file_folders}
    Please analyze whether the error is related to the file structure, such as missing critical files or redundant input files.
    If the error is related to the file structure, return the updated file structure list and their respective directories in the following format:
    ###file_name1, file_name2, ...### in ```file_folder1, file_folder2, ...``` with NO other texts.
    If the error is not related to file structure, return:
    ``` None ```
    """
    PROMPT_TEMPLATE4: str = """
    to write a OpenFoam {file_name} foamfile in {folder_names} folder that could be used to meet user requirement:{requirement}.
    """
    PRPMPT_FINAL: str = """
    {command} has been executed in openfoam10, and got the following error:
    {error}
    The corresponding input file list is:
    {file_list} in folder {folder_list}
    Please analyze which files the error may be related to, and return the related files and the corresponding folders as follows:
    ###file_name1, file_name2, ...### in ```file_folder1, file_folder2, ...``` with NO other texts.
    where file_name1, file_name2, ..., come from {file_list}
    and file_folder1, file_folder2, ..., come from {folder_list}
    """

    PROMPT_TEMPLATE_REWRITE: str = """
    to rewrite a OpenFoam {file_name} foamfile in {file_folder} folder that could solve the error:
    ###ERROR BEGIN:
    {error}
    ERROR END.###
    Note that {file_list} in {folder_list} folder was found to be associated with the error, and you need to rewrite {file_name} first, taking into account how these files affect each other.
    the original {file_list} in {folder_list} folder encounter the error when {command} has been executed in openfoam10,
    {related_files}
    Note that you need to return the entire modified file, never return a single modified fragment, because I want to save and run the file directly, making sure there are no other characters
    According to your task, return ```your_code_here ``` with NO other texts,
    your code:
    """

    async def run(self, with_messages:List[Message]=None, **kwargs) -> Message:

        base_path = config_path.Case_PATH
        
        file_text, files_names,folder_names = self.read_files_into_dict(base_path)
        os.chdir(base_path)
        print('files_names:',files_names,folder_names)
        subtasks = []
        command = with_messages[-1].content
        requirement = with_messages[0].content
        command = command.strip()
        print("command:",command)
        print("requirement:",requirement)

        if command != "None":
            command_err = f"{config_path.Case_PATH}/{command}.err"
            error_content = self.read_error_content(command_err)

            async_qa = AsyncQA_Ori()
        
            prompt3 = self.PROMPT_TEMPLATE3.format(command= command, error=error_content, file_names = files_names, file_folders = folder_names)
            print("prompt3",prompt3)
            rsp = await async_qa.ask(prompt3)
            
            print('rsp_structrue:',rsp)

            if('None' not in rsp):
                files_names_new = self.parse_file_list(rsp)
                file_folders_new = self.parse_folder_name(rsp)

                files_names_new = [name.strip().strip("'") for name in files_names_new.split(',')]
                file_folders_new = [folder.strip().strip("'") for folder in file_folders_new.split(',')]
                    
                print("files_names_new2:",files_names_new)
                print("file_folders_new2:",file_folders_new)
                # compare files_names_new and files_names
                if len(files_names_new) == len(file_folders_new):

                    for file in files_names_new:
                        
                        folder_name = file_folders_new[files_names_new.index(file)]
                        prompt4 = self.PROMPT_TEMPLATE4.format(file_name = file, folder_names = folder_name, requirement = requirement)
                        subtasks.append(prompt4)

            else:

                prompt_final = self.PRPMPT_FINAL.format(command= command, error=error_content, file_list = files_names, folder_list = folder_names)

                rsp = await async_qa.ask(prompt_final)

                print('rsp:',rsp)

                files_names_rewirte = self.parse_file_list(rsp)
                print('files_names_rewirte:',files_names_rewirte)
                file_folders_rewirte = self.parse_folder_name(rsp)
                files_names_rewirte = [name.strip().strip("'") for name in files_names_rewirte.split(',')]

                file_folders_rewirte = [folder.strip().strip("'") for folder in file_folders_rewirte.split(',')]

                n_rewrite = len(files_names_rewirte)
                print("n_rewrite:",n_rewrite)
                print("files_names_rewirte:",files_names_rewirte)
                prompt_file_texts = ""
                for file in files_names:
                    prompt_file_texts += f"The text of original {file} file is:\n"
                    prompt_file_texts += "###FILE BEGIN:\n"
                    prompt_file_texts += file_text[file]
                    prompt_file_texts += "FILE END.###\n"

                if files_names_rewirte:
                    for file in files_names_rewirte:
                        try:
                            file_folder = folder_names[file]
                            prompt_rewrite = self.PROMPT_TEMPLATE_REWRITE.format(command= command, 
                                                                                error=error_content, 
                                                                                file_name = file, 
                                                                                file_folder = file_folder,
                                                                                related_files = prompt_file_texts,
                                                                                file_list = files_names_rewirte,
                                                                                folder_list = file_folders_rewirte)
                            subtasks.append(prompt_rewrite)
                        except KeyError:

                            continue

            print('number_subatasks:',len(subtasks))

            os.chdir('../')
            return subtasks
        else:
            # command = None
            # postprocess 
            return ["None"]
    
    def read_files_into_dict(self, base_path):
        file_contents = {} 
        file_names = []  
        folder_names = {}   
        base_depth = base_path.rstrip(os.sep).count(os.sep) 
        
        for root, dirs, files in os.walk(base_path):
            current_depth = root.rstrip(os.sep).count(os.sep)
            if current_depth == base_depth + 1:  
                for file in files:
                    file_path = os.path.join(root, file) 

                    try:
                        with open(file_path, 'r') as file_handle:
                            lines = file_handle.readlines()
                            if len(lines) > 1000:
                                file_contents[file] = ''.join(lines[:20]) 
                            else:
                                file_contents[file] = ''.join(lines)


                            folder_names[file] = os.path.relpath(root, base_path)
                            file_names.append(file)
                    except UnicodeDecodeError:
                        print(f"Skipping file due to encoding error: {file_path}")
                        continue
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")

        return file_contents, file_names, folder_names
    def read_file_content(self, command):
        file_pattern = os.path.join(config_path.Case_PATH, f"{command}.err")
        log_files = glob.glob(file_pattern)
        if not log_files:
            print(f"No log files found for command: {command}")
            return
        
        print('log_file:',len(log_files))
        content_total = []
        for log_file in log_files:
            print(f"Reading file: {log_file}")
            with open(log_file, 'r') as file:
                content = file.read()
                print(content)
        content_total.append(content)
        return content_total
    def read_error_content(self, error_file_name):
        if os.path.exists(error_file_name):
            with open(error_file_name, 'r') as file:
                return file.read()
        return None
        
    @staticmethod
    def parse_file_list(rsp):
        pattern = r"###(.*)###"
        match = re.search(pattern, rsp, re.DOTALL)
        your_task_folder = match.group(1) if match else 'None'
        return your_task_folder
    @staticmethod
    def parse_folder_name(rsp):
        pattern = r"```(.*)```"
        match = re.search(pattern, rsp, re.DOTALL)
        your_task_folder = match.group(1) if match else 'None'
        return your_task_folder

