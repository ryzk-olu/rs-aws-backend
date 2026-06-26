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

let productCache: { data: string; timestamp: number } | null = null;
const CACHE_TTL = 2 * 60 * 1000;

app.all('/:service/*', async (request, reply) => {
  const { service } = request.params as { service: string };
  const recipientURL = SERVICES[service];

  if (!recipientURL) {
    return reply.status(502).send({ message: 'Cannot process request' });
  }

  const path = request.url.replace(`/${service}`, '');
  const targetUrl = `${recipientURL}${path}`;

  const isProductsList = service === 'product' &&
    path.startsWith('/products') &&
    request.method === 'GET';

  if (isProductsList && productCache) {
    const age = Date.now() - productCache.timestamp;
    if (age < CACHE_TTL) {
      reply.header('X-Cache', 'HIT');
      return reply.status(200).send(productCache.data);
    }
  }

  return new Promise((resolve) => {
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
        if (isProductsList && proxyRes.statusCode === 200) {
          productCache = { data, timestamp: Date.now() };
        }
        reply.status(proxyRes.statusCode || 200);
        Object.entries(proxyRes.headers).forEach(([key, value]) => {
          if (value) reply.header(key, value as string);
        });
        reply.header('X-Cache', 'MISS');
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
