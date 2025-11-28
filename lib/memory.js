import { Redis } from "@upstash/redis";

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_URL,
  token: process.env.UPSTASH_REDIS_TOKEN,
});

export async function getMemory(userId) {
  return await redis.get(`memory:${userId}`);
}

export async function saveMemory(userId, data) {
  return await redis.set(`memory:${userId}`, data);
}
