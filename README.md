# Azure Event Grid MQTT Client with JWT Authentication

This project provides a Python client for connecting to Azure Event Grid using MQTT protocol with JWT (JSON Web Token) authentication.

## Features

- Connect to Azure Event Grid using MQTT v5 protocol
- JWT-based authentication with RSA256 signing
- Publish and subscribe to MQTT topics
- Comprehensive logging and error handling
- TLS/SSL secure connection
- Event publishing with CloudEvents format support

## Prerequisites

1. **Azure Event Grid Namespace**: You need an Azure Event Grid namespace with MQTT support enabled
2. **OAuth 2.0 JWT Authentication**: Configure JWT authentication on your Event Grid namespace
3. **RSA Key Pair**: Generate an RSA key pair for JWT signing
4. **Python 3.7+**: Ensure you have Python 3.7 or higher installed

## Setup

### 1. Create and Activate Virtual Environment

**Option A: Using the setup script (Recommended)**
```bash
# Make the setup script executable and run it
chmod +x setup_venv.sh
./setup_venv.sh
```

**Option B: Manual setup**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 2. Activate Virtual Environment (for future sessions)

```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Deactivate Virtual Environment (when done)

```bash
deactivate
```

### 4. Azure Event Grid Configuration

1. Create an Event Grid namespace in the Azure portal
2. Enable MQTT support on the namespace
3. Configure OAuth 2.0 JWT authentication:
   - Upload your public key certificate to Azure Key Vault
   - Grant the Event Grid namespace access to validate client tokens
4. Create a topic space within the namespace

### 5. Generate RSA Key Pair

Generate an RSA key pair for JWT signing:

```bash
# Generate private key
openssl genrsa -out private_key.pem 2048

# Generate public key
openssl rsa -in private_key.pem -pubout -out public_key.pem
```

Upload the public key to Azure Key Vault and configure it in your Event Grid namespace.

### 6. Configure the Client

Update the configuration variables in `event_grid_mqtt_client.py`:

```python
# Configuration - Replace with your actual values
NAMESPACE = "your-namespace"
REGION = "eastus"
CLIENT_ID = "python-mqtt-client"
USERNAME = "your-username"

# Load your private key
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----"""
```

## Usage

### Basic Usage

```python
from event_grid_mqtt_client import EventGridMQTTClient

# Initialize client
client = EventGridMQTTClient(
    namespace="your-namespace",
    region="eastus",
    client_id="your-client-id",
    private_key="your-private-key",
    username="your-username"
)

# Connect to broker
if client.connect():
    # Subscribe to a topic
    client.subscribe_to_topic("devices/device1/messages/events")
    
    # Publish an event
    event_data = {
        "id": "event-001",
        "source": "python-client",
        "specversion": "1.0",
        "type": "com.example.sample",
        "data": {
            "message": "Hello from Python!",
            "temperature": 23.5
        }
    }
    client.publish_event("devices/device1/messages/events", event_data)
    
    # Disconnect when done
    client.disconnect()
```

### Running the Example (Python)

```bash
source venv/bin/activate
python event_grid_mqtt_client.py
```

## TypeScript/Node.js Client

### Setup

```bash
npm install
npm run dev

# Or build + run
npm run build
npm start
```

### Configure

Update `src/main.ts` with your values:

```ts
const NAMESPACE = '<your-namespace>';
const REGION = 'eastus';
const CLIENT_ID = '<client-id>';     // Must match Event Grid Client resource name
const USERNAME  = '<auth-name>';     // Must match Authentication Name
```

Place your private key in `private_key.pem` (PEM, RSA 2048+).

The client uses MQTT v5 Enhanced Auth with:
- authenticationMethod: `CUSTOM-JWT`
- authenticationData: JWT signed with RS256
- `aud` claim: `<namespace>.<region>-1.ts.eventgrid.azure.net/`

## Configuration Details

### JWT Token Claims

The JWT token includes the following claims:

- `aud`: Audience claim set to `{namespace}.{region}-1.ts.eventgrid.azure.net/`
- `iat`: Issued at timestamp
- `exp`: Expiration timestamp (default: 1 hour)
- `iss`: Issuer (client ID)
- `sub`: Subject (client ID)

### MQTT Connection Details

- **Protocol**: MQTT v5
- **Port**: 8883 (TLS/SSL)
- **Authentication**: Custom JWT in password field
- **TLS**: Enabled with default context

### Topic Structure

Topics follow the pattern: `{topic_space}/{client_id}/messages/events`

Example: `devices/python-mqtt-client/messages/events`

## Error Handling

The client includes comprehensive error handling for:

- Connection failures
- JWT token generation errors
- Message publishing failures
- Subscription errors
- Network timeouts

All errors are logged with appropriate detail levels.

## Security Considerations

1. **Private Key Security**: Keep your private key secure and never commit it to version control
2. **Token Expiration**: JWT tokens expire after 1 hour by default
3. **TLS Connection**: All connections use TLS/SSL encryption
4. **Certificate Validation**: Consider enabling proper certificate validation in production

## Troubleshooting

### Quick Diagnosis

Run the troubleshooting script to diagnose common issues:

```bash
# Activate virtual environment first
source venv/bin/activate

# Run troubleshooting script
python troubleshoot.py
```

### Common Issues

#### 1. **"Not authorized" Error (Code 5/135)**

This is the most common error. Check these items in order:

**JWT Token Issues:**
- ✅ JWT audience must be: `{namespace}.{region}-1.ts.eventgrid.azure.net/` (note trailing slash)
- ✅ JWT issuer and subject should match your client ID
- ✅ JWT token must not be expired
- ✅ Private key must be in correct PEM format

**Azure Configuration:**
- ✅ Public key must be uploaded to Azure Key Vault
- ✅ Event Grid namespace must have access to the Key Vault
- ✅ OAuth 2.0 JWT authentication must be enabled on the namespace
- ✅ MQTT must be enabled on the namespace

**Client Configuration:**
- ✅ Client ID must be ≤ 23 characters (MQTT limit)
- ✅ Namespace and region names must be exact (case-sensitive)
- ✅ Username must be provided

#### 2. **Connection Failed (Code 3)**

- Check if MQTT is enabled on the Event Grid namespace
- Verify namespace and region names are correct
- Check network connectivity and firewall settings (port 8883)

#### 3. **Topic Access Denied**

- Verify topic space configuration in Azure portal
- Check client permissions and topic space access policies
- Ensure topic naming follows the expected pattern

### Debug Logging

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Step-by-Step Debugging

1. **Run the troubleshooting script:**
   ```bash
   python troubleshoot.py
   ```

2. **Check the enhanced error messages** in the main script - they now provide specific guidance for authorization errors

3. **Verify JWT token details** - the script now logs the complete JWT payload for debugging

4. **Test with minimal configuration** - start with the basic example and gradually add complexity

### Azure Portal Checklist

When setting up Azure Event Grid:

- [ ] Event Grid namespace created
- [ ] MQTT enabled on the namespace
- [ ] OAuth 2.0 JWT authentication enabled
- [ ] Public key uploaded to Azure Key Vault
- [ ] Event Grid namespace has access to Key Vault
- [ ] Topic space created (if using custom topics)
- [ ] Client permissions configured in topic space

## License

This project is provided as-is for educational and development purposes.

## Contributing

Feel free to submit issues and enhancement requests!
