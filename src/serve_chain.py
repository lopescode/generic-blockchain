import argparse
from app_factory import create_app

def main():
    parser = argparse.ArgumentParser(description='Run blockchain Flask node.')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the node on.')
    args = parser.parse_args()

    app = create_app()
    app.run(host='0.0.0.0', port=args.port)

if __name__ == '__main__':
    main()