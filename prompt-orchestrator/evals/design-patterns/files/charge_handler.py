import json
import boto3

cache = {}

def handler(event, context):
    payments = boto3.client("payments-api")
    for record in event["Records"]:
        body = json.loads(record["body"])
        cache[body["customer_id"]] = body["card"]
        payments.charge(amount=body["amount"], card=body["card"])
    return {"ok": True}
