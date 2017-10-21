import datetime
import asyncio
import logging
import traceback

import discord


LOGGING_FORMAT = '[%(levelname)s - %(name)s - %(asctime)s] %(message)s'

# Good enough
BOTE_SPAM = [282500390891683841, 290757101914030080]

GUILDS = {
    'HTC':    184755239952318464,
    'HTSTEM': 282219466589208576,
    'Meta':   303365979444871169
}
JOINLOGS = {
    GUILDS['HTC']:    207659596167249920,
    GUILDS['HTSTEM']: 282477076454309888,
    GUILDS['Meta']:   303530104339038209
}
BACKUPS = {
    GUILDS['HTC']:    303374467336241152,
    GUILDS['HTSTEM']: 303374407420608513
}
AVATARLOGS = {
    GUILDS['HTC']: 305337536157450240,
    GUILDS['HTSTEM']: 305337565513515008
}
OWNER_ID = 140564059417346049
'''
## TESTING IDS
GUILDS = {
    'HTC':    290573725366091787
}
JOINLOGS = {
    GUILDS['HTC']:    290757101914030080
}
BACKUPS = {
    GUILDS['HTC']:    319830765842071563
}
OWNER_ID = 161508165672763392
## END TESTING SECTION
'''


PREFIX = "!"
CLIENTS = []


class JoinBot(discord.Client):
    def __init__(self):
        super().__init__()
        
        self.log = logging.getLogger(f'Bot')
        logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)
        
        self.bannedusers = {}
    
    async def broadcast_message(self, msg, guild, avatar=False):
        log_channel = None
        backup_channel = None
        if avatar:
            if guild.id in AVATARLOGS:
                log_channel = self.get_channel(AVATARLOGS[guild.id])

        else:
            if guild.id in JOINLOGS:
                log_channel = self.get_channel(JOINLOGS[guild.id])
            if guild.id in BACKUPS:
                backup_channel = self.get_channel(BACKUPS[guild.id])

        if log_channel is not None:
            try:
                await log_channel.send(msg)
            except Exception:
                self.log.error('An issue occured while trying to send to a joinlog.')
                traceback.print_exc()

        if backup_channel is not None:
            try:
                await backup_channel.send(msg)
            except Exception:
                self.log.error('An issue occured while trying to send to a backup.')
                traceback.print_exc()
    
    async def on_ready(self):
        print('Logged in as:')
        print(self.user.name)
        print(self.user.id)
        print('======')
    
    async def on_message(self, message):
        pass
    
    async def on_message_delete(self, message):
        pass
    
    async def on_member_join(self, member):
        if member.guild.id == GUILDS['HTC']:
            print('pres')
            await self.change_presence(game=discord.Game(name=f'for {member.guild.member_count} users'))

        time_now = datetime.datetime.utcnow()

        self.log.info(f'A user joined {member.guild.name}: {member} ({member.id})')

        msg = f':white_check_mark: {member.mention} (`{member}` User #{member.guild.member_count}) user joined the server.'
        if not member.avatar_url:
            msg += '\n:no_mouth: User doesn\'t have an avatar.'

        try:
            creation_time = member.created_at
            time_diff = time_now - creation_time

            msg += '\n'
            if time_diff.total_seconds() / 3600 <= 24:
                msg += ':clock1: '

            msg += 'User\'s account was created at ' + creation_time.strftime("%m/%d/%Y %I:%M:%S %p")
        except Exception:
            self.log.error('Something happened while tryin\' to do the timestamp grabby thing:')
            traceback.print_exc()

        await self.broadcast_message(msg, member.guild)
    
    async def on_member_remove(self, member):
        if member.guild.id == GUILDS['HTC']:
            await self.change_presence(game=discord.Game(name=f'for {member.guild.member_count} users'))
        
        # Wait for the ban event to fire (if at all)
        await asyncio.sleep(0.25)
        if member.guild.id in self.bannedusers and \
          member.id == self.bannedusers[member.guild.id]:
            del self.bannedusers[member.guild.id]
            return
        
        self.log.info(f'A user left {member.guild.name}: {member} ({member.id})')
        
        msg = f':x: {member.mention} (`{member}`) left the server.'
        await self.broadcast_message(msg, member.guild)
    
    async def on_member_ban(self, guild, member):
        self.bannedusers[guild.id] = member.id        
        
        event = await guild.audit_logs(action=discord.AuditLogAction.ban)
        
        self.log.info(f'A user was banned from {guild.name}: {member} ({member.id})')
        self.log.info(f'Reason: {reason}')
        
        msg = f':hammer: {member.mention} (`{member}`) was banned from the server. Reason: {reason}'
        await self.broadcast_message(msg, guild)
    
    async def on_member_unban(self, guild, member):                
        self.log.info(f'A user was unbanned from {guild.name}: {member} ({member.id})')
        
        msg = f':unlock: {member.mention} (`{member}`) was unbanned from the server.'
        await self.broadcast_message(msg, guild)
    
    async def on_member_update(self, before, after):
        #if before.guild.id == 81384788765712384: return
        
        if before.name != after.name:
            self.log.info(f'A user ({before.id}) changed their name from {before} to {after}')
            
            msg = f'User **{before}** changed their name to **{after}** ({after.mention})'
            if before.discriminator != after.discriminator:
                msg += '\n:repeat: *User\'s discriminator changed!*'
            
            await self.broadcast_message(msg, after.guild)
        elif before.avatar_url != after.avatar_url:
            self.log.info(f'{after} ({after.id}) changed their avatar from {before.avatar_url} to {after.avatar_url}')
    
            # This whole thing is hacky. Awaiting d.py update to fix.
            for guild in self.guilds:
                if guild.large:
                    # This is spammy on the console in lage guilds
                    await self.request_offline_members(guild)
                    
                if after in guild.members:  
                    msg = f':frame_photo: User **{before}** changed their avatar from {before.avatar_url} ..'
                    await self.broadcast_message(msg, guild, avatar=True)
                    
                    msg = f'.. to {after.avatar_url} ({before.mention})'
                    await self.broadcast_message(msg, guild, avatar=True)

if __name__ == '__main__':
    bot = JoinBot()
    bot.run(open('bot-token.txt').read().split('\n')[0])
    
