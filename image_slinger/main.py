from flask import Flask, request, jsonify
from image_slinger.image_generator import generate_image, load_model, unload_model
from image_slinger.status import check_cuda_status
import io
import base64
from threading import Lock

generate_image_lock = Lock()

default_model = "dataautogpt3/OpenDalleV1.1"

app = Flask(__name__)
app.global_model = None
app.global_safety_model = None
app.global_safety_processor = None

@app.route('/status', methods=['GET'])
def status():
    return jsonify(check_cuda_status(app))

#@app.route('/unload-model', methods=['DELETE'])
#def unload_model_endpoint():
#    unload_model(app)
#    return jsonify({"message": "Model unloaded successfully"})

#@app.route('/load-model', methods=['POST'])
#def load_model_endpoint():
#    data = request.json
#    model_name = data.get('model_name', default_model)
#    load_model(app, model_name)
#    return jsonify({"message": f"Model '{model_name}' loaded successfully"})

@app.route('/generate-image', methods=['POST'])
def generate_image_endpoint():
    data = request.json
    model = data.get('model',default_model)
    prompt = data.get('prompt')
    negative_prompt = data.get('negative_prompt', '')
    width = data.get('width', 512)  # default values if not specified
    height = data.get('height', 512)
    image_type = data.get('image_type', 'png').lower() # png or jepg
    num_inference_steps = data.get('num_inference_steps', 50)
    safety = data.get('safety',True)
    autoclean = data.get('autoclean',True)

    try:
        with generate_image_lock:
            image, safety_classification = generate_image(app, model, prompt, negative_prompt, width, height, num_inference_steps, safety, autoclean)
        # Assuming image is a PIL image, convert it to bytes
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
