import json
import os

import boto3

from core.ai_ops.base import AIWorker


class AWSBedrockT2TWorker(AIWorker):
    """Text-to-text worker over AWS Bedrock (Anthropic Claude message format).

    `model_id` is per-instance, not baked into the class — that's what lets
    AIWorkerRegistry hand back a different model on request (see
    ai_ops/registry.py) without needing a new worker class per model."""

    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        self.client = None
        super().__init__()

    def initialize(self):
        if not self.client:
            self.client = boto3.client(
                "bedrock-runtime",
                region_name=os.getenv("AWS_DEFAULT_REGION"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            )

    def test_connection(self) -> bool:
        try:
            self.initialize()
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 5,
                    "temperature": 0,
                    "messages": [{"role": "user", "content": [{"type": "text", "text": "ping"}]}],
                }),
                contentType="application/json",
                accept="application/json",
            )
            return response["ResponseMetadata"]["HTTPStatusCode"] == 200
        except Exception:
            return False

    def invoke(self, prompt: str, max_tokens: int = 2000) -> dict:
        self.initialize()
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": 0,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        }
        response = self.client.invoke_model(modelId=self.model_id, body=json.dumps(payload))
        body = json.loads(response["body"].read().decode("utf-8"))
        return {
            "text": body["content"][0]["text"],
            "usage": body.get("usage", {}),
            "raw": body,
        }
