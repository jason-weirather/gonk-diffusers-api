from diffusers import StableDiffusionXLPipeline, DDIMScheduler
from diffusers.pipelines.stable_diffusion import StableDiffusionSafetyChecker
from transformers import pipeline, AutoModelForImageClassification, ViTImageProcessor
from .status import check_cuda_status
from PIL import Image, ImageFilter
import torch
import gc

safety_model = 'Falconsai/nsfw_image_detection'
min_blur_size = 15
blur_fraction = 0.05

def load_model(app, model_name: str):
    print(f"Entering load_model for {model_name}")
    # Check if a different model is already loaded
    if hasattr(app, 'global_model') and \
       app.global_model is not None and \
       app.global_model.config._name_or_path != model_name:
        print("A model already exists that needs to be unloaded. Unloading:")
        unload_model(app)

    print(f"Proceeding to load_model for {model_name}")
    # Load the model if it's not already loaded
    if not hasattr(app, 'global_model') or app.global_model is None:
        print("Setting global model in StableDiffusionXLPipeline")
        app.global_model = StableDiffusionXLPipeline.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16"
        )
        print(f"Loaded model in function with model {app.global_model.config._name_or_path}")
        app.global_model.to("cuda")
        print(f"{type(app.global_model)}")

    # Lets load our safety model
    if not hasattr(app, 'global_safety_model') or app.global_safety_model is None:
        app.global_safety_model = AutoModelForImageClassification.from_pretrained(safety_model)
    if not hasattr(app, 'global_safety_processor') or app.global_safety_processor is None:
        app.global_safety_processor = ViTImageProcessor.from_pretrained(safety_model)

def unload_model(app):
    if hasattr(app, 'global_model') and app.global_model is not None:
        del app.global_model
        del app.global_safety_model
        del app.global_safety_processor
        torch.cuda.empty_cache()
        app.global_model = None
        app.global_safety_model = None
        app.global_safety_processor = None
        gc.collect()

def generate_image(app, model, prompt, negative_prompt, width, height, num_inference_steps, safety, autoclean):
    # See if our model is loaded
    status = check_cuda_status(app)
    print(status)
    if not hasattr(app,'global_model') or '_name_or_path' not in status['model_info'] or status['model_info']['_name_or_path'] != model:
        # Load model at runtime if we need to
        print('model has not been loaded')
        load_model(app,model)


    # Generate the image using the model
    # Note: Adjust the following line according to your model's API
    results = app.global_model(prompt=prompt, negative_prompt=negative_prompt,
                                       width=width, height=height,
                                       num_inference_steps=num_inference_steps)


    generated_image = results.images[0]

    #safety_model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection")
    #processor = ViTImageProcessor.from_pretrained('Falconsai/nsfw_image_detection')
    with torch.no_grad():
        inputs = app.global_safety_processor(images=generated_image, return_tensors="pt")
        outputs = app.global_safety_model(**inputs)
        logits = outputs.logits

    print(logits)
    predicted_label = logits.argmax(-1).item()
    print("second level")
    print(app.global_safety_model.config.id2label[predicted_label])

    safety_label = app.global_safety_model.config.id2label[predicted_label]
    blur_size = max(min_blur_size,5+int(max(height,width)*blur_fraction))
    if autoclean:
        unload_model(app)
    if 'nsfw' == safety_label:
        # Apply blur if NSFW
        if safety:
            blurred_image = generated_image.filter(ImageFilter.GaussianBlur(radius=blur_size))
            return blurred_image, 'nsfw'
        else:
            return generated_image, 'nsfw'
    else:
        return generated_image, 'normal'

    print(type(generated_image))
    return generated_image, safety_label
