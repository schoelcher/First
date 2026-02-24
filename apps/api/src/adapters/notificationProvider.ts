import nodemailer from "nodemailer";
import { NotificationProvider } from "../lib/contracts";
import { env } from "../lib/env";
import { prisma } from "../lib/prisma";

export class MultiChannelNotificationProvider implements NotificationProvider {
  private transporter = nodemailer.createTransport({
    host: env.smtpHost,
    port: env.smtpPort,
    secure: false,
    auth: env.smtpUser ? { user: env.smtpUser, pass: env.smtpPass } : undefined
  });

  async sendLeaveReminder(input: { userId: string; eventId: string; urgent: boolean; title: string; body: string }): Promise<void> {
    const user = await prisma.user.findUniqueOrThrow({ where: { id: input.userId } });
    try {
      await this.transporter.sendMail({ from: env.smtpFrom, to: user.email, subject: input.title, text: input.body });
      await prisma.notificationLog.create({ data: { userId: input.userId, eventId: input.eventId, channel: "email", payload: input.body } });
    } catch {
      await prisma.notificationLog.create({ data: { userId: input.userId, eventId: input.eventId, channel: "push-fallback", payload: JSON.stringify(input) } });
    }
  }
}
