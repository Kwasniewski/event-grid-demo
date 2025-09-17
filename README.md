# Azure Event Grid MQTT Client with Cert Authentication
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
