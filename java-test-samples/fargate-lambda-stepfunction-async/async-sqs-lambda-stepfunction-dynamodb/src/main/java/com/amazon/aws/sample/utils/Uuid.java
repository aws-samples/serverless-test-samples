package com.amazon.aws.sample.utils;

import java.util.UUID;

public class Uuid {
    public static String generateUuid() {
        return UUID.randomUUID().toString();
    }
}
