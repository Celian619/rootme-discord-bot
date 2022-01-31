# rootme-discord-bot

This python script run a bot that print on a discord channel new challenges done by users on root-me.

## installation steps
#### Create a discord bot on [Developer Portal](http://discordapp.com/developers/applications) and add it to your server.

#### Download the script and configure these values at the beginning:

- database_file
- log_file
- channel_id
- api_key_cookie : find this value on your root-me profile settings.
- bot_token

#### Create the database file
 
Write `{"uids" : {}, "infos" : {}}` in the file.

#### Create the chrontab

Switch to a user with less privilege.
Copy the content of crontab file and edit the default path /home/tom to your own path.
Add this to your crontab and run the script with `nohup discord.py &`

This crontab ensure the script will be running 24/7.

## commands
```
!add-user name uid  
Add a root-me user with his uid (can be found in your profile settings).


!remove-user name  
Remove a user with the name specified in add-user.

!users  
List all users registered on the bot.

!classement  
Print ranking of users.
```
