import mqtt, { IClientOptions, MqttClient, IConnackPacket } from 'mqtt';
import * as fs from 'fs';

export interface PublishEvent {
  [key: string]: unknown;
}

export interface EventGridMqttClientOptions {
  namespace: string;
  region: string;
  clientId: string;
  username: string;
  clientCertFile: string;
  clientKeyFile: string;
  caCertFile?: string;
  clientKeyPassword?: string;
  topicSpace?: string;
}

export class EventGridMqttClient {
  private readonly namespace: string;
  private readonly region: string;
  private readonly clientId: string;
  private readonly username: string;
  private readonly clientCertFile: string;
  private readonly clientKeyFile: string;
  private client: MqttClient | null = null;
  private connected = false;

  constructor(opts: EventGridMqttClientOptions) {
    this.namespace = opts.namespace;
    this.region = opts.region;
    this.clientId = opts.clientId;
    this.username = opts.username;
    this.clientCertFile = opts.clientCertFile;
    this.clientKeyFile = opts.clientKeyFile;

    this.validateConfiguration();
  }

  private validateConfiguration(): void {
    if (!this.namespace) throw new Error('Namespace is required');
    if (!this.region) throw new Error('Region is required');
    if (!this.clientId) throw new Error('Client ID is required');
    if (!this.username) throw new Error('Username is required');
    if (!this.clientCertFile) throw new Error('Client certificate file is required');
    if (!this.clientKeyFile) throw new Error('Client private key file is required');

    if (this.clientId.length > 23) {
      throw new Error(`Client ID '${this.clientId}' is ${this.clientId.length} characters long. MQTT client ID must be ≤ 23 characters.`);
    }
    const invalidChars = new Set(
      [...this.clientId].filter(c => !/^[a-zA-Z0-9-_]$/.test(c))
    );
    if (invalidChars.size > 0) {
      throw new Error(`Client ID '${this.clientId}' contains invalid characters: ${[...invalidChars].join('')}`);
    }

    // Validate certificate files exist
    if (!fs.existsSync(this.clientCertFile)) {
      throw new Error(`Client certificate file not found: ${this.clientCertFile}`);
    }
    if (!fs.existsSync(this.clientKeyFile)) {
      throw new Error(`Client key file not found: ${this.clientKeyFile}`);
    }
  }

  async connect(): Promise<boolean> {
    const url = `mqtts://${this.namespace}.${this.region}-1.ts.eventgrid.azure.net:8883`;

    // Read certificate files
    const cert = fs.readFileSync(this.clientCertFile);
    const key = fs.readFileSync(this.clientKeyFile);

    const options: IClientOptions = {
      clientId: this.clientId,
      protocolVersion: 5,
      username: this.username,
      clean: true,
      // TLS options for client certificate authentication
      cert: cert,
      key: key
    };
    console.log('cert\n', options.cert?.toString());
    console.log('key\n', options.key?.toString());

    this.client = mqtt.connect(url, options);

    this.client.on('connect', (packet: IConnackPacket) => {
      const code = packet.reasonCode ?? 0;
      if (code === 0) {
        this.connected = true;
        console.log(`Connected to ${url}`);
      } else {
        console.error(`Connect failed code=${code}`);
      }
    });

    this.client.on('error', (err) => {
      console.error('MQTT error:', err.message);
    });

    this.client.on('close', () => {
      this.connected = false;
      console.warn('Connection closed');
    });

    this.client.on('disconnect', (packet) => {
      const code = packet?.reasonCode;
      console.warn(`Disconnected (reasonCode: ${code})`);
    });

    this.client.on('message', (topic, payload) => {
      try {
        const text = payload.toString('utf8');
        console.log(`Message on ${topic}: ${text}`);
      } catch (e) {
        console.log(`Message on ${topic} (binary)`);
      }
    });

    // Wait up to 10s for connect
    const start = Date.now();
    while (!this.connected && Date.now() - start < 10_000) {
      await new Promise((r) => setTimeout(r, 100));
    }

    return this.connected;
  }

  disconnect(): void {
    if (!this.client) return;
    this.client.end(true, {}, () => {
      console.log('Disconnected from broker');
    });
  }

  async subscribe(topic: string, qos: 0 | 1 | 2 = 1): Promise<boolean> {
    if (!this.client || !this.connected) {
      console.error('Not connected');
      return false;
    }
    return new Promise<boolean>((resolve) => {
      this.client!.subscribe(topic, { qos }, (err, granted) => {
        if (err) {
          console.error('Subscribe error:', err.message);
          resolve(false);
        } else {
          console.log(`Subscribed: ${JSON.stringify(granted)}`);
          resolve(true);
        }
      });
    });
  }

  async publish(topic: string, event: PublishEvent, qos: 0 | 1 | 2 = 1): Promise<boolean> {
    if (!this.client || !this.connected) {
      console.error('Not connected');
      return false;
    }
    const payload = JSON.stringify(event);
    return new Promise<boolean>((resolve) => {
      this.client!.publish(topic, payload, { qos }, (err) => {
        if (err) {
          console.error('Publish error:', err.message);
          resolve(false);
        } else {
          console.log(`Published to ${topic}`);
          resolve(true);
        }
      });
    });
  }
}
