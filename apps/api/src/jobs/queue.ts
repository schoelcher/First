import { Queue, Worker } from "bullmq";
import IORedis from "ioredis";
import { env } from "../lib/env";
import { MultiChannelNotificationProvider } from "../adapters/notificationProvider";

const connection = new IORedis(env.redisUrl, { maxRetriesPerRequest: null });
export const reminderQueue = new Queue("reminders", { connection });

new Worker(
  "reminders",
  async (job) => {
    const notifier = new MultiChannelNotificationProvider();
    await notifier.sendLeaveReminder(job.data);
  },
  { connection }
);
