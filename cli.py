#!/usr/bin/env python3
import click
import requests
from requests.auth import HTTPBasicAuth
import json
import warnings
import logging

from requests.packages import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


# Suppress only the single InsecureRequestWarning from requests

# Configuration for the server
SERVER_URL = 'https://localhost:7777/api/v1'  # Replace with your server URL

def authenticate(password):
    """Authenticate with the server and retrieve a Bearer token."""
    response = requests.post(
        SERVER_URL,
        headers={'Content-Type': 'application/json'},
        verify=False,  # Ignore SSL warnings for self-signed certificates
        json={
            "function": "PasswordLogin",
            "data": {
                "Password" : password,
                "MinimumPrivilegeLevel": "Administrator"
                }
            }

    )
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("data").get('authenticationToken')
    else:
        click.echo(f"Authentication failed: {response.status_code} {response.reason}")
        click.echo(response.text)
        return None

def shutdown_server(token):
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        jsonreq = {
                "function": "Shutdown",
                }

        response = requests.post(SERVER_URL, headers=headers, verify=False, json=jsonreq)
        
        if response.status_code == 200:
            status_data = response.json()
            click.echo("Server Status:")
            click.echo(json.dumps(status_data, indent=4))
        else:
            click.echo(f"Failed to shutdown server: {response.status_code} {response.reason}")
            click.echo(response.text)

    except requests.exceptions.RequestException as e:
        click.echo(f"An error occurred: {e}")

def get_server_status(token):
    """Fetch and display the server status."""
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        jsonreq = {
                "function": "QueryServerState",
                }

        response = requests.post(SERVER_URL, headers=headers, verify=False, json=jsonreq)
        
        if response.status_code == 200:
            status_data = response.json()
            click.echo("Server Status:")
            click.echo(json.dumps(status_data, indent=4))
        else:
            click.echo(f"Failed to get server status: {response.status_code} {response.reason}")
            click.echo(response.text)
    except requests.exceptions.RequestException as e:
        click.echo(f"An error occurred: {e}")

@click.command()
@click.option('--password', prompt=True, hide_input=True, help='Password for server authentication.')
@click.option('--status', is_flag=True, help='Display the server status.')
@click.option('--shutdown', is_flag=True, help='Display the server status.')
def cli(password, status, shutdown):
    """CLI tool to authenticate and interact with the Satisfactory Dedicated Server API."""
    token = authenticate(password)
    
    if not token:
        click.echo("Authentication failed. Cannot proceed.")


    if status:
        get_server_status(token)

    if shutdown:
        shutdown_server(token)

if __name__ == '__main__':
    cli()

