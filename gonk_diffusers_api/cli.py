import os
import argparse
from image_slinger.main import app

def start_server(host, port, require_auth, hf_local_files_only, hf_cache_path=None):
    if require_auth:
        app.config['REQUIRE_AUTH'] = True
        app.config['API_KEY'] = os.environ.get('IMAGE_SLINGER_API_KEY')

    # Set Hugging Face cache directory if specified
    if hf_cache_path:
        os.environ['HF_CACHE_PATH'] = hf_cache_path

    if hf_local_files_only:
        os.environ['HF_LOCAL_FILES_ONLY'] = "YES"
    else:
        os.environ['HF_LOCAL_FILES_ONLY'] = "NO"

    app.run(host=host, port=port)

def main():
    parser = argparse.ArgumentParser(description="Start the Image Slinger Flask server.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-H", "--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port to run the server")
    parser.add_argument("--require-auth", action='store_true', help="Enable API key authentication")
    parser.add_argument("--hf-cache-path", type=str, help="Path to the Huggingface cache directory")
    parser.add_argument("--hf-local-files-only", action='store_true', help="Only use locally cached models")

    args = parser.parse_args()
    start_server(args.host, args.port, args.require_auth, args.hf_local_files_only, args.hf_cache_path)

if __name__ == "__main__":
    main()
