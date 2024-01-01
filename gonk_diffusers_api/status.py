import torch

def check_cuda_status(app):
    status_info = {
        "cuda_available": torch.cuda.is_available(),
        "cuda_device_count": torch.cuda.device_count(),
        "current_cuda_device_info": {},
    }

    if status_info["cuda_available"]:
        current_cuda_device = torch.cuda.current_device()
        device_properties = torch.cuda.get_device_properties(current_cuda_device)

        total_memory = device_properties.total_memory
        allocated_memory = torch.cuda.memory_allocated(current_cuda_device)
        reserved_memory = torch.cuda.memory_reserved(current_cuda_device)

        # Total memory - (Allocated memory + Reserved memory) to get the actual available memory
        actual_available_memory = total_memory - (allocated_memory + reserved_memory)

        status_info['current_cuda_device_info'].update({
            "current_cuda_device": current_cuda_device,
            "cuda_device_name": torch.cuda.get_device_name(current_cuda_device),
            "max_memory": total_memory,
            "allocated_memory": allocated_memory,
            "reserved_memory": reserved_memory,
            "actual_available_memory": actual_available_memory
        })

    return status_info
