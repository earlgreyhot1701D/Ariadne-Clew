import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION"))

resp = bedrock.invoke_model(
    modelId=os.getenv("BEDROCK_MODEL_ID"),
    body=json.dumps({"inputText": "Hello, classify this text"}),
    contentType="application/json"
)

print("✅ Bedrock works!", resp['body'].read())
