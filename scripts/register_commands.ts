import * as dotenv from 'dotenv';
dotenv.config();

const APP_ID = process.env.APP_ID!;
const BOT_TOKEN = process.env.BOT_TOKEN!;
const GUILD_ID = process.env.GUILD_ID;

const commands = [
  {
    name: 'hello',
    description: 'Replies with Hello, World!',
  },
];

const url = GUILD_ID
  ? `https://discord.com/api/v10/applications/${APP_ID}/guilds/${GUILD_ID}/commands`
  : `https://discord.com/api/v10/applications/${APP_ID}/commands`;

(async () => {
  const res = await fetch(url, {
    method: 'PUT',
    headers: {
      Authorization: `Bot ${BOT_TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(commands),
  });

  if (!res.ok) {
    console.error('Failed to register commands:', await res.text());
    process.exit(1);
  }

  console.log('Commands registered:', await res.json());
})();
