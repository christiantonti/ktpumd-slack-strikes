import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
import botocore
from urllib import parse
import re

def lambda_handler(event, context):
    response = {}
    role_perms = {
        'admin':('get', 'add', 'remove', 'register', 'help'),
        'membership':('get', 'add', 'remove', 'help'),
        'brother':('get', 'help'),
        'pledge':('get', 'help'),
    }
    valid_cmds = ('get', 'add', 'remove', 'register', 'help')
    dynamodb = boto3.resource('dynamodb')
    client = boto3.client('dynamodb')
    table = dynamodb.Table('ktpStrikes')
    args = parse_body(event.get('body'))
    print(f'ARGS: {args}')
    role = get_role(args.get('user_id'), table)
    print(f'ROLE: {role}')
    data = parse.unquote(args.get('text')).split('+')
    argc = len(data)
    # data = [x.lower() for x in data]
    cmd = data[0].lower()
    if argc < 1 or cmd not in valid_cmds: return invalid_msg()
    if cmd not in role_perms.get(role): return create_msg("Insufficient permissions for role: {}.".format(role), False)
    if cmd == 'get':
        uid = get_uid(data)
        print(f'UID: {uid}')
        if uid:
            if uid == 'all':
                strikes = get_all_strikes(table)
                print(strikes)
                msg = ':x: Strikes for all users:\n'
                for n, s in strikes:
                    msg += f'{n}: {s}\n'
                return create_msg(msg)
            strikes = get_strikes(uid, table)
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
            return modify_strikes(uid, amt, table)
        else:
            return create_msg("*Usage:* `/strikes add [user] (amount)`", False)
    elif cmd == "remove":
        uid = get_uid(data)
        if uid:
            amt = -1 if argc < 3 else -1*int(data[2])
            return modify_strikes(uid, amt, table)
        else:
            return create_msg("*Usage:* `/strikes remove [user] (amount)`", False)
    elif cmd == "register":
        uid = get_uid(data)
        if uid and argc == 4:
            try:
                table.put_item(
                    Item={
                        'user_id':uid,
                        'strikes':0,
                        'firstname':data[2],
                        'lastname':data[3]
                    })
                return create_msg('Successfully registered %s' % data[1])
            except botocore.exceptions.ClientError as error:
                print('ERROR' + error)
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
        
def get_role(uid, table):
    try:
        r = table.get_item(
            Key={
                'user_id':uid
            })
        role = r['Item']['role']
        return role
    except:
        return None
        
def get_strikes(uid, table):
    try:
        r = table.get_item(
            Key={
                'user_id':uid
            })
        print(r)
        strikes = int(r['Item']['strikes'])
        return strikes
    except:
        return None
        
def get_all_strikes(table):
    print('called get all')
    try:
        r = table.scan(FilterExpression=Attr('strikes').exists())
        retlist = []
        for item in r['Items']:
            retlist.append((f"{item['firstname']} {item['lastname']}", int(item['strikes'])))
        return sorted(retlist, key=lambda i: i[1], reverse=True)
    except:
        return None
        
def modify_strikes(uid, amt, table):
    strikes = get_strikes(uid, table)
    if strikes != None:
        strikes += amt
        if strikes < 0: return create_msg("Would result in negative strikes!", False)
        if update_strikes(uid, strikes, table):
            return create_msg('<@%s> now has %d strikes' % (uid, strikes))
        else:
            return create_msg("Error adding strikes")
    else:
        return create_msg("Error getting strikes")
    
def update_strikes(uid, strikes, table):
    try:
        table.update_item(
            Key={
                'user_id': uid,
            },
            UpdateExpression='SET strikes = :val1',
            ExpressionAttributeValues={
                ':val1': strikes
            })
        return True
    except:
        return False
        
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