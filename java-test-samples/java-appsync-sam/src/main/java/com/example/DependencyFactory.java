
package com.example;

import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.appsync.AppSyncClient;

/**
 * The module containing all dependencies required by the {@link Handler}.
 */
public class DependencyFactory {

    private DependencyFactory() {}

    /**
     * @return an instance of AppSyncClient
     */
    public static AppSyncClient appSyncClient() {
        return AppSyncClient.builder()
                       .httpClientBuilder(ApacheHttpClient.builder())
                       .build();
    }
}
