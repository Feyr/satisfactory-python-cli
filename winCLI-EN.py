#!/usr/bin/env python3
import click
import requests
from requests.auth import HTTPBasicAuth
import json
import warnings
import logging
import configparser
import os
import platform

from requests.packages import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

CONFIGFILE = os.path.join(os.environ['APPDATA'], 'satisfactory-cli.ini')

# Global variable for server URL
SERVER_URL = None


def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')


def authenticate(password):
    """Authenticate to the server and obtain a Bearer token."""
    response = send_command(None, "PasswordLogin", {"Password": password, "MinimumPrivilegeLevel": "Administrator"})
    if response:
        token_data = response.json()
        return token_data.get("data").get('authenticationToken')
    return None


def get_server_options(token):
    """Fetch and display server options."""
    response = send_command(token, "GetServerOptions")
    if response:
        options_data = response.json().get("data", {}).get("serverOptions", {})
        if not options_data:
            click.echo("Options not found in the server response.")
            return

        click.echo("\nServer Options:\n")
        for key, value in options_data.items():
            click.echo(f"  {key}: {value}")

        click.echo("\nOptions query completed.")
    else:
        click.echo("No response received from the server.")


def shutdown_server(token):
    response = send_command(token, "Shutdown")
    if response:
        click.echo("Server status:")
        click.echo(json.dumps(response.json(), indent=4))


def save_game(token, name):
    """Save the game with the specified name."""
    response = send_command(token, "SaveGame", {"SaveName": name})
    if response:
        click.echo("Game saved.")
    return


def get_server_status(token):
    """Fetch and display server status."""
    response = send_command(token, "QueryServerState")
    if response:
        server_state = response.json().get("data", {}).get("serverGameState", {})
        if not server_state:
            click.echo("Unable to retrieve server state.")
            return

        click.echo("\nServer Status:\n")
        click.echo(f"  Active session: {server_state.get('activeSessionName', 'No active session')}")
        click.echo(f"  Auto-load session: {server_state.get('autoLoadSessionName', 'Not set')}")
        click.echo(f"  Connected players: {server_state.get('numConnectedPlayers', 0)} of {server_state.get('playerLimit', 'unknown')}")
        click.echo(f"  Current tech tier: {server_state.get('techTier', 'unknown')}")
        click.echo(f"  Active schematic: {server_state.get('activeSchematic', 'unknown')}")
        click.echo(f"  Game phase: {server_state.get('gamePhase', 'No phase')}")
        click.echo(f"  Game running: {'Yes' if server_state.get('isGameRunning') else 'No'}")
        click.echo(f"  Game paused: {'Yes' if server_state.get('isGamePaused') else 'No'}")
        click.echo(f"  Average tick rate: {server_state.get('averageTickRate', 'unknown')} FPS")
        
        total_duration = server_state.get('totalGameDuration', 0)
        hours, remainder = divmod(total_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        click.echo(f"  Total game time: {hours}h {minutes}m {seconds}s")
        click.echo("\nStatus query completed.")


def enumerate_sessions(token):
    """List available sessions."""
    response = send_command(token, "EnumerateSessions")
    if response:
        sessions_data = response.json().get("data", {}).get("sessions", [])
        current_session_index = response.json().get("data", {}).get("currentSessionIndex", None)

        if not sessions_data:
            click.echo("No available sessions.")
            return

        click.echo("Available Sessions:\n")
        for idx, session in enumerate(sessions_data):
            session_name = session.get("sessionName", "Unknown session")
            click.echo(f"Session {idx + 1}: {session_name}")

            save_headers = session.get("saveHeaders", [])
            if not save_headers:
                click.echo("  No saves for this session.")
            else:
                for save_idx, save in enumerate(save_headers):
                    save_name = save.get("saveName", "Unknown save")
                    save_version = save.get("saveVersion", "Unknown version")
                    build_version = save.get("buildVersion", "Unknown version")
                    map_name = save.get("mapName", "Unknown map")
                    play_duration = save.get("playDurationSeconds", 0)
                    save_time = save.get("saveDateTime", "Unknown date")
                    is_modded = "Yes" if save.get("isModdedSave", False) else "No"

                    hours, remainder = divmod(play_duration, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    click.echo(f"  Save {save_idx + 1}: {save_name}")
                    click.echo(f"    Save version: {save_version}")
                    click.echo(f"    Play time: {hours}h {minutes}m {seconds}s")
                    click.echo(f"    Save date: {save_time}")
            
            if idx == current_session_index:
                click.echo(f"  * This is the current active session.")

        click.echo("\nEnumeration completed.")


def read_config():
    config = configparser.ConfigParser()
    config.read(CONFIGFILE)
    if "server" not in config.sections():
        config.add_section("server")

    if "token" not in config.options("server"):
        config['server'] = {"token": ""}

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

        jsonreq = {"function": funcName}

        if data:
            jsonreq["data"] = data

        response = requests.post(SERVER_URL, headers=headers, verify=False, json=jsonreq)

        if response.status_code >= 200 and response.status_code < 300:
            click.echo(f"Command executed successfully: {response.status_code}")
            return response
        else:
            click.echo(f"Failed to execute command: {response.status_code} {response.reason}")
            click.echo(response.text)
            return None
    except requests.exceptions.RequestException as e:
        click.echo(f"An error occurred: {e}")
        raise e


def display_menu():
    """Display menu for command selection."""
    click.echo("\nSelect a command:")
    click.echo("1. Show server status")
    click.echo("2. Save game")
    click.echo("3. Shut down server")
    click.echo("4. List sessions")
    click.echo("5. Show server options")
    click.echo("6. Exit\n")


@click.command()
@click.option('--host', 'host', default="localhost:7777", help='Host:port to connect to')
@click.option('--password', hide_input=True, help='Password for server authentication.')
@click.option('--command', type=click.Choice(['status', 'save', 'shutdown', 'sessions', 'options'], case_sensitive=False), help='Execute a specific command.')
@click.option('--save_name', default=None, help='Save name for the "save" command.')
def cli(host, password, command, save_name):
    """CLI tool for server authentication and interaction with the Satisfactory dedicated server API."""
    global SERVER_URL  # We need to use the global variable
    SERVER_URL = f'https://{host}/api/v1'  # Update the global SERVER_URL variable

    config = read_config()
    token = config.get("server", "token")

    if not token:
        # If no token is present, prompt for password
        password = click.prompt("Password", hide_input=True) if not password else password

        click.echo("Authenticating...")
        token = authenticate(password)
        if token:
            config['server']['token'] = token
            save_config(config)
        else:
            click.echo("Authentication failed.")
            return

    if command:
        # Execute command passed via CLI
        if command == 'status':
            get_server_status(token)
        elif command == 'save':
            if not save_name:
                save_name = click.prompt("Enter a save name")
            save_game(token, save_name)
        elif command == 'shutdown':
            if click.confirm("Are you sure you want to shut down the server?", default=False):
                shutdown_server(token)
        elif command == 'sessions':
            enumerate_sessions(token)
        elif command == 'options':
            get_server_options(token)
    else:
        # Enter interactive menu
        while True:
            display_menu()
            choice = click.prompt("Enter the command number", type=int)

            clear_screen()

            if choice == 1:
                get_server_status(token)
            elif choice == 2:
                save_name = click.prompt("Enter a save name")
                save_game(token, save_name)
            elif choice == 3:
                if click.confirm("Are you sure you want to shut down the server?", default=False):
                    shutdown_server(token)
            elif choice == 4:
                enumerate_sessions(token)
            elif choice == 5:
                get_server_options(token)
            elif choice == 6:
                click.echo("Exiting the program.")
                break
            else:
                click.echo("Invalid choice, please try again.")


if __name__ == '__main__':
    cli()
