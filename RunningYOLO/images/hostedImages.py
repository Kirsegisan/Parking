# import the inference-sdk
from inference_sdk import InferenceHTTPClient

# initialize the client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="kmdwHagZQlYas7gzGfw9"
)

# infer on a local image
result = CLIENT.infer("images/03.jpg", model_id="parking-utku6/4")

