import base64
import requests

IMAGE = r"C:\Users\riswa\product-classification-ai\test_shoe.jpg"

with open(IMAGE, "rb") as f:
    image = base64.b64encode(f.read()).decode("utf-8")

payload = {
    "model": "Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What is this product? Reply with only one short phrase."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image}"
                    }
                }
            ]
        }
    ],
    "temperature": 0,
    "max_tokens": 20
}

print("Sending image test...")

response = requests.post(
    "http://127.0.0.1:8080/v1/chat/completions",
    json=payload,
    timeout=180
)

print("Status:", response.status_code)
print(response.text)