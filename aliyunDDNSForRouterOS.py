#!/usr/bin/env python
# coding=utf-8
import os
import json
import requests
from requests.auth import HTTPBasicAuth
import time
from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest

def log_message(message):
    """Log messages with timestamp."""
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def get_acs_client(aliyun_config):
    return AcsClient(
        aliyun_config['Access_Key_ID'],
        aliyun_config['Access_Key_Secret'],
        aliyun_config['region_id']
    )

def get_dns_record(client, domain_name, sub_domain, type_key_word):
    request = DescribeDomainRecordsRequest()
    request.set_accept_format('json')
    request.set_DomainName(domain_name)
    request.set_RRKeyWord(sub_domain)
    request.set_TypeKeyWord(type_key_word)

    response = client.do_action_with_exception(request)
    return json.loads(response)

def update_dns_record(client, record_id, rr, record_type, value, line, ttl):
    request = UpdateDomainRecordRequest()
    request.set_accept_format('json')
    request.set_RecordId(record_id)
    request.set_RR(rr)
    request.set_Type(record_type)
    request.set_Value(value)
    request.set_Line(line)
    request.set_TTL(ttl)

    response = client.do_action_with_exception(request)
    print(f"Updated DNS record: {response}")

def add_dns_record(client, domain_name, rr, record_type, value, line, ttl):
    request = AddDomainRecordRequest()
    request.set_accept_format('json')
    request.set_DomainName(domain_name)
    request.set_RR(rr)
    request.set_Type(record_type)
    request.set_Value(value)
    request.set_Line(line)
    request.set_TTL(ttl)

    response = client.do_action_with_exception(request)
    print(f"Added DNS record: {response}")

def get_routeros_interface_address(routerOS_config, record_type, routerOS_Interface):
    routerOS_ipv4_request_url = routerOS_config['API_URL'] + '/rest/ip/address'
    routerOS_ipv6_request_url = routerOS_config['API_URL'] + '/rest/ipv6/address'
    routerOS_auth = HTTPBasicAuth(routerOS_config['User_Name'], routerOS_config['Password'])

    request_url = ''
    if record_type == 'A':
        request_url = routerOS_ipv4_request_url
    elif record_type == 'AAAA':
        request_url = routerOS_ipv6_request_url
    else:
        print(f"Error Record Type: {record_type}, must be A or AAAA !!")
        exit(1)

    try:
        response = requests.get(request_url, auth=routerOS_auth, timeout=10)
        if response.status_code == 200:
            # 解析响应数据
            addresses = response.json()
            for address in addresses:
                if address.get("interface") == routerOS_Interface:
                    # 提取并返回 IP 地址
                    return address.get("address").split("/")[0]
        else:
            print(f"Error accessing RouterOS API: {response.status_code}")
            exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

def handle_record(domain_config, routerOS_config, aliyun_config):
    client = get_acs_client(aliyun_config)
    domain_name = domain_config['Domain_Name']
    subDomain_name = domain_config['Sub_Domain_Name']

    for record in domain_config['Record']:
        record_type = record['Type']
        record_line = record['Line']
        routerOS_Interface = record['RouterOS_Interface']
        address = get_routeros_interface_address(routerOS_config=routerOS_config, record_type=record_type, routerOS_Interface=routerOS_Interface)
        remote_record = get_dns_record(client=client, domain_name=domain_name, sub_domain=subDomain_name, type_key_word=record_type)
        remote_records = remote_record['DomainRecords']['Record']
        # 检查远端记录是否存在
        record_found = False
        for remote_record_item in remote_records:
            if remote_record_item['Type'] == record_type and remote_record_item['Line'] == record_line:
                record_found = True
                if remote_record_item['Value'] != address:
                    print(f"Record {subDomain_name}.{domain_name}({record_line}) is set to {address}")
                    update_dns_record(client=client, record_id=remote_record_item['RecordId'], rr=subDomain_name, record_type=record_type, value=address, line=record_line, ttl=record['TTL'])
                else:
                    print(f"Record {subDomain_name}.{domain_name}({record_line}) is already set to {address}, no update needed")
        
        if not record_found:
            print(f"Record {subDomain_name}.{domain_name}({record_line}) is add to {address}")
            add_dns_record(client=client, domain_name=domain_name, rr=subDomain_name, record_type=record_type, value=address, line=record_line, ttl=record['TTL'])

def read_config_file():
    config_file_path = 'config.json'
    if os.path.exists(config_file_path):
        with open(config_file_path) as config_file:
            try:
                json_config_object = json.load(config_file)
                return json_config_object
            except json.JSONDecodeError as e:
                log_message(f"JSON decode error in config file: {e}")
                return None
            except Exception as e:
                log_message(f"Error reading config file: {e}")
                return None
    else:
        log_message("Config file not exist")
        return None

def __main__():
    config_file = read_config_file()
    if not config_file:
        return

    routerOS_config = config_file['RouterOS']
    aliyun_config = config_file['AliYun']
    update_interval = config_file.get('update_interval', 300)  # Default to 5 minutes

    while True:
        for domain_config in config_file['Domains']:
            handle_record(domain_config, routerOS_config, aliyun_config)
        
        log_message("Sleeping for next update cycle.")
        time.sleep(update_interval)

__main__()
