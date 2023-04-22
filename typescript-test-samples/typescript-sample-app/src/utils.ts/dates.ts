import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc';

dayjs.extend(utc);

export const shortTimestamp = (date?: Date) => dayjs.utc(date).format('mm:ss.SSS');