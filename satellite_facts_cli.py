import requests
import json
import argparse
import yaml
import os
import sys

def fetch_resource_facts(resource_type, args):
    # Suppress InsecureRequestWarning
    requests.packages.urllib3.disable_warnings()

    if args.config:
        config = args.config
        print(config)
        if not os.path.isfile(config):
            raise FileNotFoundError(f"Configuration file '{config}' not found.")
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)

        satellite  = config_data['satellite']  
        username   = config_data['username']
        password   = config_data['password']
        verify_ssl = not config_data.get('disable_ssl', True)
    else:
        satellite  = args.satellite
        username   = args.username
        password   = args.password
        verify_ssl = args.disable_ssl
        print(password)

    resource_facts = get_resource_facts(satellite, username, password, verify_ssl, resource_type)
    return json.dumps(resource_facts, indent=2)

def get_resource_facts(server, username, password, verify_ssl, resource_type):
    
    resources = get_json(f"https://{server}/api/v2/{resource_type}",username, password, verify_ssl)["results"]
    resource_facts = []
    for resource in resources:
        resource_id = resource['id']
        resource_fact = get_json(f"https://{server}/api/v2/{resource_type}/{resource_id}", username,password, verify_ssl)
        resource_facts.append(resource_fact)
    return resource_facts

def get_json(url, username, password, verify_ssl):
        r = requests.get(url, auth=(username, password), verify=verify_ssl)
        return r.json()

def parse_arguments():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Fetch satellite facts from Red Hat Satellite and convert them to YAML')
    parser.add_argument('hostgroups',  help="This flag will collect all of the hostgroup facts")
    parser.add_argument('subnets',     help="This flag will collect all of the subnet facts")  
    if 'subnets' in sys.argv:
        parser = argparse.ArgumentParser(description='Add the facts neeed to execute the scrapping')
        parser.add_argument('subnets')
        # Add required options
        required_group = parser.add_argument_group('required arguments')
        required_group.add_argument('-s', '--satellite',  help='Satellite server URL')
        required_group.add_argument('-u', '--username',   help='Username for the Satellite server')
        required_group.add_argument('-p', '--password',   help='Password for the Satellite server')

        required_group1 = parser.add_argument_group('Configuration file')
        required_group1.add_argument('-c', '--config', help='YAML configuration file', default=False)

        parser.add_argument('--disable-ssl', action='store_false', help='Disable SSL certificate verification') 
    if 'hostgroups' in sys.argv:
        parser = argparse.ArgumentParser(description='Add the facts neeed to execute the scrapping')
        parser.add_argument('hostgroups')
        # Add required options
        required_group = parser.add_argument_group('required arguments')
        required_group.add_argument('-s', '--satellite',  help='Satellite server URL')
        required_group.add_argument('-u', '--username',   help='Username for the Satellite server')
        required_group.add_argument('-p', '--password',   help='Password for the Satellite server')

        required_group1 = parser.add_argument_group('Configuration file')
        required_group1.add_argument('-c', '--config', help='YAML configuration file', default=False)

        parser.add_argument('--disable-ssl', action='store_false', help='Disable SSL certificate verification') 

    args = parser.parse_args()
    if not args.config and args.satellite:
        if not args.username or not args.password:
            parser.error('-u/--username and -p/--password are required when using -s/--satellite')

    return args
    return args

if __name__ == "__main__":
    try:
        args = parse_arguments()
        if 'subnets' in sys.argv:
            result = fetch_resource_facts('subnets', args)
        if 'hostgroups' in sys.argv:
            result = fetch_resource_facts('hostgroups', args)
        print(result)
        
    except FileNotFoundError as e:
        print(str(e), end="!!!")
