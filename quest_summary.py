import json
import requests
import time
import locale
import configparser
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)

rarecandy_l10n = ['Sonderbonbon', 'Rare Candy']
stardust_l10n = ['Stardust', 'Sternenstaub']
silverpinap_l10n = ['Silberne Sananabeere', 'Silver Pinap Berry']

config = configparser.ConfigParser()
config.read('config.ini')

try:
    token = config.get('CONFIG', 'TOKEN', fallback=None)
    chat_id = config.get('CONFIG', 'CHATID', fallback=None)
    discord_webhook = config.get('CONFIG', 'WEBHOOK', fallback=None)
    mapurl = config.get('CONFIG', 'MAPURL',
                        fallback="http://www.google.com/maps")
    madminurl = config.get('CONFIG', 'MADMINURL')
    localeSetting = config.get('CONFIG', 'LOCALE', fallback="en-US")
    pokemonIds = config.get('CONFIG', 'POKEMON', fallback="")
    rarecandy = config.get('CONFIG', 'RARECANDY', fallback="")
    stardust = config.get('CONFIG', 'STARDUST', fallback="")
    silverpinap = config.get('CONFIG', 'SILVERPINAP', fallback="")
    candymsg = config.get('CONFIG', 'CANDYMESSAGE', fallback="Rare Candy:")
    dustmsg = config.get('CONFIG', 'DUSTMESSAGE', fallback="Stardust:")
    pinapmsg = config.get('CONFIG', 'PINAPMESSAGE', fallback="Silver Pinap:")
    notfoundmsg = config.get('CONFIG', 'NOTFOUNDMESSAGE',
                             fallback="Not found today.")
    nextpagemsg = config.get('CONFIG', 'FOLLOWINGMESSAGE',
                             fallback="Continued in following message ...")
    user = config.get('CONFIG', 'USER', fallback="")
    passw = config.get('CONFIG', 'PASS', fallback="")
except configparser.NoOptionError as e:
    print("Missing required config setting: {}".format(e))
    sys.exit(1)

locale.setlocale(locale.LC_TIME, localeSetting)

if not token or not chat_id:
    telegram_enabled = False
    print("Not using telegram!")
else:
    telegram_enabled = True
    print("Using telegram!")

if not discord_webhook:
    discord_enabled = False
    print("Not using discord!")
else:
    discord_enabled = True
    print("Using discord!")

if not telegram_enabled and not discord_enabled:
    print("Missing required settings for telegram and discord. Aborting.")
    sys.exit(1)

pokemonIds = pokemonIds.split(',')
stardust = stardust.split(',')
rarecandy = rarecandy.split(',')
silverpinap = silverpinap.split(',')

text_file = open('text.txt', 'r', encoding='utf-8')
text = text_file.read()
discord_file = open('text.txt', 'r', encoding='utf-8')
discord_text = discord_file.read()

candyList = []
starList = []
pokeList = []
silverList = []

discord_candyList = []
discord_starList = []
discord_pokeList = []
discord_silverList = []

for k in rarecandy:
    candyList.append([])
    discord_candyList.append([])
for k in stardust:
    starList.append([])
    discord_starList.append([])
for k in silverpinap:
    silverList.append([])
    discord_silverList.append([])
for k in pokemonIds:
    pokeList.append(False)
    discord_pokeList.append(False)

json_input = requests.get(madminurl + '/get_quests', auth=(user, passw))
while json_input.status_code != 200:
    time.sleep(5)
    json_input = requests.get(madminurl + '/get_quests', auth=(user, passw))

data = json_input.json()

# insert mapurl, str(d['latitude']), str(d['longitude']), d['name']
telegram_pattern = '<a href="{}/?lat={}&lon={}&zoom=16">{}</a>\n'
# insert d['name'], mapurl, str(d['latitude']), str(d['longitude'])
discord_pattern = '[{}]({}/?lat={}&lon={}&zoom=16)\n'


for d in data:
    if d['quest_reward_type'] == "Item":
        if d['item_type'] in rarecandy_l10n:
            if str(d['item_amount']) in rarecandy:
                link = (telegram_pattern
                        .format(mapurl, str(d['latitude']),
                                str(d['longitude']), d['name']))
                mdlink = (discord_pattern
                          .format(d['name'], mapurl, str(d['latitude']),
                                  str(d['longitude'])))
                candyList[rarecandy.index(str(d['item_amount']))].append(link)
                discord_candyList[rarecandy.index(
                    str(d['item_amount']))].append(mdlink)
        elif d['item_type'] in silverpinap_l10n:
            if str(d['item_amount']) in silverpinap:
                link = telegram_pattern.format(mapurl, str(d['latitude']),
                                               str(d['longitude']), d['name'])
                mdlink = (discord_pattern
                          .format(d['name'], mapurl, str(d['latitude']),
                                  str(d['longitude'])))
                silverList[silverpinap.index(
                    str(d['item_amount']))].append(link)
                discord_silverList[silverpinap.index(
                    str(d['item_amount']))].append(mdlink)
    elif d['quest_reward_type'] in stardust_l10n:
        if str(d['item_amount']) in stardust:
            link = telegram_pattern.format(mapurl, str(d['latitude']),
                                           str(d['longitude']), d['name'])
            mdlink = (discord_pattern
                      .format(d['name'], mapurl, str(d['latitude']),
                              str(d['longitude'])))
            starList[stardust.index(str(d['item_amount']))].append(link)
            discord_starList[stardust.index(
                str(d['item_amount']))].append(mdlink)
    elif d['quest_reward_type'] == 'Pokemon':
        if str(d['pokemon_id']) in pokemonIds:
            link = (telegram_pattern
                    .format(mapurl, str(d['latitude']), str(d['longitude']),
                            d['name']) + '$' + d['pokemon_id'] + '$')
            mdlink = (discord_pattern
                      .format(d['name'], mapurl, str(d['latitude']),
                              str(d['longitude'])) +
                      '$' + d['pokemon_id'] + '$')
            text = text.replace('$' + d['pokemon_id'] + '$', link)
            discord_text = discord_text.replace('$' + d['pokemon_id'] + '$',
                                                mdlink)
            pokeList[pokemonIds.index(d['pokemon_id'])] = True
            discord_pokeList[pokemonIds.index(d['pokemon_id'])] = True

starstring = ''
candystring = ''
silverstring = ''

discord_starstring = ''
discord_candystring = ''
discord_silverstring = ''

for i in range(0, len(stardust)):
    if len(starList[i]) == 0:
        continue
    starstring += '\n🌟 ' + stardust[i] + ' <b>' + dustmsg + '</b>\n'
    discord_starstring += '\n🌟 ' + stardust[i] + ' ' + dustmsg + '\n'
    for k in starList[i]:
        starstring += k
    for k in discord_starList[i]:
        discord_starstring += k
for i in range(0, len(rarecandy)):
    if len(candyList[i]) == 0:
        continue
    candystring += '\n🍬 ' + rarecandy[i] + ' <b>' + candymsg + '</b>\n'
    discord_candystring += '\n🍬 ' + rarecandy[i] + ' ' + candymsg + '\n'
    for k in candyList[i]:
        candystring += k
    for k in discord_candyList[i]:
        discord_candystring += k
for i in range(0, len(silverpinap)):
    if len(silverList[i]) == 0:
        continue
    silverstring += ('\n🍍 ' + silverpinap[i] +
                     ' <b>' + pinapmsg + '</b>\n')
    discord_silverstring += ('\n🍍 ' + silverpinap[i] +
                             ' ' + pinapmsg + '\n')
    for k in silverList[i]:
        silverstring += k
    for k in discord_silverList[i]:
        discord_silverstring += k

for i in range(0, len(pokemonIds)):
    if pokeList[i]:
        text = text.replace('$' + pokemonIds[i] + '$', '')
        discord_text = discord_text.replace('$' + pokemonIds[i] + '$', '')
    else:
        text = text.replace('$' + pokemonIds[i] + '$',
                            '<i>' + notfoundmsg + '</i>\n')
        discord_text = discord_text.replace('$' + pokemonIds[i] + '$',
                                            '' + notfoundmsg + '\n')


telegram_replace = (('$rarecandy$', candystring), ('$stardust$', starstring),
                    ('$silverpinap$', silverstring),
                    ('$amount$', str(len(data))),
                    ('$date', time.strftime("%A, %e.%m.%Y")), ('&', '%26amp;'))
for r in telegram_replace:
    text = text.replace(*r)

discord_replace = (('$rarecandy$', discord_candystring),
                   ('$stardust$', discord_starstring),
                   ('$silverpinap$', discord_silverstring),
                   ('$amount$', str(len(data))),
                   ('$date', time.strftime("%A, %e.%m.%Y")), ('<b>', '**'),
                   ('</b>', '**'))
for r in discord_replace:
    discord_text = discord_text.replace(*r)


def bot_sendtelegram(bot_message):
    send_part = ""
    for part in bot_message.split(2 * os.linesep):
        new_part = str(send_part) + str(part)
        if new_part.count("http") > 80:
            send_part += str(2 * os.linesep)
            send_part += str("<i>" + nextpagemsg + "</i>")
            send_text = ('https://api.telegram.org/bot{}/sendMessage?chat_id={}' +
                         '&parse_mode=html&text={}').format(token, chat_id,
                                                            send_part)
            requests.get(send_text)
            send_part = str(part)
        else:
            send_part += str(2 * os.linesep)
            send_part += str(part)
    send_text = ('https://api.telegram.org/bot{}/sendMessage?chat_id={}' +
                 '&parse_mode=html&text={}').format(token, chat_id,
                                                    send_part)
    requests.get(send_text)


def discord_request(data, wh):
    success = False
    while not success:
        result = requests.post(wh, data=json.dumps(data),
                               headers={"Content-Type":
                                        "application/json"})
        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}."
                  .format(result.status_code))
            success = True
        time.sleep(1)


def bot_senddiscord(bot_message):
    for part in bot_message.split(2 * os.linesep):
        if len(part) > 2000:
            parts = part.split(os.linesep)
        else:
            parts = False
        if not parts:
            part += '\n\u200b'
            data = {"username": "questsummary-Bot", "content": part}
            print(part)
            discord_request(data, discord_webhook)
        else:
            for part in parts:
                data = {"username": "questsummary-Bot", "content": part}
                print(part)
                discord_request(data, discord_webhook)


if telegram_enabled:
    bot_sendtelegram(text)
if discord_enabled:
    bot_senddiscord(discord_text)
