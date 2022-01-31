import discord
import requests
import json
import asyncio
import datetime


#paramètres a modifier
database_file = '/home/tom/database.json'#Add the path to the database here
log_file = "/home/tom/output"#Add the path to the log file here
channel_id = 11111111111111111 # add the channel id here
api_key_cookie = {"api_key": "ADD_YOUR_API_KEY_HERE"}
bot_token = "YOUR_BOT_TOKEN_HERE"

#write this to create empty DB: {"uids" : {}, "infos" : {}}

client = discord.Client()

lock = asyncio.Lock()

#db format : {"uids" : users_uid, "infos" : users_info}


#format : {uid1 : name1, uid2 : name2}
users_uid = {}

users_info = {}





async def log(message):
        with open(log_file,"a") as out:
                out.write(str(datetime.datetime.now())+":"+str(message)+"\n")



async def update_db():
        async with lock:
                with open(database_file,"w") as info_file:
                        json.dump({"uids" : users_uid, "infos" :users_info},info_file)
                

async def add_user(name, uid):
        await log("Add user")
        for dict_uid,dict_name in users_uid.items():
                if dict_name == name or dict_uid == uid:
                        return ""
        users_uid[uid] = name
        users_info[uid] = {}

        pseudo = await update_user(uid)

        if pseudo == "":#l'uid is not valid
                del users_uid[uid]
                del users_info[uid]
        else:
                await update_db()
        return pseudo



async def remove_user(name):
        await log("Remove user")
        user_uid = 0

        for dict_uid, dict_name in users_uid.items():
                if name == dict_name:
                        user_uid = dict_uid
                        break
        if user_uid == 0:
                return ""

        users_uid.pop(user_uid)
        pseudo = users_info[user_uid]["nom"]
        users_info.pop(user_uid)


        await update_db()
        return pseudo
"""
format des challenges :
{'id_challenge': '33', 'date': '2019-10-10 14:58:41'}
"""
async def annoncer_challenge(uid,challenge):
        await asyncio.sleep(10)#ne pas brusquer l'api root-me
        await log("Annoncer challenge")
        bot_channel = client.get_channel(channel_id)
        url = "https://api.www.root-me.org/challenges/"+challenge['id_challenge']
        try:
                json_content = requests.get(url, cookies=api_key_cookie).json()[0]
        except:
                await log("Erreur lors de la récupération du challenge"+str(challenge))
                await bot_channel.send("**"+users_uid[uid]+"** a flag un challenge.")
                return

        nom_chall = json_content['titre']
        score = json_content['score']
        rubrique = json_content['rubrique']
        nom = users_uid[uid]


        #Teo [HEGZKLGDKSDJKGFKSJFK] a flag le challenge : Hash - Message Digest 5 (Cryptanalyse/5 pts)
        await bot_channel.send("**"+nom+"** a flag le challenge: ***"+nom_chall+"*** ("+rubrique+"/"+score+" pts)")


async def update_user(uid):
        async with lock:
                url = "https://api.www.root-me.org/auteurs/"+uid
                
                try:
                         r = requests.get(url, cookies=api_key_cookie)
                except:
                        await log("Request fail")
                        return ""
                if r.status_code != 200:
                        await log("L'utilisateur à l'uid :"+str(uid)+" n'est pas trouvé par l'API root-me => uid invalide ?")
                        await log("Status code : "+str(r.status_code))
                        return ""
                try:
                        json_content = r.json()
                except:
                        await log("Erreur au r.json()")
                        return ""
                del json_content["challenges"]
                del json_content["solutions"]#infos inutiles
                del json_content["statut"]
                del json_content["id_auteur"]
                #json_content = json.load(page)
                #print(json_content)
                pseudo = json_content['nom']

                if users_info[uid] != {} and json_content["validations"] != []:
                        if users_info[uid]["validations"] == []:#print tout les challenges
                                for challenge in json_content["validations"]:
                                         await annoncer_challenge(uid,challenge)
                        else:
                                last_chall = users_info[uid]["validations"]

                                for challenge in json_content["validations"]:
                                        if challenge["id_challenge"] != last_chall:#annonce tout les challenges fait après le dernier annoncé
                                                await annoncer_challenge(uid, challenge)
                                        else:
                                                break

                if json_content["validations"] != []:

                        json_content["validations"] = json_content["validations"][0]["id_challenge"]
                
                users_info[uid] = json_content
        return pseudo


async def print_classement():
        await log("Print classement")
        score_dict = []

        for uid, name in users_uid.items():
                score = users_info[uid]["score"]
                score_dict.append((int(uid,10),int(score,10)))
        classement = sorted(score_dict, key=lambda item: item[1],reverse=True)
        await log(classement)

        bot_channel = client.get_channel(channel_id)

        full_msg = ""
        place = 1
        for uid, score in classement:
                uid = str(uid)#sinon ça passe pas
                if place == 1:
                        full_msg += ":first_place: **"+users_uid[uid]+"** - "+str(users_info[uid]["position"])+"ème root-me (*"+str(score)+"* pts) \n"
                elif place == 2:
                        full_msg += ":second_place: **"+users_uid[uid]+"** - "+str(users_info[uid]["position"])+"ème root-me (*"+str(score)+"* pts) \n"
                elif place == 3:
                        full_msg += ":third_place: **"+users_uid[uid]+"** - "+str(users_info[uid]["position"])+"ème root-me (*"+str(score)+"* pts) \n"
                else:
                        full_msg += str(place)+"ème **"+users_uid[uid]+"** - "+str(users_info[uid]["position"])+"ème root-me (*"+str(score)+"* pts) \n"
                place+=1

        await bot_channel.send(full_msg[:-1])

@client.event
async def on_ready():
        await log("Bot "+str(client.user)+" is ready")
        await update_loop()


@client.event
async def on_message(message):
        if message.author == client.user or message.channel.id != channel_id:
                return

        commande = message.content
        if commande.startswith("!add-user "):
                if commande == "!add-user info"  :
                        await message.channel.send("Syntaxe : !add-user name uid\nVotre uid se trouve dans vos paramètres de profil")
                        return
                args = commande.split("!add-user ",1)[1].split(' ')
                if len(args) != 2:
                        await message.channel.send("Syntaxe : !add-user name uid\nVotre uid se trouve dans vos paramètres de profil")
                        return
                username = await add_user(args[0],args[1])#name,uid
                if username == "":
                        await message.channel.send("Ce nom ou cette uid sont déjà pris (ou l'uid n'est pas valide).")
                else:
                        await message.channel.send("Le profil rootme ["+username+"] appartenant à "+args[0]+" a été ajouté")
        elif commande.startswith("!remove-user"):
                args = commande.split("!remove-user ",1)[1].split(' ')


                username = await remove_user(args[0])#name

                if username == "":
                        await message.channel.send("Ce profil n'existe pas")
                else:
                        await message.channel.send("Le profil rootme ["+username+"] appartenant à "+args[0]+" a été supprimé")

        elif commande.startswith("!users"):
                await log("Print users")
                if len(users_uid.keys()) == 0:
                        await message.channel.send("Aucun profil")
                        return
                full_msg = ""
                for uid in users_uid.keys():
                        name = users_uid[uid]
                        username = users_info[uid]["nom"]
                        full_msg += "• **"+name+"** [*"+username+"*]\n"
                await message.channel.send(full_msg)
        elif commande.startswith("!classement"):
                await print_classement()
        elif commande.startswith("!help"):
                await message.channel.send("Les commandes du bot sont en message épinglé sur ce channel")


async def update_loop():
        while True:
                
                for uid in users_uid.keys():
                                try:
                                    await update_user(uid)
                                    
                                except Exception as e:
                                    await log("Crash on user "+str(uid))
                                    await log(str(e))
                                await update_db()
                                await asyncio.sleep(10)
                
                await log("all users done")

with open(database_file,"r") as info_file:
        jsonInfos = json.load(info_file)
        users_info = jsonInfos["infos"]
        users_uid = jsonInfos["uids"]


        client.run(bot_token)

