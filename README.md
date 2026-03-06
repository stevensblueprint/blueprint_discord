# Blueprint Discord Bot

A Discord slash command bot built with AWS CDK, API Gateway, and Lambda (Python).

## Setup

1. Create a Discord application at https://discord.com/developers/applications
2. Copy your credentials into a `.env` file:

```
APP_ID=your_app_id
PUBLIC_KEY=your_public_key
GUILD_ID=your_guild_id      # optional: omit for global commands
BOT_TOKEN=your_bot_token
```

3. Install dependencies:

```bash
npm install
```

## Deploy

```bash
npx cdk deploy
```

Copy the `ApiEndpoint` output URL and set it as your app's **Interactions Endpoint URL** in the Discord Developer Portal (Settings → General Information).

## Register slash commands

```bash
npm run register
```

Run this after every deploy and whenever you add or remove commands. If `GUILD_ID` is set, commands are registered to that guild (instant). Otherwise they are registered globally (can take up to 1 hour to propagate).

## Commands

### `/env store file:<attachment> passphrase:<string>`

Encrypts a `.env` file with the given passphrase and stores it in S3. The bot replies ephemerally (visible only to you) with a UUID key you'll use to retrieve the file later.

The UUID key is valid for **24 hours** after upload. The underlying file is retained in S3 for **1 year**.

### `/env get name:<uuid> passphrase:<string>`

Fetches the stored file by its UUID key, decrypts it with the passphrase, and replies ephemerally with the file contents.

- Wrong passphrase → `"Invalid passphrase or corrupted file."`
- Key not found or expired → `"File not found."`

## Adding a new command

### 1. Register it with Discord

Add an entry to the `commands` array in `scripts/register_commands.ts`, then run:

```bash
npm run register
```

### 2. Handle it in the Lambda

Add a branch for your command name in `lambda/main.py` inside the `type == 2` block:

```python
if name == "mycommand":
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"type": 4, "data": {"content": "My response"}}),
    }
```

Then redeploy:

```bash
npx cdk deploy
```

## Useful commands

| Command | Description |
|---|---|
| `npm run build` | Compile TypeScript to JS |
| `npm run watch` | Watch for changes and compile |
| `npm run test` | Run Jest unit tests |
| `npm run register` | Register slash commands with Discord |
| `npx cdk deploy` | Deploy stack to AWS |
| `npx cdk diff` | Compare deployed stack with current state |
| `npx cdk synth` | Emit the synthesized CloudFormation template |
