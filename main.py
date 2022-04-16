import discord, os, dotenv
import pandas as pd
from discord import message
from discord.ext import commands
from discord.ext.commands import Bot
from discord import member
from discord import DMChannel
from dotenv import load_dotenv

load_dotenv()
client = commands.Bot(command_prefix = os.getenv('PREFIX'))

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Streaming(name="By GODMOD, special thx ModerNik", url="https://www.twitch.tv/nullexcept1on"))

@client.command()
async def иск(ctx):
    case_id = int(os.getenv('CASE_ID'))
    plaintiff = ctx.author.id
    def check(i):
        return i.author.id == ctx.author.id
    await ctx.reply('Укажите ник игрока (@User#0000)')
    defendant = (await client.wait_for('message', check=check)).content
    while defendant[2:3] == '&':
        await ctx.reply('Укажите ник игрока (@User#0000)')
        defendant = (await client.wait_for('message', check=check)).content
    await ctx.reply('Укажите возможные статьи. Если таковых нет - введите 0')
    article = (await client.wait_for('message', check=check)).content
    await ctx.reply('Опишите подробности дела')
    more = (await client.wait_for('message', check=check)).content
    dotenv.set_key(dotenv.find_dotenv(),'CASE_ID',str(case_id+1))
    embed = discord.Embed(
    title = '-'*60,
    colour = discord.Colour.dark_magenta()
    )
    embed.add_field(name='Дело:', value=case_id, inline=False)
    embed.add_field(name='Подающий:', value=f'<@!{plaintiff}>', inline=False)
    embed.add_field(name='Виновный:', value=defendant, inline=False)
    embed.add_field(name='Статьи:', value=article, inline=False)
    embed.add_field(name='Подробности:', value=more, inline=False)
    await ctx.channel.send(embed=embed)
    data = pd.read_csv('data.csv', delimiter=',')
    data = data.append({'case_id':int(os.getenv('CASE_ID')), 'plaintiff':plaintiff, 'defendant':defendant, 'article':article, 'more':more, 'verdict':'-', 'status':'открыто'}, ignore_index=True)
    data.to_csv('data.csv', encoding='utf-8', index=False)

@client.command(pass_context=True)
@commands.has_role(os.environ['ROLE'])
async def вердикт(ctx, *, case_id):
    def check(i):
        return i.author.id == ctx.author.id 
    role = discord.utils.get(ctx.guild.roles, name=os.environ['ROLE'])
    if role in ctx.author.roles:
        await ctx.channel.send('Итог суда')
        verdict = (await client.wait_for('message', check=check)).content
        embed = discord.Embed(
        title = '-'*60,
        colour = discord.Colour.dark_magenta()
        )
        embed.add_field(name='Дело:', value=case_id, inline=False)
        embed.add_field(name='Вердикт:', value=verdict, inline=False)
        await ctx.channel.send(embed=embed)

        data = pd.read_csv('data.csv', delimiter=',')
        for i in data.index:
            print(data.loc[i, 'case_id'])
            if data.loc[i, 'case_id'] == int(case_id):
                data.loc[i, 'verdict'] = str(verdict)
                data.loc[i, 'status'] = "закрыто"
                data.to_csv('data.csv', sep=',', index=False, encoding='utf-8')

@client.command()
async def дело(ctx, *, case_id):
    data = pd.read_csv('data.csv', delimiter=',')
    for i in data.index:
        if data.loc[i, 'case_id'] == int(case_id):
            embed = discord.Embed(
            title = '-'*60,
            colour = discord.Colour.dark_magenta()
            )
            embed.add_field(name='Дело:', value=data.loc[i, 'case_id'], inline=False)
            embed.add_field(name='Подающий:', value=f'<@!{data.loc[i, "plaintiff"]}>', inline=False)
            embed.add_field(name='Виновный:', value=data.loc[i, 'defendant'], inline=False)
            embed.add_field(name='Статьи:', value=data.loc[i, 'article'], inline=False)
            embed.add_field(name='Подробности:', value=data.loc[i, 'more'], inline=False)
            embed.add_field(name='Вердикт:', value=data.loc[i, 'verdict'], inline=False)
            embed.add_field(name='Состояние:', value=data.loc[i, 'status'], inline=False)
            await ctx.channel.send(embed=embed)

@client.command()
async def отменить(ctx, *, case_id):
    role = discord.utils.get(ctx.guild.roles, name=os.environ['ROLE'])
    data = pd.read_csv('data.csv', delimiter=',')
    for i in data.index:
        if data.loc[i, 'case_id'] == int(case_id) and (data.loc[i, 'plaintiff'] == ctx.author.id or role in ctx.author.roles):
            data = data.drop([i])
            data.to_csv('data.csv', sep=',', encoding='utf-8', index=False)
            await ctx.reply('Удалено')

@client.command()
async def заявки(ctx):
    data = pd.read_csv('data.csv', delimiter=',')
    for i in data.index:
        if data.loc[i, 'status'] == 'открыто':
            embed = discord.Embed(
            title = '-'*60,
            colour = discord.Colour.dark_magenta()
            )
            embed.add_field(name='Дело:', value=data.loc[i, 'case_id'], inline=False)
            embed.add_field(name='Подающий:', value=f'<@!{data.loc[i, "plaintiff"]}>', inline=False)
            embed.add_field(name='Виновный:', value=data.loc[i, 'defendant'], inline=False)
            embed.add_field(name='Статьи:', value=data.loc[i, 'article'], inline=False)
            embed.add_field(name='Подробности:', value=data.loc[i, 'more'], inline=False)
            embed.add_field(name='Вердикт:', value=data.loc[i, 'verdict'], inline=False)
        await ctx.channel.send(embed=embed)

@client.command(pass_context=True)
async def мои_дела(ctx):
    user = int(ctx.author.id)
    data = pd.read_csv('data.csv', delimiter=',')
    await ctx.author.send('**ВАШИ ИСКИ**')
    for i in data.index:
        if int(data.loc[i, 'plaintiff']) == user and data.loc[i, 'status'] == 'открыто':
            embed = discord.Embed(
            title = '-'*60,
            colour = discord.Colour.dark_magenta()
            )
            embed.add_field(name='Дело:', value=data.loc[i, 'case_id'], inline=False)
            embed.add_field(name='Подающий:', value=f'<@!{data.loc[i, "plaintiff"]}>', inline=False)
            embed.add_field(name='Виновный:', value=data.loc[i, 'defendant'], inline=False)
            embed.add_field(name='Статьи:', value=data.loc[i, 'article'], inline=False)
            embed.add_field(name='Подробности:', value=data.loc[i, 'more'], inline=False)
            embed.add_field(name='Вердикт:', value=data.loc[i, 'verdict'], inline=False)
            await ctx.author.send(embed=embed)

    await ctx.author.send('**ИСКИ ПРОТИВ ВАС**')
    for i in data.index:
        if int(data.loc[i, 'defendant'][2:-1]) == user and data.loc[i, 'status'] == 'открыто':
            embed = discord.Embed(
            title = '-'*60,
            colour = discord.Colour.dark_magenta()
            )
            embed.add_field(name='Дело:', value=data.loc[i, 'case_id'], inline=False)
            embed.add_field(name='Подающий:', value=f'<@!{data.loc[i, "plaintiff"]}>', inline=False)
            embed.add_field(name='Виновный:', value=data.loc[i, 'defendant'], inline=False)
            embed.add_field(name='Статьи:', value=data.loc[i, 'article'], inline=False)
            embed.add_field(name='Подробности:', value=data.loc[i, 'more'], inline=False)
            embed.add_field(name='Вердикт:', value=data.loc[i, 'verdict'], inline=False)
            await ctx.author.send(embed=embed)

if __name__ == "__main__":
    client.run(os.getenv('BOT_TOKEN'))
