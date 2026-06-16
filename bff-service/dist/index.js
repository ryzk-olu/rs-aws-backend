"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const fastify_1 = __importDefault(require("fastify"));
const dotenv = __importStar(require("dotenv"));
const http = __importStar(require("http"));
const https = __importStar(require("https"));
dotenv.config();
const app = (0, fastify_1.default)({ logger: true });
const PORT = process.env.PORT || 3000;
const SERVICES = {
    product: process.env.PRODUCT_SERVICE_URL || '',
    cart: process.env.CART_SERVICE_URL || '',
};
app.all('/:service/*', async (request, reply) => {
    const { service } = request.params;
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
                    if (value)
                        reply.header(key, value);
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
