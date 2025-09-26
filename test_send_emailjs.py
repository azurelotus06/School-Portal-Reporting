import subprocess
import json

# Fill these with your actual EmailJS values
SERVICE_ID = "service_l9fh0pj"
TEMPLATE_ID = "template_rerp7v6"
PUBLIC_KEY = "ta5OfAVP6Jqpb5VCc"
RECIPIENT_EMAIL = ["davidgundaker3@gmail.com"]

# Template variables as required by your EmailJS template
template_vars = {
    "name": "Noah Cooksey",
    "email": "davidgundaker3@gmail.com"
}

args = [
    "node",
    "send_email.js",
    SERVICE_ID,
    TEMPLATE_ID,
    PUBLIC_KEY,
    json.dumps(template_vars),
]

try:
    result = subprocess.run(args, capture_output=True, text=True, check=True)
    print("Node.js script output:")
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print("Node.js script failed:")
    print(e.stderr)
