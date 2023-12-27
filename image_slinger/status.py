import torch

def check_cuda_status():
    # Your code to check CUDA availability and memory
    # Return status information
    print("Is CUDA available:", torch.cuda.is_available())
    print("CUDA device count:", torch.cuda.device_count())
    print("Current CUDA Device:", torch.cuda.current_device())
    print("CUDA Device Name:", torch.cuda.get_device_name(torch.cuda.current_device()))
