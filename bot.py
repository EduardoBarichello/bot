import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import os
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Definir intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True


bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')


@bot.command(name="limpar", help="Limpa um número específico de mensagens.")
@has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f'{amount} mensagens limpas por {ctx.author.mention}', delete_after=5)


@bot.command(name="kick", help="Kicka um usuário do servidor.")
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'Usuário {member.mention} foi kickado por {ctx.author.mention}. Motivo: {reason}')


@bot.command(name="ban", help="Bane um usuário do servidor.")
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Usuário {member.mention} foi banido por {ctx.author.mention}. Motivo: {reason}')


@bot.command(name="unban", help="Desbane um usuário do servidor.")
@has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Usuário {user.mention} foi desbanido por {ctx.author.mention}.')
            return


@bot.command(name="mute", help="Muta um usuário do servidor.")
@has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    muted_role = discord.utils.get(guild.roles, name="Muted")

    if not muted_role:
        muted_role = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False, read_message_history=True, read_messages=False)

    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f'Usuário {member.mention} foi mutado por {ctx.author.mention}. Motivo: {reason}')


@bot.command(name="unmute", help="Desmuta um usuário do servidor.")
@has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

    await member.remove_roles(muted_role)
    await ctx.send(f'Usuário {member.mention} foi desmutado por {ctx.author.mention}.')


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)


@bot.command(name="ping", help="Mostra a latência do bot.")
async def ping(ctx):
    await ctx.send(f'Pong! Latência: {round(bot.latency * 1000)}ms')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send(f'Você não tem permissão para usar este comando, {ctx.author.mention}.')

bot.run(TOKEN)
