type RepeaterConfig = {
  interval: number; // milliseconds
  limit: number;
};

type RepeatResult<T> = {
  result: T | null | undefined;
  count: number;
};

export class Repeater {
  private readonly interval: number;
  private readonly limit: number;
  private count = 0;

  constructor({ interval, limit }: RepeaterConfig) {
    this.interval = interval;
    this.limit = limit;
  }

  // Repeatedly execute a function until it returns something or until the repetition limit is reached
  async repeat<T>(func: (count: number) => Promise<T>): Promise<RepeatResult<T>> {
    await new Promise((resolve) => setTimeout(resolve, this.interval)); // delay
    const result = await func(++this.count);
    if (result) return { result, count: this.count };
    if (this.count <= this.limit) return this.repeat(func);
    return { result: null, count: this.count };
  }
}
