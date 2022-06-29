import secrets, asyncio, nextcord
from nextcord.ext.commands import Bot
from nextcord.ext import commands
from enum import Enum
from nextcord.ext import commands
import nextcord, re, random, collections, math
from nextcord.ui import select
from nextcord.ui import text_input
from collections import defaultdict
from time import sleep
intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
bot = Bot(command_prefix='.', intents=intents)
claims = {}
class CommandType(Enum):
    Whois=1
    Search=2
    Roll=3
class Dropdown(nextcord.ui.Select):
    def __init__(self, items):
        options = []
        for item in items:
            options.append(nextcord.SelectOption(label=item, value=item))
        super().__init__(placeholder='Choose an Item', min_values=1, max_values=1, options=options)
    async def callback(self, interaction: nextcord.Interaction):
        await loot_channel.send(f"> {interaction.user.display_name} wants to claim {self.values[0]} for {claims[interaction.user.display_name]}")
        await interaction.message.delete()
class DropdownView(nextcord.ui.View):
    def __init__(self, dropdown):
        super().__init__()
        self.add_item(dropdown)
creds = secrets.get_secrets()
campaign = creds["Campaign"]
general = creds["General"]
roll = creds["Roll"]
loot = creds["Loot"]
test = creds["Test"]
guild = creds["Guild"]
#campaign_channel = bot.fetch_channel(campaign)
general_channel =  bot.get_channel(int(general))
#roll_channel = bot.fetch_channel(roll)
#loot_channel = bot.fetch_channel(loot)
gold = 0
@bot.event
async def on_ready():
    global general_channel, campaign_channel, test_channel, loot_channel, guild
    general_channel = bot.get_channel(int(general))
    campaign_channel = bot.get_channel(int(campaign))
    loot_channel = bot.get_channel(int(loot))
    test_channel = bot.get_channel(int(test))
    guild = bot.get_guild(int(guild))
    print("Ready")

@bot.command()
async def search(ctx, args):
    print("args:",args)
    searchmsgs = await campaign_channel.history(limit=800).flatten()
    search_results = []
    for searchmsg in searchmsgs:
        has_content = searchmsg.content.lower().find(args.lower())
        is_code_block = searchmsg.content.find("```")
        if has_content > -1 and is_code_block > -1 and searchmsg.author.bot is False:
            search_results.append(searchmsg.content)
    print(search_results)
    for search_result in search_results:
        await ctx.send(search_result)

    pass
@bot.command()
async def whois(ctx, args):
    whoisresults = []
    whomsgs = await campaign_channel.history(limit=800).flatten()
    print("args",args)
    for whomsg in whomsgs:
        print("Author",whomsg.author)
        has_person = whomsg.content.lower().find(args.lower())

        is_green = whomsg.content[0:2] == "> "
            #print("whomsgcontent - |", whomsg.content[0:2], "-",whomsg.content)
        if is_green and has_person > -1 and whomsg.author.bot is not True:
            whoisresults.append(whomsg.content)
    for whoisresult in whoisresults:
        await ctx.send(whoisresult)

@bot.command()
async def roll(ctx, arg):
    pos= 1
    roll =re.split("\D", arg)
    if roll[0] == '':
        roll[0] =1
    if str(arg).find('-') > -1:
        pos = -1
    for a in roll:
        print(a)
    if len(roll) > 2:
        roll = int(roll[0]) * random.randrange(1,int(roll[1])+1)+int(roll[2]) * pos
    else:
        roll = int(roll[0]) * random.randrange(1,int(roll[1])+1)
    await ctx.send(f"> {str(ctx.author)[:-5]} rolled a {roll}!")

@bot.command()
async def bid(ctx, args):
    try:
        int(args)
    except:
        ctx.send("Bids must be a whole number")
    global claims
    claims[str(ctx.author)[:-5]] = int(args)
    msgs = await loot_channel.history(limit=800).flatten()
    loot_code_block = ''
    items_for_bid = []
    for msg in msgs:
        if msg.content.find('```') > -1:
            loot_code_block = msg.content.split('```')[1]
    for it in loot_code_block.split("\n"):
        if it != '':
            if it.lower().find("misc") == -1 and it.lower().find("gold") == -1:
                items_for_bid.append(it)
    drop = Dropdown(items_for_bid)
    dropView = DropdownView(drop)
    await ctx.author.send(view=dropView)
@bot.command()
async def get_bid(ctx, args):
    pass
async def post(msg, channel):
    await channel.send(msg)
    pass

@bot.command()
async def clear_chat(ctx):
    
    loot_history = await loot_channel.history(limit=800).flatten()
    for msg in loot_history:
        if msg.author.bot:
            await msg.delete()

@bot.command()
async def distribute_loot(ctx, args):
    try:
        int(args)
    except:
        ctx.send("argument must be a whole number")
    total_bids = int(args)
    loot_history = await loot_channel.history(limit=800).flatten()
    loot_lists = await extract_code_block(loot_history)
    bid_history = await loot_channel.history(limit=800).flatten()
    current_bids = []
    gold = await get_gold(loot_lists[0])
    unbid_items = loot_lists[0].split("\n")[1:-1]
    for u_items in unbid_items:
        if u_items.lower().find('misc') > -1 or u_items.lower().find('gold') >-1 or u_items.lower().find('gp') >-1:
            unbid_items.remove(u_items)
    for bid_item in bid_history:
        try:
            len(loot_lists) > 1
            if bid_item.created_at > loot_lists[0].created_at and bid_item.created_at < loot_lists[1].created_at:
                current_bids.append(bid_item)
        except:
            current_bids.append(bid_item)

    item_bids = await extract_green_text(current_bids)
    i_bids = await parse_bids(item_bids)
    Player_winners = defaultdict(list)
    Gold_cost = {}
    
    for i_bid in i_bids:
        print("i_bids",i_bids)
        
        winner = ("",0)
        for i_player in i_bids[i_bid]:
            print("Bid",i_player, i_bid)
            
            if i_player[1] > winner[1]:
                print(i_player[0], i_player[1])
                winner = i_player
            print("winner", winner, i_bid)
        print("i_bid",i_bid, winner)
        print("unbid_items",unbid_items)
        unbid_items.remove(i_bid)
        if winner != ("",0):
            
            Player_winners[winner[0]].append(i_bid)
            if winner[0] in Gold_cost:
                Gold_cost[winner[0]] +=  winner[1]
            else:
                Gold_cost[winner[0]] = winner[1]
        
    bids_taken_out = 0
    for winner_dict in Player_winners:
        result_message= ""
        
        print("WINNIG BID",winner_dict, Player_winners[winner_dict])
        print("CURRENT GOLD PILE", gold)
        goldsplit = gold//(total_bids - bids_taken_out)
        bids_taken_out += 1
        print("CURRENT GOLDSPLIT SIZE", goldsplit)
        print(winner_dict, Gold_cost[winner_dict])
        goldsplit -= Gold_cost[winner_dict]
        gold -= Gold_cost[winner_dict]
        for item in Player_winners[winner_dict]:
            
            member = guild.get_member_named(winner_dict)
            if member is not None:
                result_message += item + "\n"
                print(winner_dict,":",result_message)
                is_gain = "gain" if goldsplit >= 0 else "pay"
            
        await member.send(f"Congratulations you won\n {result_message} and {is_gain} {abs(goldsplit)} gold")
    unbid_str = ""
    for u_it in unbid_items:
        unbid_str += u_it + '\n'
    await loot_channel.send(f"Everyone that lost or didn't bid gets {gold//(total_bids-len(Player_winners))} gold.\n{unbid_str}were unbid and will be sold for their value")
    
async def parse_bids(player_bids):
    try:
        bid_dict = defaultdict(list)
        
        for bid in player_bids:
            biddata = bid.split(" wants to claim ")
            bid_split = biddata[1].split(" for ")
            bid_dict[bid_split[0]].append((biddata[0] , int(bid_split[1])))


        return bid_dict
    except Exception as e:
        print(f"failed to parse bids {e}")

async def extract_green_text(green_messages):
    bids = []
   
    for green_message in green_messages:
        if green_message.content[:2] == "> ":
           
            bids.append(green_message.content[2:])
    return bids
async def extract_code_block(code_messages):
    extracted_blocks = []
    for code_message in code_messages:
        if code_message.content.find('```') > -1:
            extracted_blocks.append(code_message.content)
    return extracted_blocks

async def get_gold(block):
    _gold = 0
    for row in block.split('\n'):
        if row.lower().find("misc") > -1 or row.lower().find("gold") > -1:
            _gold = int(row.split(" ")[0])
    return _gold

#bot = DiscordBot(command_prefix = '.', intents=intents)
@bot.command()
async def clear_commands(ctx):
    loot_history = await loot_channel.history(limit=800).flatten()
    for his in loot_history:
        if his.content[0] == '.':
            await his.delete()
@bot.command()
async def get_current_bids(ctx):
    bid_history = await loot_channel.history(limit=800).flatten()
    last_loot = await extract_code_block(bid_history)
    current_bids = []
    for bid_item in bid_history:
        try:
            if bid_item.created_at > last_loot[0].created_at:
                current_bids.append(bid_item)
        except:
            current_bids.append(bid_item)
    
    all_bids = await extract_green_text(current_bids)
    for bid in all_bids:
        await ctx.send(bid)
@bot.command()
async def get_money_split(ctx, arg):
    gold = await get_gold()
    await ctx.send(f"the current split for {arg} is {gold} gold")
bot.run(creds['APIKey'])