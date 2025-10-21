import os
import requests

class GeminiImageDescriber:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key must be provided via argument or GEMINI_API_KEY env variable.")
        # Updated endpoint as per official documentation
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    def describe_image(self, image_path, prompt="Describe this image."):
        with open(image_path, "rb") as img_file:
            img_bytes = img_file.read()
        # Determine mime type based on file extension
        ext = os.path.splitext(image_path)[1].lower()
        if ext == ".png":
            mime_type = "image/png"
        else:
            mime_type = "image/jpeg"
        img_b64 = self._to_base64(img_bytes)
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": img_b64
                            }
                        }
                    ]
                }
            ]
        }
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        response = requests.post(self.api_url, json=data, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        # Defensive: check for candidates and structure
        try:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise RuntimeError(f"Unexpected API response: {result}")

    @staticmethod
    def _to_base64(binary_data):
        import base64
        return base64.b64encode(binary_data).decode("utf-8")

# Example usage:
# describer = GeminiImageDescriber()
# description = describer.describe_image("samples/test.jpg", prompt="Describe the game card in detail.")
# print(description)
