from diffusers import StableDiffusionXLPipeline
import torch

def generate_image(prompt, negative_prompt, width, height, num_inference_steps):
    # Your existing code for image generation
    # Return the generated image or image data
    pipe = StableDiffusionXLPipeline.from_pretrained("segmind/Segmind-Vega", torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
    pipe.to("cuda")
    #pipe.to("cpu")
    prompt = "make a mini short haired golden doodle with a touch of irish setter mix dog, masterpiece, photograph" # Your prompt here
    neg_prompt = "(worst quality, naked, low quality, illustration, 3d, 2d, painting, sketch)" # Negative prompt here
    image = pipe(prompt=prompt, negative_prompt=neg_prompt,width=800,height=600,num_inference_steps=50).images[0]
    image