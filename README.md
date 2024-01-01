# gonk-diffusers-api

gonk-diffusers-api allows you to hostan API server to transforms text prompts into vivid images using machine learning models compatible with Huggingface's Stable Diffusion diffusers library. It's specifically optimized for CUDA-enabled GPUs on a small scale hardware where memory conservation and 1-by-1 processing of incoming requests is desiarable.

#### Example request in a Jupyter notebook
```python
import requests
import base64
from IPython.display import Image, display

url = 'http://localhost:8000/generate-image'
data = {
    'model': 'dataautogpt3/OpenDalleV1.1',
    'prompt': 'Aerial view of a futuristic cityscape getting tip-toed on by a giant kitten acting like godzilla',
    'negative_prompt': "(worst quality, low quality, simpsons hands)",
    'width': 1024,
    'height': 1024,
    'image_type': 'png',
    'num_inference_steps': 40,
    'safety': True
}
response = requests.post(url, json=data)
response_data = response.json()

# Check the response and display the image
if response.status_code == 200 and 'image' in response_data:
    encoded_image = response_data['image']
    mime_type = response_data['mime_type']
    
    # Decode the Base64 string to bytes
    image_bytes = base64.b64decode(encoded_image)
    
    # Display the image
    display(Image(data=image_bytes, format=mime_type.split('/')[-1], embed=True))
else:
    print("Failed to generate image:", response.text)
```
<img src="https://i.imgur.com/BEjjkQ5.png" width="300" height="300" alt="Example image">

## Features
- **Stable Diffusion Compatibility**: Utilizes models compatible with Stable Diffusion for high-quality image generation.
- **CUDA GPU Acceleration**: Optimized for use with CUDA-compatible NVIDIA GPUs.
- **On-by-default Safety**: Leverages the [Falconsai/nsfw_image_detection](https://huggingface.co/Falconsai/nsfw_image_detection) model to blur images that do not pass the safety filter.
- **Concurrency Control**: Manages multiple simultaneous requests with built-in concurrency control.
- **Interactive Swagger Documentation**: Includes Swagger UI for easy interaction with the API.

## System Requirements
- **CUDA-Compatible GPU**: Requires an NVIDIA GPU with CUDA support.
- **Python 3.8+**: Recommended to use the latest version of Python.
- **Dependencies**: Listed in the `requirements.txt` file.

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/jason-weirather/gonk-diffusers-api.git
   ```
2. **Navigate to the Project Directory**:
   ```bash
   cd gonk-diffusers-api
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
### Starting the Server
Start the server using the CLI:
```bash
python -m gonk-diffusers-api.cli
```
Optional CLI arguments:
- `-H`, `--host`: Host address (default `0.0.0.0`).
- `-p`, `--port`: Port number (default `8000`).
- `--require-auth`: Enable API key authentication.

### API Endpoints
- **POST `/generate-image`**: Generates an image from a given text prompt.
- **GET `/status`**: Retrieves the server and CUDA status.



### Authentication
To enable API authentication, set the `GONK_DIFFUSERS_API_KEY` environment variable and start the server with the `--require-auth` flag.

### API Documentation
Access the interactive API documentation by navigating to `http://localhost:8000/docs`.

## License
This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
