from fastapi import FastAPI, HTTPException
from .image_generator import generate_image
from .status import check_cuda_status
from threading import Lock

app = FastAPI()
generate_lock = Lock()

@app.get("/status")
async def status():
    return check_cuda_status()

@app.post("/generate-image")
async def generate(prompt: str, negative_prompt: str, width: int, height: int, num_inference_steps: int):
    with generate_lock:  # Ensures only one image generation process at a time
        return generate_image(prompt, negative_prompt, width, height, num_inference_steps)
