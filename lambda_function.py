# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import boto3
import uuid

thingName = str(uuid.uuid4())

def lambda_handler(event, context):

    macAddr = event['body']['macaddr']

    iot = boto3.client('iot')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('devices')

    macaddrCheck = table.get_item(
        Key={
            'macaddr': macAddr
        }
    )

    if 'Item' in macaddrCheck:
        print("macaddrCheck output: ", macaddrCheck['ResponseMetadata'])
        return { "message": "MAC address already exists. New device not created." }
    else:
        print("macaddrCheck output: ", macaddrCheck['ResponseMetadata'])
        createDevice = iot.create_thing(thingName=thingName,
                                        attributePayload={
                                            'attributes': {
                                                'string': 'string'
                                            }
                                        }
                                        )
        print("createDevice output: ", createDevice['ResponseMetadata'])

        insertDevice = table.put_item(
            Item={
                'macaddr': macAddr,
                'deviceid': createDevice['thingName'],
            }
        )
        print("insertDevice output: ", insertDevice['ResponseMetadata'])

    createCert = iot.create_keys_and_certificate(
        setAsActive=True
    )
    print("createCert output: ", createCert['ResponseMetadata'])

    attachCert = iot.attach_thing_principal(
        thingName= createDevice['thingName'],
        principal= createCert['certificateArn']
    )
    print("attachCert output: ", attachCert['ResponseMetadata'])

    insertCert = table.put_item(
        Item={
            'macaddr': macAddr,
            'deviceid': createDevice['thingName'],
            'certificatePem': createCert['certificatePem'],
            'PublicKey': createCert['keyPair']['PublicKey'],
            'PrivateKey': createCert['keyPair']['PrivateKey'],
        }
    )
    print("insertCert output: ", insertCert['ResponseMetadata'])

    return {"message": "Device created."}