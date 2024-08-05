# MetaOpenFOAM
MetaOpenFOAM: an LLM-based multi-agent framework for CFD

# MetaOpenFOAM Setup Guide

## Environment Requirements

- Python >= 3.9
- MetaGPT v0.8.0
- Langchain v0.1.19
- OpenFOAM 10

## Step 1: Setup Python Environment

1. Create a Python >= 3.9 environment. In this example, we'll create a Python 3.11.4 environment in a directory called `your_dir`.

    ```bash
    conda create --prefix your_dir python=3.11.4
    ```

2. Activate the environment.

    ```bash
    conda activate your_dir
    ```

3. Verify the Python version.

    ```bash
    python --version
    ```

## Step 2: Setup MetaGPT

1. Create a new working directory called `MetaOpenFOAM_path` and navigate to it.

    ```bash
    mkdir MetaOpenFOAM_path
    cd MetaOpenFOAM_path
    ```

2. Clone the MetaGPT repository and install the development version.

    ```bash
    git clone https://github.com/geekan/MetaGPT.git
    cd MetaGPT
    pip install -e .
    ```

## Step 3: Install Langchain

1. Install Langchain version 0.1.19.

    ```bash
    pip install langchain==0.1.19
    ```

2. Verify the Langchain version.

    ```bash
    python -c "import langchain; print(langchain.__version__)"
    ```

## Step 4: Setup OpenFOAM

1. After installing OpenFOAM 10, activate the OpenFOAM environment.

    ```bash
    source OpenFOAM_PATH/OpenFOAM/OpenFOAM-10/etc/bashrc
    ```

2. Verify the environment activation.

    ```bash
    echo $WM_PROJECT_DIR
    ```

## Step 5: Install MetaOpenFOAM

1. Clone the MetaOpenFOAM repository.

    ```bash
    git clone https://github.com/Terry-cyx/MetaOpenFOAM.git
    ```

2. Set the `PYTHONPATH` to include the MetaOpenFOAM directory.

    ```bashac
    export PYTHONPATH="MetaOpenfoam_dir/metaOpenfoam:$PYTHONPATH"
    ```

3. Run `make` to build the project.

    ```bash
    make
    ```

Now your environment is set up and you can start working with MetaOpenFOAM.

Once my paper is published, the source code will be made public

## Citation
If you find our work useful in your research, please consider citing:

```bibtex
@article{Chen2024MetaOpenFOAM,
  title={MetaOpenFOAM: an LLM-based multi-agent framework for CFD},
  author={Yuxuan Chen and Xu Zhu and Hua Zhou and Zhuyin Ren},
  journal={Journal Name},
  year={2024},
  doi={http://arxiv.org/abs/2407.21320}
}
