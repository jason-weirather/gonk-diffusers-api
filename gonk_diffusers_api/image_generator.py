from diffusers import StableDiffusionXLPipeline
from transformers import AutoModelForImageClassification, ViTImageProcessor
from PIL import ImageFilter
import torch
import gc
import os

# Constants for safety model and image processing
safety_model = 'Falconsai/nsfw_image_detection'
min_blur_size = 15
blur_fraction = 0.05

def load_model(app, model_name: str):
    """Load the specified model into the application context."""
    # Check if a different model is already loaded and needs to be unloaded
    if hasattr(app, 'global_model') and app.global_model is not None and app.global_model.config._name_or_path != model_name:
        unload_model(app)

    # Load the primary model
    app.global_model = StableDiffusionXLPipeline.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16",
        local_files_only = True if os.environ['HF_LOCAL_FILES_ONLY'] == "YES" else False,
        cache_dir = None if 'HF_CACHE_PATH' not in os.environ else os.environ['HF_CACHE_PATH']
    )
    app.global_model.to("cuda")

    # Load the safety model and processor
    app.global_safety_model = AutoModelForImageClassification.from_pretrained(
        safety_model,
        local_files_only = True if os.environ['HF_LOCAL_FILES_ONLY'] == "YES" else False,
        cache_dir = None if 'HF_CACHE_PATH' not in os.environ else os.environ['HF_CACHE_PATH']
    )
    app.global_safety_processor = ViTImageProcessor.from_pretrained(
        safety_model,
        local_files_only = True if os.environ['HF_LOCAL_FILES_ONLY'] == "YES" else False,
        cache_dir = None if 'HF_CACHE_PATH' not in os.environ else os.environ['HF_CACHE_PATH']
    )

def unload_model(app):
    """Unload models from the application context and clear CUDA cache."""
    del app.global_model
    del app.global_safety_model
    del app.global_safety_processor
    torch.cuda.empty_cache()
    app.global_model = None
    app.global_safety_model = None
    app.global_safety_processor = None
    gc.collect()

def generate_image(app, model, prompt, negative_prompt, width, height, num_inference_steps, safety):
    """Generate an image using the specified parameters and model."""
    # Load model
    load_model(app, model)

    # Generate the image
    results = app.global_model(prompt=prompt, negative_prompt=negative_prompt, width=width, height=height, num_inference_steps=num_inference_steps)
    generated_image = results.images[0]

    # Process image for safety
    with torch.no_grad():
        inputs = app.global_safety_processor(images=generated_image, return_tensors="pt")
        outputs = app.global_safety_model(**inputs)
        logits = outputs.logits
        predicted_label = logits.argmax(-1).item()
        safety_label = app.global_safety_model.config.id2label[predicted_label]

    # Unload models
    unload_model(app)

    # Apply blur if image is NSFW
    blur_size = max(min_blur_size, int(max(height, width) * blur_fraction))
    if 'nsfw' == safety_label and safety:
        blurred_image = generated_image.filter(ImageFilter.GaussianBlur(radius=blur_size))
        return blurred_image, safety_label
    else:
        return generated_image, safety_label
