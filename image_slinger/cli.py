import argparse
from image_slinger.main import app

def start_server(host, port):
    app.run(host=host, port=port)

def main():
    parser = argparse.ArgumentParser(description="Start the Image Slinger Flask server.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-H", "--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port to run the server")

    args = parser.parse_args()
    start_server(args.host, args.port)

if __name__ == "__main__":
    main()
