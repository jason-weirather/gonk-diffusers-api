import os
import argparse
from gonk_diffusers_api.main import app

def str_to_bool(value):
    """Converts a string to a boolean."""
    return value.lower() in ('true', '1', 't', 'y', 'yes')

def start_server(host, port, require_auth, hf_local_files_only, hf_cache_path=None):
    if require_auth:
        app.config['REQUIRE_AUTH'] = True
        app.config['API_KEY'] = os.environ.get('GONK_DIFFUSERS_API_KEY')

    # Set Hugging Face cache directory if specified
    if hf_cache_path:
        os.environ['HF_CACHE_PATH'] = hf_cache_path

    if hf_local_files_only:
        os.environ['HF_LOCAL_FILES_ONLY'] = "YES"
    else:
        os.environ['HF_LOCAL_FILES_ONLY'] = "NO"


    # Check if USE_GUNICORN environment variable is set to 'true'
    use_gunicorn = str_to_bool(os.environ.get('USE_GUNICORN', 'false'))

    if use_gunicorn:
        from gunicorn.app.base import BaseApplication

        class FlaskApplication(BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                config = {key: value for key, value in self.options.items()
                          if key in self.cfg.settings and value is not None}
                for key, value in config.items():
                    self.cfg.set(key.lower(), value)

            def load(self):
                return self.application
        options = {
            'bind': f'{host}:{port}',
            'workers': 1,  # Adjust as needed
            'timeout': 240
        }
        FlaskApplication(app, options).run()
    else:
        app.run(host=host, port=port)

def main():
    parser = argparse.ArgumentParser(description="Start the gonk-diffusers-api Flask server.",
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
