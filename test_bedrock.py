import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION"))

body = {
    "messages": [{"role": "user", "content": "Hello, classify this text"}],
    "max_tokens": 1000,
    "anthropic_version": "bedrock-2023-05-31",
}

resp = bedrock.invoke_model(
    modelId=os.getenv("BEDROCK_MODEL_ID"),
    body=json.dumps(body),
    contentType="application/json",
)

print("✅ Bedrock works!", resp["body"].read())
