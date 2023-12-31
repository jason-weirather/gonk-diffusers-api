import os
import argparse
from image_slinger.main import app

def start_server(host, port, require_auth):
    if require_auth:
        app.config['REQUIRE_AUTH'] = True
        app.config['API_KEY'] = os.environ.get('IMAGE_SLINGER_API_KEY')
    app.run(host=host, port=port)

def main():
    parser = argparse.ArgumentParser(description="Start the Image Slinger Flask server.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-H", "--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port to run the server")
    parser.add_argument("--require-auth", action='store_true', help="Enable API key authentication")

    args = parser.parse_args()
    start_server(args.host, args.port, args.require_auth)

if __name__ == "__main__":
    main()
