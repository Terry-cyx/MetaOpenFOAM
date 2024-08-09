
import re
import subprocess
from typing import List
import os
import shutil

from metagpt.actions import Action
from metagpt.schema import Message

from qa_module import AsyncQA_allrun
import config_path
import sys
import glob
from Statistics import global_statistics

class RunnerAction(Action):

    PROMPT_TEMPLATE_allrun: str = """
        Your task is to write linux execution command allrun file to meet the user requirement: {requirement}.
        The input file list is {file_list}.
        Here is a openfoam allrun file similar to the user requirements:
        {tutorial}
        Please take this file as a reference.
        The possible command list is
        {commands}
        The possible run list is
        {runlists}
        Make sure the written linux execution command are coming from the above two lists.
        According to your task, return ```your_allrun_file_here ``` with NO other texts
        """
    PROMPT_TEMPLATE_review: str = """
        Your task is to review linux execution command ({command}) to meet the user requirement: {requirement}.
        with hlep:
        {command_help}
        make sure the command is correctly used. 
        According to your task, return ```your_allrun_file_here ``` with NO other texts
        """
    async def run(self, with_messages:List[Message]=None, **kwargs) -> Message:

        allrun_file_path = f'{config_path.Case_PATH}/Allrun'

        allrun_write = "None"

        if os.path.exists(allrun_file_path):

            with open(allrun_file_path, 'r', encoding='utf-8') as allrun_file:

                allrun_write = allrun_file.read()
                print('allrun_write2:',allrun_write)

        if allrun_write == "None":

            requirement = with_messages[0].content
            async_qa_allrun = AsyncQA_allrun()
            runlists = ['isTest', 'getNumberOfProcessors','getApplication','runApplication','runParallel','compileApplication','cloneCase','cloneMesh']
            commands = self.read_commands(config_path.Database_PATH)
            file_list = self.read_files(config_path.Case_PATH)

            find_tutorial = self.read_tutorial()
            #print("find_tutorial:",find_tutorial)
            case_name = self.get_case_name(find_tutorial)
            #print("case_name:",case_name)
            allrun_tutorial = self.get_allrun_tutorial(case_name)
            #print("allrun_tutorial:",allrun_tutorial)

            prompt_allrun = self.PROMPT_TEMPLATE_allrun.format(
                requirement=requirement, 
                tutorial = allrun_tutorial,
                file_list = file_list, 
                commands = commands, 
                runlists = runlists)
            
            rsp = await async_qa_allrun.ask(prompt_allrun) 
            result = rsp["result"]
            #doc = rsp["source_documents"]
            #print("allrun_source_documents:",doc[0])
            #print("allrun:",result)
            allrun_write = self.parse_allrun(result)
            with open(allrun_file_path, 'w') as outfile:  
                outfile.write(allrun_write)
                
        print('allrun_write:',allrun_write)

        out_file = os.path.join(config_path.Case_PATH, 'Allrun.out')
        err_file = os.path.join(config_path.Case_PATH, 'Allrun.err')

        self.remove_log_files(config_path.Case_PATH)
        if os.path.exists(err_file):
            os.remove(err_file)
        if os.path.exists(out_file):
            os.remove(out_file)
        self.remove_err_files(config_path.Case_PATH)
        self.remove_pro_files(config_path.Case_PATH)
        dir_path = config_path.Case_PATH
        initial_files = {}
        for subdir in os.listdir(dir_path):
            subdir_path = os.path.join(dir_path, subdir)
            if os.path.isdir(subdir_path):
                initial_files[subdir] = set(os.listdir(subdir_path))

        print("initial_files:",initial_files)

        self.run_command(allrun_file_path, out_file, err_file, config_path.Case_PATH)
        # check endTime and folder time
        error_logs = self.check_foam_errors(config_path.Case_PATH)

        print('error_logs:',error_logs)

        commands_run = self.extract_commands_from_allrun_out(out_file)


        command = self.compare_commands_with_error_logs(commands_run, error_logs)

        if not error_logs:
            print("No error logs found.")
            result = "None"
            self.check_endtime_and_folder(config_path.Case_PATH)

        elif not command:
            print("Error: Could not find the erroneous command.")
            #result = commands_run
            result = ", ".join(commands_run)
        else:
            print('command line error:', command[0]['command'])
            print('error:', command[0]['error_content'])

            error_file_name = f"{config_path.Case_PATH}/{command[0]['command']}.err"
            self.save_error_content(command[0]['error_content'], error_file_name)
            result = command[0]['command']
            self.check_time_and_folder(config_path.Case_PATH)
            if "mesh" in result.lower():
                global_statistics.Executability = 0
            else:
                if global_statistics.Executability == 0:
                    global_statistics.Executability = 1
                    print("Executability:",global_statistics.Executability)
            # delete generated files
            if config_path.should_stop == False:
                final_files = {}
                for subdir in os.listdir(dir_path):
                    subdir_path = os.path.join(dir_path, subdir)
                    if os.path.isdir(subdir_path):
                        final_files[subdir] = set(os.listdir(subdir_path))

                print("final_files:",final_files)

                for subdir in final_files:
                    new_files = final_files[subdir] - initial_files.get(subdir, set())
                    subdir_path = os.path.join(dir_path, subdir)
                    for file in new_files:
                        file_path = os.path.join(subdir_path, file)
                        try:
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                                print(f"Already deleted: {file_path}")
                            elif os.path.isdir(file_path):
                                os.rmdir(file_path)  
                                print(f"Already deleted: {file_path}")
                        except Exception as e:
                            print(f"Delete:{file_path} occur error: {e}")
        # if error is found, need to compare the new file list and old file list and convert to the old one
        global_statistics.loop = global_statistics.loop + 1
        print('loop:', global_statistics.loop)
        if global_statistics.loop >= config_path.max_loop:
            print('reach max loops', config_path.max_loop)
            config_path.should_stop = True

        if config_path.should_stop == True:
            list_show, total_files, total_lines = self.count_files_and_lines(config_path.Case_PATH)
            global_statistics.total_lines_of_inputs += total_lines
            global_statistics.number_of_input_files += total_files
            global_statistics.lines_per_file += total_lines/total_files
            self.display_results(list_show, total_files, total_lines)

        return result


        
    def read_file_content(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return None
    def read_commands(self, database_path):

        file_path = f"{database_path}/openfoam_commands.txt"
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        with open(file_path, 'r') as file:
            commands = [line.strip() for line in file if line.strip()]
    
        return commands
    def read_files(self, base_path):
        file_names = []   
        base_depth = base_path.rstrip(os.sep).count(os.sep) 
        for root, dirs, files in os.walk(base_path):
            current_depth = root.rstrip(os.sep).count(os.sep)
            if current_depth == base_depth + 1: 
                for file in files:
                    file_path = os.path.join(root, file)  

                    try:
                        with open(file_path, 'r') as file_handle:
                            content = file_handle.read() 
                            file_names.append(file)
                    except UnicodeDecodeError:
                        print(f"Skipping file due to encoding error: {file_path}")
                        continue
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")
        return file_names
    def read_tutorial(self):
        save_path = config_path.Case_PATH
        file_path = f"{save_path}/find_tutorial.txt"
        with open(file_path, 'r') as file_handle:
            content = file_handle.read() 
        return content
    def get_case_name(self, content):
        match = re.search(r'case name:\s*(.+)', content)
        your_task_folder = match.group(1).strip() if match else 'None'
        return your_task_folder
    
    def get_allrun_tutorial(self,case_name):

        filename = 'openfoam_allrun.txt' 
        file_path = f"{config_path.Database_PATH}/{filename}"
        end_marker = 'input_file_end.```'  
        with open(file_path, 'r') as file:  
            lines = file.readlines()  
        extracted_content = []
        found_keyword = False  
        for line in lines:  
            if found_keyword:  
                if end_marker in line:  
                    break  
                extracted_content.append(line)  
            elif case_name in line:  
                found_keyword = True  
                continue  

        return ''.join(extracted_content)  
    
    def parse_allrun(self, allrun_total):
        print('allrun_total:',allrun_total)

        match = re.search(r'```(?:.*?\n)(.*?)\n```', allrun_total, re.DOTALL)
        allrun_text = match.group(1).strip() if match else 'None'
        return allrun_text
    

    def run_command(self, script_path, out_file, err_file, working_dir):
        with open(out_file, 'w') as out, open(err_file, 'w') as err:
            process = subprocess.Popen(['bash', script_path], cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            out.write(stdout)
            err.write(stderr)
                        
        return "None"
    

    def check_foam_errors(self, log_dir):
        error_logs = []

        log_files = [f for f in os.listdir(log_dir) if f.startswith('log')]

        for log_file in log_files:
            log_path = os.path.join(log_dir, log_file)
            with open(log_path, 'r') as file:
                lines = file.readlines()

            print('log_file:',log_file)
            error_indices = None
            for i, line in enumerate(lines):
                if 'error' in line.lower() and 'foam' in line.lower():
                    error_indices = i
                    break

            if error_indices is None:
                continue

            start_index = max(0, error_indices - 30)
            end_index = min(len(lines), error_indices + 60)

            error_content = [line.strip() for line in lines[start_index:end_index]]

            if error_content:
                error_logs.append({
                    'file': log_file,
                    'error_content': "\n".join(error_content)
                })

        return error_logs

    def remove_log_files(self, directory):
        log_files = glob.glob(os.path.join(directory, 'log*'))
        for log_file in log_files:
            os.remove(log_file)

    def extract_commands_from_allrun_out(self, allrun_out_path):
        commands = []
        with open(allrun_out_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            if line.startswith('Running '):

                command_part = line.split('Running ')[1]

                command = command_part.split(' on ')[0]
                command_true = command.split()[0]
                commands.append(command_true)
        
        return commands
    def compare_commands_with_error_logs(self, commands_run, error_logs):
        comparison_results = []
        for command in commands_run:
            for error_log in error_logs:
                if command in error_log['file']:
                    comparison_results.append({
                        'command': command,
                        'error_content': error_log['error_content']
                    })
                    break  # Assuming one match per command is enough
        return comparison_results
    
    def save_error_content(self, error_content, error_file_name):
        with open(error_file_name, 'w') as file:
            file.write(error_content)
    def remove_err_files(self, directory):

        err_files = glob.glob(os.path.join(directory, '*.err'))

        for err_file in err_files:
            try:
                os.remove(err_file)
                print(f"Deleted file: {err_file}")
            except OSError as e:
                print(f"Error deleting file {err_file}: {e}")
    def remove_pro_files(self, directory):

        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path) and item.startswith('processor'):
                try:
                    shutil.rmtree(item_path)
                    print(f"Deleted folder: {item_path}")
                except Exception as e:
                    print(f"Error deleting folder {item_path}: {e}")

    def check_endtime_and_folder(self, address):
        control_dict_path = os.path.join(address, 'system', 'controlDict')
        
        if not os.path.isfile(control_dict_path):
            print("controlDict file not found.")
            return
        
        endtime_value = None

        with open(control_dict_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.strip().startswith('endTime'):
                    endtime_value = line.split('endTime', 1)[1].strip().strip(';').replace(" ", "")
                    break

        if endtime_value is None:
            print("endTime not found in controlDict.")
            return

        for folder_name in os.listdir(address):
            folder_path = os.path.join(address, folder_name)
            if os.path.isdir(folder_path) and folder_name == endtime_value:
                global_statistics.Executability = 3
                print("Executability: 3")
                config_path.should_stop = True


        #print("not reach endTime")
        return
    def check_time_and_folder(self, address):
        control_dict_path = os.path.join(address, 'system', 'controlDict')
        
        if not os.path.isfile(control_dict_path):
            print("controlDict file not found.")
            return
        
        endtime_value = None

        with open(control_dict_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.strip().startswith('endTime'):
                    endtime_value = line.split('endTime', 1)[1].strip().strip(';').replace(" ", "")
                    break

        if endtime_value is None:
            print("endTime not found in controlDict.")
            return
        
        for folder_name in os.listdir(address):
            folder_path = os.path.join(address, folder_name)
            if os.path.isdir(folder_path):
                if re.search(r'\b(?!0\b)\d+\b', folder_name):
                    global_statistics.Executability = 2
                    print("Executability: 2")
                
        for folder_name in os.listdir(address):
            folder_path = os.path.join(address, folder_name)
            if os.path.isdir(folder_path) and folder_name == endtime_value:
                global_statistics.Executability = 3
                print("(A)\tExecutability: 3")
                config_path.should_stop = True

        #print("not runnable")
        return
    
    def is_number(self,s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def count_files_and_lines(self,path):
        result = {}
        total_files = 0
        total_lines = 0
        for subdir in os.listdir(path):
            subdir_path = os.path.join(path, subdir)

            if os.path.isdir(subdir_path) and not (
                (self.is_number(subdir) and float(subdir) != 0) or 
                subdir.startswith("processor") or 
                subdir.startswith("post")
            ):
                file_count = 0
                line_count = 0

                for item in os.listdir(subdir_path):
                    item_path = os.path.join(subdir_path, item)
                    if os.path.isfile(item_path):
                        file_count += 1
                        with open(item_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            line_count += len(lines)

                result[subdir] = {'file_count': file_count, 'line_count': line_count}
                total_files += file_count
                total_lines += line_count
        return result, total_files, total_lines
    
    def display_results(self, results, total_files, total_lines):
        print(f"{'Subdirectory':<40} {'File Count':<15} {'Line Count':<15}")
        print("="*70)
        for subdir, counts in results.items():
            print(f"{subdir:<40} {counts['file_count']:<15} {counts['line_count']:<15}")
        
        print("="*70)
        print(f"{'Total':<40} {total_files:<15} {total_lines:<15}")

