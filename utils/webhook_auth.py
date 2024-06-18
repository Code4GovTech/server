import hmac,hashlib,json

#FUNCTION TO VERIFY SECRET TOKEN
async def verify_github_webhook(request, secret_key):
    signature = request.headers.get('X-Hub-Signature-256')

    if signature is None:
        return False, "Signature header missing."

    try:
        # Extracting the JSON payload directly from the Quart request object
        payload = await request.get_json()

        if payload is None:
            return False, "No JSON payload found in the request."

        # Convert the payload to a JSON string
        payload_string = json.dumps(payload, separators=(',', ':'))

        # Generate the expected signature using HMAC with SHA-256
        expected_signature = "sha256=" + hmac.new(secret_key.encode(), payload_string.encode('utf-8'), hashlib.sha256).hexdigest()

        # Compare the expected signature with the received signature
        if hmac.compare_digest(expected_signature, signature):
            return True, None
        else:
            return False, "Signatures do not match."
    except Exception as e:
        return False, f"Error verifying GitHub webhook signature: {e}"