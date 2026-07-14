import { Injectable, OnModuleDestroy, OnModuleInit } from '@nestjs/common';
import { ConfirmChannel, ChannelModel, connect } from 'amqplib';
import { OutboxStatus } from '@prisma/client';
import { PrismaService } from '../database/prisma.service';

@Injectable()
export class OutboxPublisherService implements OnModuleInit, OnModuleDestroy {
  private connection?: ChannelModel;
  private channel?: ConfirmChannel;
  private timer?: NodeJS.Timeout;
  private polling = false;
  private readonly exchange = process.env.RABBITMQ_EXCHANGE ?? 'hr.events';

  constructor(private readonly prisma: PrismaService) {}

  onModuleInit() {
    if (process.env.OUTBOX_PUBLISHER_ENABLED === 'false') return;
    this.timer = setInterval(() => void this.poll(), Number(process.env.OUTBOX_POLL_INTERVAL_MS ?? 2_000));
    void this.poll();
  }

  async onModuleDestroy() {
    if (this.timer) clearInterval(this.timer);
    await this.channel?.close().catch(() => undefined);
    await this.connection?.close().catch(() => undefined);
  }

  private async poll() {
    if (this.polling) return;
    this.polling = true;
    try {
      const channel = await this.getChannel();
      const events = await this.prisma.outboxEvent.findMany({
        where: { status: OutboxStatus.PENDING, attempts: { lt: 10 } },
        orderBy: { createdAt: 'asc' },
        take: 20
      });
      for (const event of events) {
        try {
          const routingKey = `hr.${event.aggregateType.toLowerCase()}.${event.eventType.toLowerCase()}`;
          channel.publish(this.exchange, routingKey, Buffer.from(JSON.stringify(event.payload)), {
            persistent: true,
            contentType: 'application/json',
            messageId: event.id,
            correlationId: event.correlationId,
            type: event.eventType,
            timestamp: event.createdAt.getTime()
          });
          await channel.waitForConfirms();
          await this.prisma.outboxEvent.update({ where: { id: event.id }, data: { status: OutboxStatus.PUBLISHED, publishedAt: new Date() } });
        } catch (error: unknown) {
          await this.prisma.outboxEvent.update({
            where: { id: event.id },
            data: { attempts: { increment: 1 }, status: event.attempts + 1 >= 10 ? OutboxStatus.FAILED : OutboxStatus.PENDING }
          });
          this.log('error', 'outbox.publish.failed', { eventId: event.id, error: error instanceof Error ? error.message : 'unknown error' });
        }
      }
    } catch (error: unknown) {
      this.channel = undefined;
      this.connection = undefined;
      this.log('warn', 'outbox.poll.failed', { error: error instanceof Error ? error.message : 'unknown error' });
    } finally {
      this.polling = false;
    }
  }

  private async getChannel() {
    if (this.channel) return this.channel;
    this.connection = await connect(process.env.RABBITMQ_URL ?? 'amqp://ertis:ertis_dev@localhost:5673');
    this.channel = await this.connection.createConfirmChannel();
    await this.channel.assertExchange(this.exchange, 'topic', { durable: true });
    this.connection.on('close', () => {
      this.connection = undefined;
      this.channel = undefined;
    });
    return this.channel;
  }

  private log(level: string, event: string, details: Record<string, unknown>) {
    process.stdout.write(`${JSON.stringify({ level, event, ...details })}\n`);
  }
}
