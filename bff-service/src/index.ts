import Fastify from 'fastify';
import * as dotenv from 'dotenv';
import * as http from 'http';
import * as https from 'https';

dotenv.config();

const app = Fastify({ logger: true });
const PORT = process.env.PORT || 3000;

const SERVICES: Record<string, string> = {
  product: process.env.PRODUCT_SERVICE_URL || '',
  cart: process.env.CART_SERVICE_URL || '',
};

app.all('/:service/*', async (request, reply) => {
  const { service } = request.params as { service: string };
  const recipientURL = SERVICES[service];

  if (!recipientURL) {
    return reply.status(502).send({ message: 'Cannot process request' });
  }

  const path = request.url.replace(`/${service}`, '');
  const targetUrl = `${recipientURL}${path}`;

  return new Promise((resolve, reject) => {
    const url = new URL(targetUrl);
    const lib = url.protocol === 'https:' ? https : http;
    const options = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method: request.method,
      headers: {
        ...request.headers,
        host: url.hostname,
      },
    };

    const proxyReq = lib.request(options, (proxyRes) => {
      let data = '';
      proxyRes.on('data', (chunk) => (data += chunk));
      proxyRes.on('end', () => {
        reply.status(proxyRes.statusCode || 200);
        Object.entries(proxyRes.headers).forEach(([key, value]) => {
          if (value) reply.header(key, value as string);
        });
        reply.send(data);
        resolve(null);
      });
    });

    proxyReq.on('error', (err) => {
      reply.status(502).send({ message: err.message });
      resolve(null);
    });

    if (request.body) {
      proxyReq.write(JSON.stringify(request.body));
    }
    proxyReq.end();
  });
});

app.listen({ port: Number(PORT), host: '0.0.0.0' }, (err) => {
  if (err) {
    app.log.error(err);
    process.exit(1);
  }
});
