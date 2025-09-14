# lambda_classifier.py
"""
Lambda function: S3-triggered classifier that processes session logs with Claude (via Bedrock),
classifies content, and stores structured result in DynamoDB.
"""

import json
import os
import logging
from typing import Any, Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# === Environment Variables ===
S3_BUCKET = os.environ.get("LOG_BUCKET")
DDB_TABLE = os.environ.get("DDB_TABLE")
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-v2")
REGION = os.environ.get("AWS_REGION", "us-east-1")

# === AWS Clients ===
s3_client = boto3.client("s3")
ddb_client = boto3.client("dynamodb")
bedrock_client = boto3.client("bedrock-runtime", region_name=REGION)


# === Lambda Handler ===
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        logger.info(f"Triggered by file: s3://{bucket}/{key}")

        log_content = get_s3_object(bucket, key)
        structured = classify_session(log_content)
        store_result(structured)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Classification stored."}),
        }
    except Exception as e:
        logger.exception("Handler failed")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


# === Helper: Fetch Log ===
def get_s3_object(bucket: str, key: str) -> str:
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read().decode("utf-8")
    except ClientError as e:
        logger.error(f"Failed to get S3 object: {e}")
        raise


# === Helper: Claude Classification ===
def classify_session(session_text: str) -> Dict[str, Any]:
    prompt = build_prompt(session_text)
    try:
        response = bedrock_client.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({"prompt": prompt, "max_tokens_to_sample": 1024}),
        )
        body = json.loads(response["body"].read())
        completion = body.get("completion")
        if not completion:
            raise ValueError("Claude response missing 'completion'")
        return json.loads(completion)
    except (BotoCoreError, ClientError, json.JSONDecodeError, ValueError) as e:
        logger.error(f"Claude call failed: {e}")
        raise


# === Helper: Prompt Construction ===
def build_prompt(session_text: str) -> str:
    return (
        "System:\n"
        "You are Ariadne, a context agent that classifies logs and produces structured output.\n\n"
        "User:\n"
        f"Messages:\n{session_text}\n\n"
        "Return strict JSON with fields: aha_moments, mvp_changes, scope_creep, readme_notes, "
        "post_mvp_ideas, summary, quality_flags."
    )


# === Helper: Store Result ===
def store_result(data: Dict[str, Any]) -> None:
    try:
        session_id = data.get("session_id")
        timestamp = data.get("timestamp")
        if not session_id or not timestamp:
            raise ValueError("Missing session_id or timestamp in result")
        item = {
            "session_id": {"S": session_id},
            "timestamp": {"S": timestamp},
            "payload": {"S": json.dumps(data)},
        }
        ddb_client.put_item(TableName=DDB_TABLE, Item=item)
    except (ClientError, ValueError) as e:
        logger.error(f"DynamoDB put_item failed: {e}")
        raise
