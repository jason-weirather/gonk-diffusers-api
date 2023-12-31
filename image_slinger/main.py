from flask import Flask, request, jsonify
from image_slinger.image_generator import generate_image, load_model, unload_model
from image_slinger.status import check_cuda_status
import io
import base64
from threading import Lock

# Initialize the lock for synchronizing image generation requests
generate_image_lock = Lock()

# Default model to be used if not specified in the request
default_model = "dataautogpt3/OpenDalleV1.1"

# Initialize Flask application
app = Flask(__name__)

# Routes
@app.route('/status', methods=['GET'])
def status():
    """Endpoint to get the current status of the server."""
    return jsonify(check_cuda_status(app))

@app.route('/generate-image', methods=['POST'])
def generate_image_endpoint():
    """Endpoint to generate an image based on the provided parameters."""
    data = request.json
    model = data.get('model', default_model)
    prompt = data.get('prompt')
    negative_prompt = data.get('negative_prompt', '')
    width = data.get('width', 512)  # Default width if not specified
    height = data.get('height', 512)  # Default height if not specified
    image_type = data.get('image_type', 'png').lower()  # Default to PNG if not specified
    num_inference_steps = data.get('num_inference_steps', 50)
    safety = data.get('safety', True)

    try:
        with generate_image_lock:
            image, safety_classification = generate_image(app, model, prompt, negative_prompt, width, height, num_inference_steps, safety)
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        if image_type == 'jpeg' or image_type == 'jpg':
            image.save(img_byte_arr, format='JPEG')
            mimetype = 'image/jpeg'
        elif image_type == 'png':
            image.save(img_byte_arr, format='PNG')
            mimetype = 'image/png'
        else:
            raise ValueError(f"Unknown image type {image_type}")
        encoded_img = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        return jsonify({
            "image": encoded_img,
            "safety_classification": safety_classification,
            "mime_type": mimetype
        })
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
