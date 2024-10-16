#!/usr/bin/env python3
import click
import requests
from requests.auth import HTTPBasicAuth
import json
import warnings
import logging
import configparser
import os
import platform  # Import the platform module to check OS type

from requests.packages import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

# Path to the configuration file for Windows
CONFIGFILE = os.path.join(os.environ['APPDATA'], 'satisfactory-cli.ini')

# Global variable for the server URL
SERVER_URL = 'https://localhost:7777/api/v1'  # Default local server


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')


def authenticate(password):
    """Authenticate with the server and retrieve a Bearer token."""
    response = send_command(None, "PasswordLogin", {"Password": password, "MinimumPrivilegeLevel": "Administrator"})
    if response:
        token_data = response.json()
        return token_data.get("data").get('authenticationToken')
    return None

def get_server_options(token):
    """Fetch and display server options."""
    response = send_command(token, "GetServerOptions")
    if response:
        options_data = response.json().get("data", {}).get("serverOptions", {})  # Update this line
        
        if not options_data:
            click.echo("No options found in the server response.")
            return

        click.echo("\nServer Options:\n")
        for key, value in options_data.items():
            click.echo(f"  {key}: {value}")

        click.echo("\nOptions request completed.")
    else:
        click.echo("No response received from the server.")


def shutdown_server(token):
    response = send_command(token, "Shutdown")
    if response:
        click.echo("Server Status:")
        click.echo(json.dumps(response.json(), indent=4))


def save_game(token, name):
    """Save game with the provided name."""
    response = send_command(token, "SaveGame", {"SaveName": name})
    if response:
        click.echo("Game saved.")
    return


def get_server_status(token):
    """Retrieve and display the server status in a formatted way."""
    response = send_command(token, "QueryServerState")
    if response:
        server_state = response.json().get("data", {}).get("serverGameState", {})

        if not server_state:
            click.echo("Failed to retrieve server state.")
            return

        click.echo("\nServer Status:\n")
        click.echo(f"  Active Session: {server_state.get('activeSessionName', 'No active session')}")
        click.echo(f"  Auto-load Session: {server_state.get('autoLoadSessionName', 'Not set')}")
        click.echo(f"  Connected Players: {server_state.get('numConnectedPlayers', 0)} out of {server_state.get('playerLimit', 'unknown')}")
        click.echo(f"  Current Tech Tier: {server_state.get('techTier', 'unknown')}")
        click.echo(f"  Active Schematic: {server_state.get('activeSchematic', 'unknown')}")
        click.echo(f"  Game Phase: {server_state.get('gamePhase', 'None')}")
        click.echo(f"  Game Running: {'Yes' if server_state.get('isGameRunning') else 'No'}")
        click.echo(f"  Game Paused: {'Yes' if server_state.get('isGamePaused') else 'No'}")
        click.echo(f"  Average Tick Rate: {server_state.get('averageTickRate', 'unknown')} FPS")

        total_duration = server_state.get('totalGameDuration', 0)

        # Convert total game time into hours, minutes, and seconds
        hours, remainder = divmod(total_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        click.echo(f"  Total Game Time: {hours}h {minutes}m {seconds}s")

        click.echo("\nStatus request completed.")



def enumerate_sessions(token):
    """Function to enumerate sessions and display them in a readable format."""
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
                    map_options = save.get("mapOptions", "No additional options")
                    play_duration = save.get("playDurationSeconds", 0)
                    save_time = save.get("saveDateTime", "Unknown date")
                    is_modded = "Yes" if save.get("isModdedSave", False) else "No"
                    is_edited = "Yes" if save.get("isEditedSave", False) else "No"
                    is_creative_mode = "Yes" if save.get("isCreativeModeEnabled", False) else "No"

                    # Convert play time into hours, minutes, and seconds
                    hours, remainder = divmod(play_duration, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    click.echo(f"  Save {save_idx + 1}: {save_name}")
                    click.echo(f"    Save Version: {save_version}")
                    click.echo(f"    Build Version: {build_version}")
                    click.echo(f"    Map: {map_name}")
                    click.echo(f"    Map Options: {map_options}")
                    click.echo(f"    Play Time: {hours}h {minutes}m {seconds}s")
                    click.echo(f"    Save Date: {save_time}")
                    click.echo(f"    Modded Save: {is_modded}")
                    click.echo(f"    Edited Save: {is_edited}")
                    click.echo(f"    Creative Mode Enabled: {is_creative_mode}")
            
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
            click.echo(f"Failed to execute command: {response.status_code} {response.reason}")
            click.echo(response.text)
            return None
    except requests.exceptions.RequestException as e:
        click.echo(f"An error occurred: {e}")
        raise e


def display_menu():
    """Display the menu for selecting a command."""
    click.echo("\nChoose a command:")
    click.echo("1. Show server status")
    click.echo("2. Save game")
    click.echo("3. Shutdown server")
    click.echo("4. Enumerate sessions")
    click.echo("5. Show server options")  # New option
    click.echo("6. Exit\n")  # Updated option number


@click.command()
@click.option('--host', 'host', default="localhost:7777", help='Host:port to connect to')
@click.option('--password', hide_input=True, help='Password for server authentication.')
def cli(host, password):
    """CLI tool to authenticate and interact with the Satisfactory Dedicated Server API."""
    config = read_config()
    token = config.get("server", "token")

    if not token:
        # If token is absent, prompt for the password
        password = click.prompt("Password", hide_input=True)

        click.echo("Authenticating...")
        token = authenticate(password)
        if token:
            config['server']['token'] = token
            save_config(config)
        else:
            click.echo("Authentication failed.")
            return

    if host:
        global SERVER_URL
        SERVER_URL = f'https://{host}/api/v1'

    # Menu after authentication
    while True:

        display_menu()
        choice = click.prompt("Enter command number", type=int)

        clear_screen()  # Clear screen before executing the selected command

        if choice == 1:
            get_server_status(token)
        elif choice == 2:
            save_name = click.prompt("Enter name for save")
            save_game(token, save_name)
        elif choice == 3:
            confirm_shutdown = click.confirm("Are you sure you want to shut down the server?", default=False)
            if confirm_shutdown:
                shutdown_server(token)
        elif choice == 4:
            enumerate_sessions(token)
        elif choice == 5:
            get_server_options(token)  # Call the new function
        elif choice == 6:
            click.echo("Exiting the program.")
            break
        else:
            click.echo("Invalid choice, please try again.")


if __name__ == '__main__':
    cli()
