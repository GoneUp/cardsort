sudo apt install -y python3-libcamera python3-kms++ libcap-dev
pip3 install fastapi uvicorn requests websockets pydantic --break-system-packages

uv run uvicorn web_api:app --host 0.0.0.0 --port 8000

