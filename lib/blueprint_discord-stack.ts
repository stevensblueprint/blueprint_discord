import * as cdk from "aws-cdk-lib/core";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigwv2 from "aws-cdk-lib/aws-apigatewayv2";
import * as integrations from "aws-cdk-lib/aws-apigatewayv2-integrations";
import * as s3 from "aws-cdk-lib/aws-s3";
import { Construct } from "constructs";
import * as path from 'path';

export interface BlueprintDiscordStackProps extends cdk.StackProps {
  discordAppId: string;
  discordPublicKey: string;
  discordGuildId: string;
  discordBotToken: string;
}

export class BlueprintDiscordStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: BlueprintDiscordStackProps) {
    super(scope, id, props);

    const s3SummaryBucket = new s3.Bucket(this, "SummaryBucket", {
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      lifecycleRules: [
        {
          prefix: "envfiles/",
          expiration: cdk.Duration.days(365),
        },
      ],
    });
    const fn = new lambda.Function(this, "DiscordInteractionHandler", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "main.handler",
      code: lambda.Code.fromAsset("lambda", {
        bundling: {
          image: lambda.Runtime.PYTHON_3_11.bundlingImage,
          user: 'root',
          platform: "linux/amd64",
          command: [
            "bash",
            "-lc",
            [
              "pip install -r requirements.txt -t /asset-output",
              "cp -au . /asset-output",
            ].join(" && "),
          ],
        },
      }),
      timeout: cdk.Duration.seconds(29),
      environment: {
        DISCORD_APP_ID: props.discordAppId,
        DISCORD_PUBLIC_KEY: props.discordPublicKey,
        DISCORD_GUILD_ID: props.discordGuildId,
        DISCORD_BOT_TOKEN: props.discordBotToken,
        SUMMARY_BUCKET_NAME: s3SummaryBucket.bucketName,
      },
    });

    s3SummaryBucket.grantReadWrite(fn);

    const httpApi = new apigwv2.HttpApi(this, "DiscordApi", {
      apiName: "discord-slash-bot",
    });

    httpApi.addRoutes({
      path: "/interactions",
      methods: [apigwv2.HttpMethod.POST],
      integration: new integrations.HttpLambdaIntegration(
        "LambdaIntegration",
        fn,
      ),
    });

    new cdk.CfnOutput(this, "ApiEndpoint", {
      value: httpApi.apiEndpoint,
    });
  }
}

export default BlueprintDiscordStack;
