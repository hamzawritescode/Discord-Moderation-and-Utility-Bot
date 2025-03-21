# ------------------ About the Developer ------------------ #
# Developer: Hamza
# GitHub Profile: https://github.com/hamzawritescode
# Codédex Profile: https://www.codedex.io/@HamzaWritesCode
# Project Repository: https://github.com/hamzawritescode/Discord_Bot
# Codédex Project Link: https://www.codedex.io/community/project-showcase/MJbHinqVP98yuGrw4ft6
#
#
# Hamza is a Python programmer with a passion for creating clean, efficient, 
# and impactful code. With a focus on problem-solving and innovation, 
# he enjoys building tools and projects that make a real difference. 
# This Discord bot is one of his many creations, designed to enhance 
# server management and engagement.

# ------------------ About the Project ------------------ #
# Project Name: Discord Moderation and Utility Bot
# Description: 
# This feature-rich Discord bot is designed for server management and engagement. 
# It includes moderation tools like kick, ban, and warn, along with fun and utility commands.
#
# Key Features:
# - Moderation: Kick, ban, warn, mute, and unmute users.
# - Utility: Get server info, user info, and latency.
# - Fun: Share random compliments.
# - Customizable leveling system to reward user engagement.
# - Error handling with user-friendly messages.

# ------------------ Required Modules ------------------ #
# Install the required modules using these commands:
# pip install discord.py
# logging, json, and random are part of Python's standard library.


# ------------------------ Code -------------------------------- #



import discord  # For interacting with the Discord API
from discord.ext import commands  # For bot commands and extensions
import logging  # For logging events and information
import json  # For managing warning data in JSON format
import random  # For generating random compliments

# ------------------ Logging Setup ------------------ #
logging.basicConfig(level=logging.INFO)

# ------------------ Bot Intents ------------------ #
intents = discord.Intents.default()
intents.members = True  # Enable member-related actions
intents.messages = True  # Enable message-related actions
intents.guilds = True    # Enable guild-related actions
intents.message_content = True  # Enable reading message content (for commands)

# ------------------ Initialize Bot ------------------ #
bot = commands.Bot(command_prefix='~', intents=intents)

# ------------------ Load Warnings Data ------------------ #
def load_warnings():
    """Load warning data from JSON file."""
    try:
        with open('warnings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

warnings_data = load_warnings()

# ------------------ Events ------------------ #
@bot.event
async def on_ready():
    """Runs when the bot is ready."""
    print(f'Logged in as {bot.user}!')
    await bot.change_presence(activity=discord.Game(name="Moderating your server"))

# ------------------ Moderation Commands ------------------ #
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    """Kick a member from the server."""
    await member.kick(reason=reason)
    await ctx.send(f'Kicked {member.mention} for: {reason or "No reason provided"}')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    """Ban a member from the server."""
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention} for: {reason or "No reason provided"}')

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member: str):
    """Unban a member from the server."""
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')
    for banned_entry in banned_users:
        if banned_entry.user.name == member_name and banned_entry.user.discriminator == member_discriminator:
            await ctx.guild.unban(banned_entry.user)
            await ctx.send(f'Unbanned {banned_entry.user.mention}')
            return
    await ctx.send(f'User {member} not found in the ban list.')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Clear a specified number of messages."""
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'Cleared {amount} messages!', delete_after=5)

@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    """Warn a member and store the reason."""
    user_id = str(member.id)
    warnings_data.setdefault(user_id, []).append(reason or "No reason provided")

    with open('warnings.json', 'w') as f:
        json.dump(warnings_data, f)

    await ctx.send(f'{member.mention}, you have been warned for: {reason or "No reason provided"}')

@bot.command()
@commands.has_permissions(kick_members=True)
async def view_warnings(ctx, member: discord.Member):
    """View warnings for a specific member."""
    user_id = str(member.id)
    warnings = warnings_data.get(user_id, [])
    if warnings:
        await ctx.send(f'{member.mention} has the following warnings: ' + ', '.join(warnings))
    else:
        await ctx.send(f'{member.mention} has no warnings.')

# ------------------ Informative Commands ------------------ #
@bot.command()
async def serverinfo(ctx):
    """Display information about the server."""
    server = ctx.guild
    embed = discord.Embed(title=f"{server.name}'s Info", color=discord.Color.blue())
    embed.add_field(name="Owner", value=server.owner, inline=True)
    embed.add_field(name="Members", value=server.member_count, inline=True)
    embed.add_field(name="Created At", value=server.created_at.strftime("%b %d, %Y"), inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    """Display information about a user."""
    member = member or ctx.author
    embed = discord.Embed(title=f"{member.name}'s Info", color=discord.Color.green())
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Joined At", value=member.joined_at.strftime("%b %d, %Y"), inline=True)
    embed.add_field(name="Roles", value=", ".join([role.name for role in member.roles if role.name != "@everyone"]), inline=True)
    await ctx.send(embed=embed)

# ------------------ Utility Commands ------------------ #
@bot.command()
async def ping(ctx):
    """Check the bot's latency."""
    await ctx.send(f'Pong! Latency: {round(bot.latency * 1000)}ms')

@bot.command()
async def compliment(ctx, member: discord.Member = None):
    """Send a random compliment to a user."""
    member = member or ctx.author
    compliments = [
        "You're amazing!", "You're a true gem!", "You light up the room!", 
        "You're the best!", "You're fantastic!", "You make everything better!"
    ]
    await ctx.send(f'{member.mention}, {random.choice(compliments)}')

# ------------------ Error Handling ------------------ #
@kick.error
@ban.error
@warn.error
@clear.error
async def command_error(ctx, error):
    """Handle command errors gracefully."""
    if isinstance(error, commands.BadArgument):
        await ctx.send('Could not find that member.')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('You do not have permission to use this command.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please provide the necessary arguments.')

# ------------------ Run the Bot ------------------ #
bot.run('your_bot_token_here')


# --------------------------- Code Ended ------------------------------ #
