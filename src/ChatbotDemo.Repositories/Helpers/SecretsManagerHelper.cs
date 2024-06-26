using Amazon;
using Amazon.SecretsManager;
using Amazon.SecretsManager.Model;

namespace ChatbotDemo.Repositories.Helpers;

public static class SecretsManagerHelper
{
    public static async Task<string> GetSecretValue(string secretName)
    {
        var client = new AmazonSecretsManagerClient(RegionEndpoint.USWest2);

        var request = new GetSecretValueRequest
        {
            SecretId = secretName,
            VersionStage = "AWSCURRENT"
        };

        var response = await client.GetSecretValueAsync(request);
        return response.SecretString;
    }
}