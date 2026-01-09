import json

def handler(event, context):
    print("[print_lambda] Hello! This should appear in CloudWatch Logs.")
    print("[print_lambda] event:", json.dumps(event)[:2000])
    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": json.dumps({"ok": True, "message": "printed to CloudWatch"})
    }
