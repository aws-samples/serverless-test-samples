using Amazon.CDK;
using Amazon.CDK.AwsBedrock;
using Cdklabs.GenerativeAiCdkConstructs.Bedrock;
using Constructs;

namespace ChatbotDemo.Infrastructure.Stacks
{
    public class BedrockGuardrailStack : Stack
    {
        internal BedrockGuardrailStack(Construct scope, string id, IStackProps props = null) : base(scope, id, props)
        {
            var guardrails = new Guardrail(this, "bedrockGuardrail", new GuardrailProps
            {
                Name = "mm-guardrails",
                Description = "Legal ethical guardrails"
            });

            guardrails.AddSensitiveInformationPolicyConfig(new ISensitiveInformationPolicyConfigProps[]
            {
                new SensitiveInformationPolicyConfigProps
                {
                    Type = General.EMAIL,
                    Action = PiiEntitiesConfigAction.BLOCK,
                },
                new SensitiveInformationPolicyConfigProps
                {
                    Type = InformationTechnology.IP_ADDRESS,
                    Action = PiiEntitiesConfigAction.BLOCK
                }
            }, new CfnGuardrail.RegexConfigProperty
            {
                Name = "CUSTOMER_ID",
                Description = "Customer Id",
                Pattern = "/^[A-Z]{2}\\d{6}$/",
                Action = "BLOCK",
            });

            var topicPolicy = new Topic(this, "mmTopic");
            topicPolicy.FinancialAdviceTopic();
            topicPolicy.PoliticalAdviceTopic();
            
            guardrails.AddTopicPolicyConfig(topicPolicy);

            _ = new CfnOutput(this, "guardrailVersion", new CfnOutputProps
            {
                Value = guardrails.GuardrailVersion,
                Description = "Guardrail Version"
            });
            _ = new CfnOutput(this, "guardrailId", new CfnOutputProps
            {
                Value = guardrails.GuardrailId,
                Description = "Guardrail Id"
            });
        }
    }
}