import { EventGridMqttClient } from './eventGridMqttClient.js';

async function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  // Replace with your actual values
  const NAMESPACE = 'kwasniewski-event-grid-test';
  const REGION = 'eastus';
  const CLIENT_ID = 'admin1'; // Must match the Client resource name in Event Grid
  const USERNAME = 'admin1'; // Must match Authentication Name in Event Grid

  // mTLS certificate files (PEM)
  const CLIENT_CERT_FILE = 'admin_public_key.pem';     // Client certificate (public)
  const CLIENT_KEY_FILE = 'admin_private_key.pem';     // Client private key

  const client = new EventGridMqttClient({
    namespace: NAMESPACE,
    region: REGION,
    clientId: CLIENT_ID,
    username: USERNAME,
    clientCertFile: CLIENT_CERT_FILE,
    clientKeyFile: CLIENT_KEY_FILE
  });

  try {
    const ok = await client.connect();
    if (!ok) {
      console.error('Failed to connect');
      process.exit(1);
    }

    const topic = `tcu/camera/report`;
    await client.subscribe(topic, 1);

    // Wait for 5 seconds
    await sleep(5000);

    const event = {
      id: 'ts-sample-001',
      source: 'ts-client',
      specversion: '1.0',
      type: 'com.example.sample',
      time: new Date().toISOString(),
      data: { message: 'Hello from TypeScript MQTT client!', temperature: 22.7 }
    };

    await client.publish('tcu/client1/reservation/update', event, 1);
    await client.publish('tcu/client2/reservation/update', event, 1);

    console.log('Keeping connection alive for 30 seconds...');
    await new Promise((r) => setTimeout(r, 30_000));
  } catch (err) {
    console.error('Unexpected error:', (err as Error).message);
  } finally {
    client.disconnect();
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});


