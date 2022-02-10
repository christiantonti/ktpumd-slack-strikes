# File for handling database interactions
import boto3
from boto3.dynamodb.conditions import Key, Attr
import botocore

class Database:
    def __init__(self, table_name):
        dynamodb = boto3.resource('dynamodb')
        # client = boto3.client('dynamodb')
        self.table = dynamodb.Table(table_name)

    # gets the role for a given uid
    def get_role(self, uid):
        try:
            r = self.table.get_item(
                Key={
                    'user_id':uid
                })
            role = r['Item']['role']
            return role
        except Exception as e:
            print(f'Error fetching role for UID {uid}: {repr(e)}')
            return None

    # gets the current strikes for a given uid
    def get_strikes(self, uid):
        try:
            r = self.table.get_item(
                Key={
                    'user_id':uid
                })
            strikes = int(r['Item']['strikes'])
            return strikes
        except Exception as e:
            print(f'Error fetching strikes for UID {uid}: {repr(e)}')
            return None

    # gets all current strikes stored in the table, descending
    def get_all_strikes(self):
        try:
            r = self.table.scan(FilterExpression=Attr('strikes').exists())
            retlist = []
            for item in r['Items']:
                retlist.append((f"{item['firstname']} {item['lastname']}", int(item['strikes'])))
            return sorted(retlist, key=lambda i: i[1], reverse=True)
        except Exception as e:
            print(f'Error fetching all strikes: {repr(e)}')
            return None

    # updates the current strikes for a given uid
    def update_strikes(self, uid, strikes):
        try:
            self.table.update_item(
                Key={
                    'user_id': uid,
                },
                UpdateExpression='SET strikes = :val1',
                ExpressionAttributeValues={
                    ':val1': strikes
                })
            return True
        except Exception as e:
            print(f'Error updating strikes for {uid}: {repr(e)}')
            return False

    # registers a user into the table
    def register_user(self, uid, firstname, lastname):
        try:
            self.table.put_item(
                Item={
                    'user_id':uid,
                    'strikes':0,
                    'firstname':firstname,
                    'lastname':lastname
                })
            return True
        except Exception as e:
            print(f'Error registering user {uid}: {repr(e)}')
            return False