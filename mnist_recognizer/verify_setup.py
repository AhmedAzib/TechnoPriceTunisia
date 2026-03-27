import torch
import torchvision
import matplotlib
import pandas
import numpy

print(f"Torch version: {torch.__version__}")
print(f"Torchvision version: {torchvision.__version__}")
print(f"Matplotlib version: {matplotlib.__version__}")
print(f"Pandas version: {pandas.__version__}")
print(f"Numpy version: {numpy.__version__}")

if torch.cuda.is_available():
    print("CUDA is available.")
else:
    print("CUDA is NOT available (using CPU).")
