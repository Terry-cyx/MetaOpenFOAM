# Define the Python interpreter
PYTHON=python
Case_input=Cavity

# Define the paths to the Python scripts and input file
SRC_DIR=src
INPUT_DIR=inputs
INPUT_FILE=$(INPUT_DIR)/$(Case_input).yaml
CONFIG_PATH=$(SRC_DIR)/config_path.py
TUTORIAL_POSTPROCESS=$(SRC_DIR)/Tutorial_postprocess.py
LANGCHAIN_DB_ADD_SUMMARY=$(SRC_DIR)/Langchain_database_add_tutorial_summary.py
LANGCHAIN_DB_ADD_TUTORIAL=$(SRC_DIR)/Langchain_database_add_tutorial.py
LANGCHAIN_DB_ADD_COMMAND=$(SRC_DIR)/Langchain_database_add_command.py
LANGCHAIN_DB_ADD_ALLRUN=$(SRC_DIR)/Langchain_database_add_allrun.py
METAOPENFOAM_V2=$(SRC_DIR)/metaOpenfoam_v2.py
TEST = $(SRC_DIR)/test.py

# Define the CONFIG_FILE_PATH environment variable
CONFIG_FILE_PATH=$(INPUT_FILE)

# Export the CONFIG_FILE_PATH environment variable
export CONFIG_FILE_PATH

# Default target
all: run_config run_postprocess run_db_add run_main

# Run config_path.py to load system paths with input file
run_config:
	@echo "Running config_path.py to load system paths..."
	$(PYTHON) $(CONFIG_PATH) $(INPUT_FILE)

# Run Tutorial_postprocess.py for data preprocessing
run_postprocess:
	@echo "Running Tutorial_postprocess.py for data preprocessing..."
	$(PYTHON) $(TUTORIAL_POSTPROCESS)

# Run Langchain_database_add scripts to store processed data
run_db_add:
	@echo "Running Langchain_database_add_tutorial_summary.py..."
	$(PYTHON) $(LANGCHAIN_DB_ADD_SUMMARY)
	@echo "Running Langchain_database_add_tutorial.py..."
	$(PYTHON) $(LANGCHAIN_DB_ADD_TUTORIAL)
	@echo "Running Langchain_database_add_command.py..."
	$(PYTHON) $(LANGCHAIN_DB_ADD_COMMAND)
	@echo "Running Langchain_database_add_allrun.py..."
	$(PYTHON) $(LANGCHAIN_DB_ADD_ALLRUN)

# Run metaOpenfoam_v2.py to execute the main program
run_main:
	@echo "Running metaOpenfoam_v2.py to execute the main program..."
	$(PYTHON) $(METAOPENFOAM_V2)

# Clean up generated files (if needed)
clean:
	@echo "Cleaning up..."
	# Add cleanup commands here, for example, deleting generated files
	# rm -f *.pyc
