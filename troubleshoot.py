#!/usr/bin/env python3
"""
Azure Event Grid MQTT Troubleshooting Script

This script helps diagnose common issues with Azure Event Grid MQTT connections.
"""

import jwt
import json
import time
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_jwt_token(namespace: str, region: str, client_id: str, private_key: str):
    """
    Validate JWT token generation and format
    """
    logger.info("🔍 Validating JWT token...")
    
    try:
        # Generate JWT token
        now = datetime.utcnow()
        audience = f"{namespace}.{region}-1.ts.eventgrid.azure.net/"
        
        payload = {
            "aud": audience,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
            "iss": client_id,
            "sub": client_id
        }
        
        logger.info(f"JWT Payload: {json.dumps(payload, indent=2)}")
        
        # Generate token with headers
        headers = {
            "typ": "JWT",
            "alg": "RS256"
        }
        token = jwt.encode(payload, private_key, algorithm="RS256", headers=headers)
        logger.info("✅ JWT token generated successfully")
        
        # Decode and verify
        decoded = jwt.decode(token, options={"verify_signature": False})
        logger.info(f"Decoded JWT: {json.dumps(decoded, indent=2)}")
        
        # Decode and show header
        import base64
        import json as json_lib
        header_part = token.split('.')[0]
        # Add padding if needed
        header_part += '=' * (4 - len(header_part) % 4)
        header_decoded = base64.urlsafe_b64decode(header_part)
        header_json = json_lib.loads(header_decoded)
        logger.info(f"JWT Header: {json.dumps(header_json, indent=2)}")
        
        # Check token format
        parts = token.split('.')
        if len(parts) != 3:
            logger.error("❌ JWT token doesn't have 3 parts")
            return False
        
        logger.info("✅ JWT token format is correct")
        return True
        
    except Exception as e:
        logger.error(f"❌ JWT validation failed: {e}")
        return False


def validate_private_key(private_key: str):
    """
    Validate private key format
    """
    logger.info("🔍 Validating private key...")
    
    if not private_key:
        logger.error("❌ Private key is empty")
        return False
    
    if not private_key.strip().startswith("-----BEGIN"):
        logger.error("❌ Private key doesn't start with '-----BEGIN'")
        return False
    
    if not private_key.strip().endswith("-----END"):
        logger.error("❌ Private key doesn't end with '-----END'")
        return False
    
    if "PRIVATE KEY" not in private_key:
        logger.error("❌ Private key doesn't contain 'PRIVATE KEY'")
        return False
    
    logger.info("✅ Private key format appears correct")
    return True


def validate_configuration(namespace: str, region: str, client_id: str, username: str):
    """
    Validate basic configuration parameters
    """
    logger.info("🔍 Validating configuration...")
    
    issues = []
    
    if not namespace:
        issues.append("Namespace is empty")
    elif " " in namespace:
        issues.append("Namespace contains spaces")
    
    if not region:
        issues.append("Region is empty")
    elif " " in region:
        issues.append("Region contains spaces")
    
    if not client_id:
        issues.append("Client ID is empty")
    elif len(client_id) > 23:
        issues.append(f"Client ID is {len(client_id)} characters long (MQTT limit is 23)")
    else:
        # Check for invalid characters in client ID
        invalid_chars = set(client_id) - set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        if invalid_chars:
            issues.append(f"Client ID contains invalid characters: {invalid_chars}")
    
    if not username:
        issues.append("Username is empty")
    
    if issues:
        for issue in issues:
            logger.error(f"❌ {issue}")
        return False
    
    logger.info("✅ Configuration validation passed")
    logger.info(f"✅ Client ID: '{client_id}' (length: {len(client_id)})")
    return True


def print_troubleshooting_tips():
    """
    Print common troubleshooting tips
    """
    logger.info("\n🔧 TROUBLESHOOTING TIPS:")
    logger.info("=" * 50)
    
    logger.info("\n1. 🔐 JWT Authentication Issues:")
    logger.info("   - Ensure your public key is uploaded to Azure Key Vault")
    logger.info("   - Verify Event Grid namespace has access to the Key Vault")
    logger.info("   - Check that OAuth 2.0 JWT authentication is enabled")
    logger.info("   - Verify JWT audience matches: {namespace}.{region}-1.ts.eventgrid.azure.net/")
    
    logger.info("\n2. 🏗️ Azure Configuration:")
    logger.info("   - Ensure MQTT is enabled on your Event Grid namespace")
    logger.info("   - Verify the namespace and region names are correct")
    logger.info("   - Check that the namespace is in a supported region")
    
    logger.info("\n3. 🔑 Key Management:")
    logger.info("   - Use RSA 2048-bit or higher keys")
    logger.info("   - Ensure private key is in PEM format")
    logger.info("   - Verify the public key matches the private key")
    
    logger.info("\n4. 🌐 Network Issues:")
    logger.info("   - Check firewall settings (port 8883)")
    logger.info("   - Verify DNS resolution for the broker URL")
    logger.info("   - Test network connectivity to Azure")
    
    logger.info("\n5. 📝 Common Mistakes:")
    logger.info("   - Wrong audience in JWT (missing trailing slash)")
    logger.info("   - Client ID too long (>23 characters)")
    logger.info("   - Expired JWT token")
    logger.info("   - Incorrect namespace/region combination")


def main():
    """
    Main troubleshooting function
    """
    logger.info("🚀 Azure Event Grid MQTT Troubleshooting Tool")
    logger.info("=" * 50)
    
    # Example configuration - replace with your actual values
    NAMESPACE = "your-namespace"
    REGION = "eastus"
    CLIENT_ID = "python-mqtt-client"
    USERNAME = "your-username"
    
    # Example private key - replace with your actual private key
    PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----"""
    
    logger.info("⚠️  IMPORTANT: Update the configuration variables in this script with your actual values!")
    logger.info("")
    
    # Run validations
    config_valid = validate_configuration(NAMESPACE, REGION, CLIENT_ID, USERNAME)
    key_valid = validate_private_key(PRIVATE_KEY)
    
    if config_valid and key_valid:
        jwt_valid = validate_jwt_token(NAMESPACE, REGION, CLIENT_ID, PRIVATE_KEY)
    else:
        jwt_valid = False
    
    # Print results
    logger.info("\n📊 VALIDATION RESULTS:")
    logger.info("=" * 30)
    logger.info(f"Configuration: {'✅ PASS' if config_valid else '❌ FAIL'}")
    logger.info(f"Private Key:   {'✅ PASS' if key_valid else '❌ FAIL'}")
    logger.info(f"JWT Token:     {'✅ PASS' if jwt_valid else '❌ FAIL'}")
    
    if not all([config_valid, key_valid, jwt_valid]):
        print_troubleshooting_tips()
    else:
        logger.info("\n✅ All validations passed! Your configuration looks good.")
        logger.info("If you're still having connection issues, check the Azure portal configuration.")


if __name__ == "__main__":
    main()
