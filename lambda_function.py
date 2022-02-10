import json
from urllib import parse
import re
from db_utils import Database

def lambda_handler(event, context):
    # permissions for each role
    role_perms = {
        'admin':('get', 'all', 'add', 'remove', 'register', 'help'),
        'membership':('get', 'all', 'add', 'remove', 'help'),
        'brother':('get', 'all', 'help'),
        'pledge':('get', 'help'),
    }
    # currently supported commands
    valid_cmds = ('get', 'add', 'remove', 'register', 'help')

    # init dynamodb Table
    db = Database('ktpStrikes')

    # parse GET string into arguments
    print(f'EVENT: {event}')
    args = parse_body(event.get('body'))
    print(f'ARGS: {args}')

    # fetch requestor role
    requestor = args.get('user_id')
    role = db.get_role(requestor)
    print(f'ROLE: {role}')

    # unquote URL string and get message data
    data = parse.unquote(args.get('text')).split('+')
    argc = len(data)
    # data = [x.lower() for x in data]

    cmd = data[0].lower()
    # check for valid commands and role permissions
    if argc < 1 or cmd not in valid_cmds: return invalid_msg()
    if cmd not in role_perms.get(role): return create_msg("Insufficient permissions for role: {}.".format(role), False)
    # begin command switch
    print(f'DATA: {data}')
    if cmd == 'get':
        uid = get_uid(data)
        print(f'UID: {uid}')
        if uid:
            if uid == 'all':
                strikes = db.get_all_strikes()
                msg = ':x: Strikes for all users:\n'
                for n, s in strikes:
                    msg += f'{n}: {s}\n'
                return create_msg(msg)
            strikes = db.get_strikes(uid)
            if strikes != None:
                return create_msg('%s has %d strikes' % (data[1],strikes))
            else:
                return create_msg("Error fetching strikes")
        else:
            return create_msg("*Usage:* `/strikes get [user]`", False)
    elif cmd == "add":
        uid = get_uid(data)
        if uid:
            amt = 1 if argc < 3 else int(data[2])
            return modify_strikes(uid, amt, db)
        else:
            return create_msg("*Usage:* `/strikes add [user] (amount)`", False)
    elif cmd == "remove":
        uid = get_uid(data)
        if uid:
            amt = -1 if argc < 3 else -1*int(data[2])
            return modify_strikes(uid, amt, db)
        else:
            return create_msg("*Usage:* `/strikes remove [user] (amount)`", False)
    elif cmd == "register":
        uid = get_uid(data)
        if uid and argc == 4:
            if db.register_user(uid, data[2], data[3]):
                return create_msg('Successfully registered %s' % data[1])
            else:
                return create_msg("Error registering user")
        else:
            return create_msg("*Usage:* `/strikes register [user] [firstname] [lastname]`", False)
    elif cmd == "help":
        return create_msg("Hi there! :wave:\nThis slash command is used to help keep track of strikes for the current pledge class.\nHere is a list of valid commands:\n - `/strikes get [user]` gets the current strikes of a given user\n - `/strikes add [user] (amount)` increases a user's strikes\n - `/strikes remove [user] (amount)` decreases a user's strikes\n - `/strikes register [user] [firstname] [lastname]` registers a new user (this must be done before getting/adding/removing any strikes for that user)\n - `/strikes help` will show you this message again!\n Note that arguments in [brackets] are *required*; those in (parentheses) are _optional_.\nRemember that successful commands will be visible to the _entire_ channel!", False)
    else:
       return invalid_msg()

def parse_body(body):
    ret = {}
    for x in body.split('&'):
        y = x.split('=')
        ret[y[0]] = y[1]
    return ret
    
def get_uid(data):
    if len(data) >= 2:
        seq = data[1]
        # check for a "get all"
        if seq.lower() == 'all':
            return 'all'
        idsrch = re.search('<@(\w*)\|.*>', seq)
        if idsrch:
            uid = idsrch.group(1)
            return uid
    return None
        
def modify_strikes(uid, amt, db):
    strikes = db.get_strikes(uid)
    if strikes != None:
        strikes += amt
        if strikes < 0: return create_msg("Would result in negative strikes!", False)
        if db.update_strikes(uid, strikes):
            return create_msg('<@%s> now has %d strikes' % (uid, strikes))
        else:
            return create_msg("Error adding strikes")
    else:
        return create_msg("Error getting strikes")
        
def invalid_msg():
    return create_msg("*Invalid Command!* To see available commands, type `/strikes help`", False)
        
def create_msg(msg, visible=True):
    return {
        'statusCode': 200,
        'body': json.dumps({
            'text':msg,
            'response_type': 'in_channel' if visible else 'ephemeral'
        }),
    }