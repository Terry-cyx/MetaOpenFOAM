# this function is to convert tutorials of openfoam10 to txt file which could be used as a database of metaOpenfoam


import os
import subprocess
import config_path

def read_files_into_dict(base_path):
    file_contents = {}  # 创建一个空字典来存储文件内容
    file_names = []     # 创建一个空列表来存储文件名
    folder_names = {}   # 创建一个空列表来存储每个文件的文件夹名
    base_depth = base_path.rstrip(os.sep).count(os.sep)  # 计算基础路径的深度

    # 读取 base_path 目录下的 Allrun 文件
    allrun_path = os.path.join(base_path, 'Allrun')
    if os.path.isfile(allrun_path):
        try:
            with open(allrun_path, 'r') as file_handle:
                allrun_content = file_handle.read()
        except UnicodeDecodeError:
            print(f"Skipping file due to encoding error: {allrun_path}")
        except Exception as e:
            print(f"Error reading file {allrun_path}: {e}")
    else:
        allrun_content = "None"
    for root, dirs, files in os.walk(base_path):
        current_depth = root.rstrip(os.sep).count(os.sep)
        if current_depth == base_depth + 1:  # 只处理base_path下一级目录的文件
            for file in files:
                file_path = os.path.join(root, file)  # 获取文件的完整路径
                #print(file_path)
                try:
                    with open(file_path, 'r') as file_handle:
                        lines = file_handle.readlines()
                        if len(lines) > 1000:
                            file_contents[file] = "None"
                        else:
                            file_contents[file] = ''.join(lines)
                            #content = file_handle.read()  # 读取文件内容
                            #file_contents[file] = content  # 将内容添加到字典，键是文件名

                        folder_names[file] = os.path.relpath(root, base_path)
                        file_names.append(file)
                except UnicodeDecodeError:
                    print(f"Skipping file due to encoding error: {file_path}")
                    continue
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
    return allrun_content, file_contents, file_names, folder_names

def find_cases(root_dir):
    cases = []
    # 遍历root_dir目录下所有的文件和文件夹
    for root, dirs, files in os.walk(root_dir):
        # 检查当前目录下是否有名为system的文件夹
        if 'system' in dirs:
            #print(root)
            allrun_content, file_contents, file_names, folder_names = read_files_into_dict(root)
            # 提取算例名（当前目录的上一级目录名）
            case_name = os.path.basename(root)
            # 初始化求解器和类别
            solver, category, domain = None, None, None
            # 遍历路径找到XXFoam或者记录所在领域，最多向上遍历三层
            current_path = os.path.dirname(root)
            max_levels = 3  # 设置最大向上遍历的层数
            found_foam = False
            while current_path and os.path.basename(current_path) != root_dir and max_levels > 0:
                dir_name = os.path.basename(current_path)
                if dir_name.endswith('Foam'):
                    solver = dir_name
                    domain = os.path.basename(os.path.dirname(current_path))
                    found_foam = True
                    break
                elif max_levels == 3:
                    category = dir_name
                current_path = os.path.dirname(current_path)
                max_levels -= 1  # 减少一个遍历层级
            
            if not found_foam:
                category = None
                # 如果三级后还没有找到Foam，尝试从根目录的下两级目录中提取信息
                relative_path = os.path.relpath(root, root_dir)
                path_components = relative_path.split(os.sep)
                if(len(path_components)==3):
                    domain = path_components[0]
                    solver = path_components[1]
                elif(len(path_components)==4):
                    domain = path_components[0]
                    solver = path_components[1]
                    category = path_components[2]

            
            # 添加找到的信息到cases列表
            cases.append({
                'case_name': case_name,
                'solver': solver,
                'category': category,
                'domain': domain,
                'folder_names':folder_names,
                'file_names':file_names,
                'file_contents':file_contents,
                'allrun':allrun_content
            })

    return cases

def save_cases_to_file(cases, file_path):

    text_to_save = "Here is the list of tutorials in openfoam 10,\n"
    
    for case in cases:
        case_name = case['case_name']
        case_domain = case['domain']
        case_category = case['category']
        case_solver = case['solver']

        text_to_save += "###case begin:\n"
        text_to_save += f"case name: {case_name}\n"
        text_to_save += f"case domain: {case_domain}\n"
        text_to_save += f"case category: {case_category}\n"
        text_to_save += f"case solver: {case_solver}\n"
        files = case['file_names']
        text_to_save += f"case input name:{files}\n"
        text_to_save += f"corresponding input folder:{case['folder_names']}\n"

        for file_name in files:
            folder = case['folder_names'][file_name]
            file_content = case['file_contents'][file_name]
            text_to_save += f"```input_file_begin: input {file_name} file of case {case_name} (domain: {case_domain}, category: {case_category}, solver:{case_solver}) in {folder} folder:\n\n"
            text_to_save += f"{file_content}\n"
            text_to_save += "input_file_end.```\n\n"
        
        text_to_save += "case end.###\n\n"

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text_to_save)

def save_cases_summary(cases, file_path):

    text_to_save = "Here is the list of tutorials in openfoam 10,\n"
    
    for case in cases:
        case_name = case['case_name']
        case_domain = case['domain']
        case_category = case['category']
        case_solver = case['solver']

        text_to_save += "###case begin:\n"
        text_to_save += f"case name: {case_name}\n"
        text_to_save += f"case domain: {case_domain}\n"
        text_to_save += f"case category: {case_category}\n"
        text_to_save += f"case solver: {case_solver}\n"
        files = case['file_names']
        text_to_save += f"case input name:{files}\n"
        text_to_save += f"corresponding input folder:{case['folder_names']}\n"
        text_to_save += "case end.###\n\n"

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text_to_save)

def save_all_run(cases, file_path):

    # 遍历cases列表，每个case为一个字典
    text_to_save = "Here is the list of linux execution command allrun files of specific case in openfoam 10,\n"
    for case in cases:
        case_name = case['case_name']
        case_domain = case['domain']
        case_category = case['category']
        case_solver = case['solver']
        all_run = case['allrun']
        text_to_save += f"```input_file_begin: linux execution command allrun file of case {case_name} (domain: {case_domain}, category: {case_category}, solver:{case_solver}):\n"
        text_to_save += f"{all_run}\n"
        text_to_save += "input_file_end.```\n\n"
        #如果case中有文件名信息，则遍历并添加每个文件的信息

    # 打开文件，并写入构建的字符串
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text_to_save)

def get_commands_from_directory(directory_path):
    # 检查目录是否存在
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"The directory {directory_path} does not exist.")
    
    # 获取目录下的所有文件名
    commands = []
    for file_name in os.listdir(directory_path):
        full_path = os.path.join(directory_path, file_name)
        if os.path.isfile(full_path):
            commands.append(file_name)
    
    return commands

def get_command_help(command, directory_path):
    full_command = os.path.join(directory_path, command) + " -help"
    try:
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return str(e)

def save_all_commands(commands, file_path):

    # 打开文件，并写入构建的字符串
    text_to_save = ""
    for command in commands:
        text_to_save += f"{command}\n"
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text_to_save)

def save_all_commands_help(commands, commands_help, file_path):
    
    # 遍历cases列表，每个case为一个字典
    text_to_save = "Here is the list of linux execution command help in openfoam 10,\n"
    for command in commands:
        text_to_save += "```input_file_begin:\n"
        text_to_save += f"{commands_help[command]}\n"
        text_to_save += "input_file_end.```\n\n"
        #如果case中有文件名信息，则遍历并添加每个文件的信息

    # 打开文件，并写入构建的字符串
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text_to_save)


wm_project_dir = os.getenv('WM_PROJECT_DIR')
if wm_project_dir is None:
    raise EnvironmentError("The environment variable WM_PROJECT_DIR is not set.")

tutorial_path = f"{wm_project_dir}/tutorials"
cases_info = find_cases(tutorial_path)

print(len(cases_info))
print(cases_info[0]['case_name'])
print(cases_info[0]['solver'])
print(cases_info[0]['domain'])
print('allrun:',cases_info[0]['allrun'])
files = cases_info[0]['file_names']
print(files)
print(cases_info[0]['folder_names'][files[0]])

database_tutorials_path = f'{config_path.Database_PATH}/openfoam_tutorials.txt'
save_cases_to_file(cases_info, database_tutorials_path)

database_tutorials_summary_path = f'{config_path.Database_PATH}/openfoam_tutorials_summary.txt'
save_cases_summary(cases_info, database_tutorials_summary_path)

database_allrun_path = f'{config_path.Database_PATH}/openfoam_allrun.txt'
save_all_run(cases_info, database_allrun_path)


commands_path = os.path.join(wm_project_dir, 'platforms/linux64GccDPInt32Opt/bin')

commands = get_commands_from_directory(commands_path)

command_context = {}
for command in commands:
    help_output = get_command_help(command, commands_path)
    command_context[command] = help_output

command_file_path = f'{config_path.Database_PATH}/openfoam_commands.txt'
help_file_path = f'{config_path.Database_PATH}/openfoam_command_helps.txt'

save_all_commands(commands,command_file_path)
save_all_commands_help(commands,command_context,help_file_path)


