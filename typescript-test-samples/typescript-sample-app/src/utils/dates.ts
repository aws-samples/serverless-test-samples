import dayjs from 'dayjs'
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import utc from 'dayjs/plugin/utc';

dayjs.extend(utc);

export const shortTimestamp = (date?: Date) => dayjs.utc(date).format('mm:ss:SSS [m:s:ms]');