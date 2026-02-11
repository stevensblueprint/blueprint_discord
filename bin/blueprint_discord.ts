#!/usr/bin/env node
import * as cdk from "aws-cdk-lib/core";
import { BlueprintDiscordStack } from "../lib/blueprint_discord-stack";

const app = new cdk.App();
new BlueprintDiscordStack(app, "blueprint-discord-stack", {
  env: {
    region: process.env.CDK_DEFAULT_REGION,
    account: process.env.CDK_DEFAULT_ACCOUNT,
  },
  discordPublicKey: process.env.DISCORD_PUBLIC_KEY || "",
});
