# deep-chess-playground

Where deep learning meets chess.

![Chess AI](assets/chessai.jpg)

This repository aims to implement techniques for neural chess engines, providing an in-depth look at the practical application of AI in chess game.

## Table of contents

1. [Play chessbots on lichess](#play-chessbots-on-lichess)
2. [Run chessbots locally](#run-chessbots-locally)
    - [Setup](#setup)
    - [Play](#play)
3. [Train your own chessbots](#train-your-own-chessbots)
    - [Data loading](#data-loading)
    - [Data processing](#data-processing)
    - [Training](#training)

## Play chessbots on lichess

COMING SOON

## Run chessbots locally

### Setup

It is recommended to use Anaconda for managing your Python environment, especially if you plan to use GPU acceleration. However, we also provide instructions for standard Python with pip.

#### Option 1: Using Anaconda (recommended)

1. Download and install Anaconda from the official website: [https://www.anaconda.com/products/distribution](https://www.anaconda.com/products/distribution).

2. Open Anaconda Prompt and run the following command to create a virtual environment:
   ```
   conda create --name deep_chess_playground python=3.10
   ```

3. Activate the environment:
   ```
   conda activate deep_chess_playground
   ```

4. Install PyTorch. Follow the instructions at [PyTorch website](https://pytorch.org/get-started/locally/). 
   Choose the compute platform (CUDA or CPU) depending on whether you have a GPU or not.

5. Install PyTorch Lightning:
   ```
   conda install pytorch-lightning -c conda-forge
   ```

6. Install deep-chess-playground:
   ```
   pip install deep-chess-playground
   ```

#### Option 2: Using standard Python and pip

1. Ensure you have Python 3.10 or later installed. You can download it from [python.org](https://www.python.org/downloads/).

2. Create a virtual environment:
   ```
   python -m venv deep_chess_env
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     deep_chess_env\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source deep_chess_env/bin/activate
     ```

4. Install PyTorch. Follow the instructions at [PyTorch website](https://pytorch.org/get-started/locally/). 
   Choose the compute platform (CUDA or CPU) depending on whether you have a GPU or not.

5. Install PyTorch Lightning:
   ```
   pip install pytorch-lightning
   ```

6. Install deep-chess-playground:
   ```
   pip install deep-chess-playground
   ```

### Play

COMING SOON

## Train your own chessbots

### Data loading

<p align="center">
  <img src="assets/data_loading.png" alt="Data loading"/>
</p>

If you need a lot of training data, you can use the [lichess.org open database](https://database.lichess.org/) which has more than 5 000 000 000 games recorded starting from January 2013!

### Training

COMING SOON
