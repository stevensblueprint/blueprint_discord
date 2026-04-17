import * as dotenv from 'dotenv';
dotenv.config();

const APP_ID = process.env.APP_ID!;
const BOT_TOKEN = process.env.BOT_TOKEN!;
const GUILD_ID = process.env.GUILD_ID;

const commands = [
  {
    name: 'env',
    description: 'Manage encrypted .env files',
    options: [
      {
        type: 1, // SUB_COMMAND
        name: 'store',
        description: 'Encrypt and store a .env file',
        options: [
          {
            type: 11, // ATTACHMENT
            name: 'file',
            description: 'The .env file to store',
            required: true,
          },
          {
            type: 3, // STRING
            name: 'passphrase',
            description: 'Passphrase used to encrypt the file',
            required: true,
          },
        ],
      },
      {
        type: 1, // SUB_COMMAND
        name: 'get',
        description: 'Retrieve and decrypt a stored .env file',
        options: [
          {
            type: 3, // STRING
            name: 'name',
            description: 'The UUID key returned when storing the file',
            required: true,
          },
          {
            type: 3, // STRING
            name: 'passphrase',
            description: 'Passphrase used to decrypt the file',
            required: true,
          },
        ],
      },
    ],
  },
  {
    name: 'designer',
    description: 'testing designer command'
  }
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
