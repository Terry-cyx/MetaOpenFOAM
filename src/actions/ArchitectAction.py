
import re
from typing import List
import os
from metagpt.actions import Action

from metagpt.schema import Message
from metagpt.logs import logger

from qa_module import AsyncQA_tutorial_name
import config_path
from Statistics import global_statistics

class ArchitectAction(Action):

    PROMPT_TEMPLATE_divide_task: str = """
    User requirement:
    {requirement}
    Your task is to generate the openfoam input foamfiles list following file structure of OpenFOAM cases to meet the user requirements.
    Here is a openfoam case similar to the user requirements
    The following is a case of openfoam, which is similar to the user's requirements:
    {tutorial}
    Please take this case as a reference. generate the openfoam input foamfiles list following file structure of OpenFOAM cases to meet the user requirements.
    You should splits foamfiles list into several subtasks, and one subtask corresponds to one input foamfile
    Return ```splits into number_of_subtasks subtasks:  
    subtask1: to Write a OpenFoam specific_file_name foamfile in specific_folder_name folder that could be used to meet user requirement:{requirement}.
    subtask2: to Write a OpenFoam specific_file_name foamfile in specific_folder_name folder that could be used to meet user requirement:{requirement}.
    ...

    ``` with NO other texts,
    your subtasks:
    """

    PROMPT_TEMPLATE3: str = """
    User requirement:
    {requirement}
    Your task is to generate the openfoam input foamfiles list following file structure of OpenFOAM cases to meet the user requirements.
    You should splits foamfiles list into several subtasks, and one subtask corresponds to one input foamfile
    Return ```splits into number_of_subtasks subtasks:  
    subtask1: to Write a OpenFoam specific_file_name foamfile in specific_folder_name folder that could be used to meet user requirement:{requirement}.
    subtask2: to Write a OpenFoam specific_file_name foamfile in specific_folder_name folder that could be used to meet user requirement:{requirement}.
    ...

    ``` with NO other texts,
    your subtasks:
    """
    PROMPT_TEMPLATE_Find_case: str = """
    Your task is to find the case that is most similar to the user's requirement:
    {requirement}
    Your task is to generate the openfoam input foamfiles list following file structure of OpenFOAM cases to meet the user requirements.
    You should splits foamfiles list into several subtasks, and one subtask corresponds to one input foamfile
    Return ```
    case name: specific_case_name
    case domain: specific_case_domain
    case category: specific_case_category
    case solver: specific_case_solver
    file_names: specific_file_names
    file_folders: specific_file_folders
    ...

    ``` with NO other texts
    """
    PROMPT_Translate: str = """
        Translate the following user request into the specified standard format:
        User request:
        {requirement}
        Standard format:
        case name: specific_case_name
        case domain: specific_case_domain
        case category: specific_case_category
        case solver: specific_case_solver
        Note that case domain could only be one of following strings:
        [basic, compressible, discreteMethods, DNS, electromagnetics, financial, heatTransfer, incompressible, lagrangian, mesh, multiphase, stressAnalysis]
    """

    PROMPT_Find: str = """
        Find the OpenFOAM case that most closely matches the following case:
        {user_case}
        where case domain, case category and case solver should be matched with the highest priority
    """

    name: str = "ArchitectAction"

    async def run(self, with_messages:List[Message]=None, **kwargs) -> List[str]:

        async_qa_tutotial = AsyncQA_tutorial_name()

        prompt_Translate = self.PROMPT_Translate.format(requirement=with_messages[0].content)
        rsp = await async_qa_tutotial.ask(prompt_Translate)
        user_case = rsp["result"]
        print('user_case:',user_case)
        case_name = self.parse_case_name(user_case)
        if config_path.run_times > 1:
            config_path.Case_PATH = f"{config_path.Run_PATH}/{case_name}_{global_statistics.runtimes}"
        else:
            config_path.Case_PATH = f"{config_path.Run_PATH}/{case_name}"
        os.makedirs(config_path.Case_PATH, exist_ok=True)

        prompt_Find = self.PROMPT_Find.format(user_case=user_case)
        rsp = await async_qa_tutotial.ask(prompt_Find)
        doc = rsp["source_documents"]
        tutorial = doc[0]
        print('find_case',tutorial)
        save_path = config_path.Case_PATH

        self.save_find_tutorial(tutorial.page_content, save_path)

        prompt_subtask = self.PROMPT_TEMPLATE_divide_task.format(requirement=with_messages[0].content, tutorial=tutorial)
        rsp = await async_qa_tutotial.ask(prompt_subtask)
        result = rsp["result"]
        logger.info(str(result))

        subtasks: List[str] = self.split_subtask(result)
        
        return subtasks
    
    def split_subtask(self, content: str) -> list:

        header_pattern = re.compile(r'splits into (\d+) subtasks:')

        subtask_pattern = re.compile(r'subtask\d+: (.*)')

        header_match = header_pattern.search(content)
        if header_match:
            number_of_subtasks = int(header_match.group(1))
        else:
            return []

        subtasks = []

        for match in subtask_pattern.finditer(content):

            subtasks.append(match.group(1))

        if len(subtasks) != number_of_subtasks:

            print("Warning: Declared number of subtasks does not match extracted subtasks.")
        
        return subtasks
    @staticmethod
    def parse_case_name(rsp):
        match = re.search(r'case name:\s*(.+)', rsp)
        your_task_folder = match.group(1).strip() if match else 'None'
        return your_task_folder
    def save_find_tutorial(self, tutorial, save_path):
        file_path = f"{save_path}/find_tutorial.txt"
        with open(file_path, 'w') as file:
            file.write(tutorial) 

        print(f"File saved successfully at {file_path}")
        return 0
