from flask import Flask, request, jsonify, send_from_directory, abort
from image_slinger.image_generator import generate_image, load_model, unload_model
from image_slinger.status import check_cuda_status
import io
import base64
import os
from threading import Lock
from flask_swagger_ui import get_swaggerui_blueprint

# Default model to be used if not specified in the request
default_model = "dataautogpt3/OpenDalleV1.1"

# Initialize the lock and Flask app
generate_image_lock = Lock()
app = Flask(__name__)

# Function to correctly determine the directory of the static files
def get_static_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'static')

app.static_folder = get_static_dir()

# Swagger UI configuration
SWAGGER_URL = '/docs'
API_URL = '/static/openapi.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Image Slinger API"},
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.before_request
def authenticate():
    excluded_paths = ['/docs','/static']
    if not any(request.path.startswith(path) for path in excluded_paths):
        if app.config.get('REQUIRE_AUTH', False):
            api_key = request.headers.get('Authorization')
            if not api_key or api_key != app.config['API_KEY']:
                abort(401, description="Unauthorized: API key required")

@app.route('/static/<path:path>')
def send_static(path):
    """Custom static file server."""
    return send_from_directory(app.static_folder, path)

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
    num_inference_steps = data.get('num_inference_steps', 40)
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
