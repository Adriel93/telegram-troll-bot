// lib/memory.js
import { Redis } from "@upstash/redis";

export const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN,
});

export async function saveUser(id, data) {
  await redis.set(`user:${id}`, JSON.stringify(data));
}

export async function getUser(id) {
  const raw = await redis.get(`user:${id}`);
  return raw ? JSON.parse(raw) : null;
}
