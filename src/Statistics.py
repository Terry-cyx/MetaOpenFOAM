import os

class Statistics:
    def __init__(self):
        self.loop = 0
        self.runtimes = 0
        self.Executability = 0
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.running_time = 0
        self.number_of_input_files = 0
        self.lines_per_file = 0
        self.total_lines_of_inputs = 0

    def reset(self):
        self.__init__()

    def save(self, other):
        self.loop += other.loop
        self.Executability += other.Executability
        self.total_tokens += other.total_tokens
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.running_time += other.running_time
        self.number_of_input_files += other.number_of_input_files
        self.lines_per_file += other.lines_per_file
        self.total_lines_of_inputs += other.total_lines_of_inputs

    def average(self, count):
        self.loop /= count
        self.Executability /= count
        self.total_tokens /= count
        self.prompt_tokens /= count
        self.completion_tokens /= count
        self.running_time /= count
        self.number_of_input_files /= count
        self.lines_per_file /= count
        self.total_lines_of_inputs /= count

    def display(self):
        print(f"Average Loop: {self.loop}")
        print(f"Average Executability: {self.Executability}")
        print(f"Average Total Tokens: {self.total_tokens}")
        print(f"Average Prompt Tokens: {self.prompt_tokens}")
        print(f"Average Completion Tokens: {self.completion_tokens}")
        print(f"Average Running Time: {self.running_time}")
        print(f"Average Number of Input Files: {self.number_of_input_files}")
        print(f"Average Lines Per File: {self.lines_per_file}")
        print(f"Average Total Lines of Inputs: {self.total_lines_of_inputs}")
        
    def save_to_file(self, directory):
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, 'statistics.txt')
        with open(file_path, 'w') as f:
            f.write(f"Loop: {self.loop}\n")
            f.write(f"Executability: {self.Executability}\n")
            f.write(f"Total Tokens: {self.total_tokens}\n")
            f.write(f"Prompt Tokens: {self.prompt_tokens}\n")
            f.write(f"Completion Tokens: {self.completion_tokens}\n")
            f.write(f"Running Time: {self.running_time}\n")
            f.write(f"Number of Input Files: {self.number_of_input_files}\n")
            f.write(f"Lines Per File: {self.lines_per_file}\n")
            f.write(f"Total Lines of Inputs: {self.total_lines_of_inputs}\n")

    def save_ave_file(self, directory):
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, 'ave_statistics.txt')
        with open(file_path, 'w') as f:
            f.write(f"Loop: {self.loop}\n")
            f.write(f"Executability: {self.Executability}\n")
            f.write(f"Total Tokens: {self.total_tokens}\n")
            f.write(f"Prompt Tokens: {self.prompt_tokens}\n")
            f.write(f"Completion Tokens: {self.completion_tokens}\n")
            f.write(f"Running Time: {self.running_time}\n")
            f.write(f"Number of Input Files: {self.number_of_input_files}\n")
            f.write(f"Lines Per File: {self.lines_per_file}\n")
            f.write(f"Total Lines of Inputs: {self.total_lines_of_inputs}\n")

global_statistics = Statistics()