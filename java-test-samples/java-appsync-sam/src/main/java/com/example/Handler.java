package com.example;

import software.amazon.awssdk.services.appsync.AppSyncClient;


public class Handler {
    private final AppSyncClient appSyncClient;

    public Handler() {
        appSyncClient = DependencyFactory.appSyncClient();
    }

    public void sendRequest() {
        // TODO: invoking the api calls using appSyncClient.
    }
}
