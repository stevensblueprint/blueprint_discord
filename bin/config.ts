import * as dotenv from 'dotenv';

dotenv.config();

export const config = {
    discordAppId: process.env.APP_ID || '',
    discordPublicKey: process.env.PUBLIC_KEY || '',
    discordGuildId: process.env.GUILD_ID || '',
    discordBotToken: process.env.BOT_TOKEN || '',
};