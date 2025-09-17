#!/usr/bin/env python3
"""
Azure Event Grid MQTT Client with JWT Authentication

This script demonstrates how to connect to Azure Event Grid using MQTT protocol
with JWT (JSON Web Token) authentication.
"""

import paho.mqtt.client as mqtt
import time
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import ssl
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EventGridMQTTClient:
    """
    Azure Event Grid MQTT Client using TLS client certificates (mTLS)
    """
    
    def __init__(self, 
                 namespace: str,
                 region: str,
                 client_id: str,
                 username: str,
                 client_cert_file: str,
                 client_key_file: str,
                 ca_cert_file: Optional[str] = None,
                 client_key_password: Optional[str] = None,
                 topic_space: str = "default"):
        """
        Initialize the Event Grid MQTT client
        
        Args:
            namespace: Azure Event Grid namespace name
            region: Azure region (e.g., 'eastus', 'westus2')
            client_id: Unique client identifier
            private_key: RSA private key for JWT signing
            username: Username for MQTT connection
            topic_space: Topic space name (default: 'default')
        """
        self.namespace = namespace
        self.region = region
        self.client_id = client_id
        self.username = username
        self.topic_space = topic_space
        self.client_cert_file = client_cert_file
        self.client_key_file = client_key_file
        self.ca_cert_file = ca_cert_file
        self.client_key_password = client_key_password
        
        # Construct the broker URL
        self.broker_url = f"{namespace}.{region}-1.ts.eventgrid.azure.net"
        self.port = 8883
        
        # Initialize MQTT client
        self.client = mqtt.Client(
            client_id=client_id,
            protocol=mqtt.MQTTv5
        )
        
        # Set up event handlers
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish
        self.client.on_subscribe = self._on_subscribe
        
        # Connection state
        self.connected = False
        
        # Validate configuration
        self._validate_configuration()
    
    def _validate_configuration(self):
        """Validate the client configuration"""
        logger.info("🔍 Validating configuration...")
        
        # Check required fields
        if not self.namespace:
            raise ValueError("Namespace is required")
        if not self.region:
            raise ValueError("Region is required")
        if not self.client_id:
            raise ValueError("Client ID is required")
        if not self.username:
            raise ValueError("Username is required")
        if not self.client_cert_file:
            raise ValueError("Client certificate file is required")
        if not self.client_key_file:
            raise ValueError("Client private key file is required")
        
        # Validate client ID (MQTT requirements)
        if len(self.client_id) > 23:
            raise ValueError(f"Client ID '{self.client_id}' is {len(self.client_id)} characters long. MQTT client ID must be ≤ 23 characters.")
        
        # Check for invalid characters in client ID
        invalid_chars = set(self.client_id) - set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        if invalid_chars:
            raise ValueError(f"Client ID '{self.client_id}' contains invalid characters: {invalid_chars}. Only alphanumeric, hyphens, and underscores are allowed.")
        
        # Validate certificate files
        if not os.path.isfile(self.client_cert_file):
            raise ValueError(f"Client certificate file not found: {self.client_cert_file}")
        if not os.path.isfile(self.client_key_file):
            raise ValueError(f"Client key file not found: {self.client_key_file}")
        if self.ca_cert_file and not os.path.isfile(self.ca_cert_file):
            raise ValueError(f"CA certificate file not found: {self.ca_cert_file}")
        
        # Validate namespace and region format
        if " " in self.namespace:
            logger.warning("⚠️  Namespace contains spaces - this may cause issues")
        
        # Log configuration (without sensitive data)
        logger.info(f"✅ Namespace: {self.namespace}")
        logger.info(f"✅ Region: {self.region}")
        logger.info(f"✅ Client ID: {self.client_id} (length: {len(self.client_id)})")
        logger.info(f"✅ Username: {self.username}")
        logger.info(f"✅ Broker URL: {self.broker_url}")
        logger.info(f"✅ Topic Space: {self.topic_space}")
        
        logger.info("✅ Configuration validation completed")
    
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """Handle MQTT connection events"""
        # Handle both MQTT v3.1.1 (integer) and MQTT v5 (ReasonCodes) return codes
        if hasattr(rc, 'value'):
            # MQTT v5 - rc is a ReasonCodes object
            rc_value = rc.value
            rc_name = rc.name if hasattr(rc, 'name') else str(rc)
        else:
            # MQTT v3.1.1 - rc is an integer
            rc_value = rc
            rc_name = str(rc)
        
        if rc_value == 0:
            self.connected = True
            logger.info(f"Successfully connected to {self.broker_url}")
        else:
            self.connected = False
            # Enhanced error reporting for common connection issues
            logger.error(f"Connection failed with code {rc_value} ({rc_name})")
      
    
    def _on_disconnect(self, client, userdata, rc, properties=None):
        """Handle MQTT disconnection events"""
        self.connected = False
        
        # Handle both MQTT v3.1.1 (integer) and MQTT v5 (ReasonCodes) return codes
        if hasattr(rc, 'value'):
            rc_value = rc.value
            rc_name = rc.name if hasattr(rc, 'name') else str(rc)
        else:
            rc_value = rc
            rc_name = str(rc)
        
        if rc_value != 0:
            logger.warning(f"Unexpected disconnection (code: {rc_value} - {rc_name})")
        else:
            logger.info("Disconnected from broker")
    
    def _on_message(self, client, userdata, message):
        """Handle incoming MQTT messages"""
        try:
            payload = message.payload.decode('utf-8')
            logger.info(f"Received message on topic '{message.topic}': {payload}")
            
            # Try to parse as JSON
            try:
                data = json.loads(payload)
                logger.info(f"Parsed JSON data: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                logger.info("Message is not valid JSON")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _on_publish(self, client, userdata, mid):
        """Handle message publish events"""
        logger.info(f"Message published successfully (mid: {mid})")
    
    def _on_subscribe(self, client, userdata, mid, reason_codes, properties=None):
        """Handle subscription events"""
        # Handle both MQTT v3.1.1 and v5 subscription responses
        if isinstance(reason_codes, list):
            # MQTT v3.1.1 - reason_codes is a list of integers
            for i, reason_code in enumerate(reason_codes):
                logger.info(f"Subscribed (mid: {mid}, reason: {reason_code})")
        else:
            # MQTT v5 - reason_codes is a list of ReasonCodes objects
            for i, reason_code in enumerate(reason_codes):
                if hasattr(reason_code, 'value'):
                    rc_value = reason_code.value
                    rc_name = reason_code.name if hasattr(reason_code, 'name') else str(reason_code)
                else:
                    rc_value = reason_code
                    rc_name = str(reason_code)
                
                logger.info(f"Subscribed (mid: {mid}), reason: {rc_value} - {rc_name}")
    
    def connect(self) -> bool:
        """
        Connect to Azure Event Grid MQTT broker
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Set username if required
            if self.username:
                self.client.username_pw_set(username=self.username)

            # Configure TLS with client certificate (mTLS)
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            if self.ca_cert_file:
                context.load_verify_locations(cafile=self.ca_cert_file)
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_cert_chain(
                certfile=self.client_cert_file,
                keyfile=self.client_key_file,
                password=self.client_key_password
            )
            self.client.tls_set_context(context)
            
            # Connect to broker
            logger.info(f"Connecting to {self.broker_url}:{self.port}")
            result = self.client.connect(self.broker_url, self.port, keepalive=60)
            
            if result == 0:
                # Start the network loop
                self.client.loop_start()
                
                # Wait for connection
                timeout = 10
                start_time = time.time()
                while not self.connected and (time.time() - start_time) < timeout:
                    time.sleep(0.1)
                
                return self.connected
            else:
                logger.error(f"Failed to initiate connection (result: {result})")
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the MQTT broker"""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from broker")
    
    def publish_event(self, topic: str, event_data: Dict[str, Any]) -> bool:
        """
        Publish an event to a topic
        
        Args:
            topic: MQTT topic to publish to
            event_data: Event data to publish
            
        Returns:
            True if publish successful, False otherwise
        """
        if not self.connected:
            logger.error("Not connected to broker")
            return False
        
        try:
            # Convert event data to JSON
            payload = json.dumps(event_data, default=str)
            
            # Publish message
            result = self.client.publish(topic, payload, qos=1)
            
            if result.rc == 0:
                logger.info(f"Event published to topic '{topic}'")
                return True
            else:
                logger.error(f"Failed to publish event (rc: {result.rc})")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False
    
    def subscribe_to_topic(self, topic: str) -> bool:
        """
        Subscribe to a topic
        
        Args:
            topic: MQTT topic to subscribe to
            
        Returns:
            True if subscription successful, False otherwise
        """
        if not self.connected:
            logger.error("Not connected to broker")
            return False
        
        try:
            result = self.client.subscribe(topic, qos=1)
            
            if result[0] == 0:
                logger.info(f"Subscribed to topic '{topic}'")
                return True
            else:
                logger.error(f"Failed to subscribe to topic '{topic}' (rc: {result[0]})")
                return False
                
        except Exception as e:
            logger.error(f"Error subscribing to topic: {e}")
            return False


def main():
    """
    Example usage of the Event Grid MQTT client
    """
    # Configuration - Replace with your actual values
    NAMESPACE = "kwasniewski-event-grid-test"
    REGION = "eastus"
    CLIENT_ID = "client1"  # Must match Event Grid MQTT client name
    USERNAME = "client1"   # Must match Authentication Name if configured

    # mTLS certificate files (PEM)
    CLIENT_CERT_FILE = "public_key.pem"     # Client certificate (public)
    CLIENT_KEY_FILE = "private_key.pem"     # Client private key

    # Create client
    client = EventGridMQTTClient(
        namespace=NAMESPACE,
        region=REGION,
        client_id=CLIENT_ID,
        username=USERNAME,
        client_cert_file=CLIENT_CERT_FILE,
        client_key_file=CLIENT_KEY_FILE,
    )
    
    try:
        # Connect to broker
        if client.connect():
            logger.info("Connected successfully!")
            
            # Subscribe to a topic
            topic = f"tcu/{CLIENT_ID}/reservation/update"
            if client.subscribe_to_topic(topic):
                logger.info(f"Subscribed to {topic}")
            
            # Subscribe to a topic
            topic = f"tcu/client2/reservation/update"
            if client.subscribe_to_topic(topic):
                logger.info(f"Subscribed to {topic}, this should fail")

            # Publish a sample event
            sample_event = {
                "id": "sample-event-001",
                "source": "tcu",
                "specversion": "1.0",
                "type": "motion-detected",
                "time": datetime.now(timezone.utc).isoformat() + "Z",
                "data": {
                    "message": "New event",
                    "camera_id": "camera1",
                    "motion_detected": True,
                    "temperature": 23.5,
                    "humidity": 65.2,
                    "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
                }
            }
            
            publish_topic = "tcu/camera/report"
            if client.publish_event(publish_topic, sample_event):
                logger.info("Sample event published successfully!")
            
            # Keep the connection alive for a while to receive messages
            logger.info("Keeping connection alive for 30 seconds...")
            time.sleep(30)
        else:
            logger.error("Failed to connect to broker")
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
