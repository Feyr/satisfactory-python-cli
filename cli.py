#!/usr/bin/env python3
import click
import requests
from requests.auth import HTTPBasicAuth
import json
import warnings
import logging
import configparser
import os

from requests.packages import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

CONFIGFILE=f"{os.environ['HOME']}/.config/satisfactory-cli.ini"

# Suppress only the single InsecureRequestWarning from requests

# abusing a global so we dont have to pass it around every time
SERVER_URL = 'https://localhost:7777/api/v1'  # Replace with your server URL


def authenticate(password):
    """Authenticate with the server and retrieve a Bearer token."""
    response = send_command(None, "PasswordLogin", {"Password": password, "MinimumPrivilegeLevel":"Administrator"})
    if response:
        token_data = response.json()
        return token_data.get("data").get('authenticationToken')

    return None

def shutdown_server(token):
    response = send_command(token, "Shutdown")
    if response:
        click.echo("Server Status:")
        click.echo(json.dumps(response.json(), indent=4))

def save_game(token, name):
    """save game with the provided name"""
    response = send_command(token, "SaveGame", {"SaveName": name})
    if response:
        click.echo("Saved")
    return

def get_server_status(token):
    """Fetch and display the server status."""

    response = send_command(token, "QueryServerState")
    if response:
        click.echo(json.dumps(response.json(), indent=4))
    return

def enumerate_sessions(token):
    response = send_command(token, "EnumerateSessions")
    if response:
        click.echo(json.dumps(response.json(), indent=4))
    return

def read_config():
    config = configparser.ConfigParser()
    config.read(CONFIGFILE)
    if "server" not in config.sections():
        config.add_section("server")

    if "token" not in config.options("server"):
        config['server'] = { "token": ""}

    return config


def save_config(config):
    with open(CONFIGFILE, "w+") as f:
        config.write(f)


def send_command(token, funcName, data=None):
    try:
        headers = {}
        if token:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

        jsonreq = {
                "function": funcName
                }

        if data:
            jsonreq["data"] = data

        response = requests.post(SERVER_URL, headers=headers, verify=False, json=jsonreq)

        if response.status_code >= 200 and response.status_code < 300:
            click.echo(f"Command success: {response.status_code}")
            return response
        else:
            click.echo(f"Failed to get server status: {response.status_code} {response.reason}")
            click.echo(response.text)
            return None
    except requests.exceptions.RequestException as e:
        click.echo(f"An error occurred: {e}")
        raise(e)


@click.command()
@click.option('--host', 'host', default="localhost:7777", help='host:port to connect to')
@click.option('--password', hide_input=True, help='Password for server authentication.')
@click.option('--status', is_flag=True, help='Display the server status.')
@click.option('--save', 'save', help='save game with name')
@click.option('--shutdown', is_flag=True, help='shutdown the server')
@click.option('--enumerate', 'enums', is_flag=True, help='enumerate sessions')
def cli(host, password, status,save, shutdown, enums):
    """CLI tool to authenticate and interact with the Satisfactory Dedicated Server API."""
    config = read_config()
    token = config.get("server", "token")

    if not token:
        password = click.prompt("password", hide_input=True)

        print("token")
        token = authenticate(password)
        config['server']['token'] = token
        save_config(config)

    if host:
        global SERVER_URL
        SERVER_URL = f'https://{host}/api/v1'

    if not token:
        click.echo("Authentication failed. Cannot proceed.")

    if status:
        get_server_status(token)

    if shutdown:
        shutdown_server(token)

    if save:
        save_game(token, save)

    if enums:
        enumerate_sessions(token)



if __name__ == '__main__':
    cli()

