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

# Путь к конфигурационному файлу для Windows
CONFIGFILE = os.path.join(os.environ['APPDATA'], 'satisfactory-cli.ini')

# Глобальная переменная для URL сервера
SERVER_URL = 'https://localhost:7777/api/v1'  # По умолчанию локальный сервер


def authenticate(password):
    """Authenticate with the server and retrieve a Bearer token."""
    response = send_command(None, "PasswordLogin", {"Password": password, "MinimumPrivilegeLevel": "Administrator"})
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
    """Save game with the provided name."""
    response = send_command(token, "SaveGame", {"SaveName": name})
    if response:
        click.echo("Game saved.")
    return


def get_server_status(token):
    """Fetch and display the server status."""
    response = send_command(token, "QueryServerState")
    if response:
        click.echo(json.dumps(response.json(), indent=4))
    return


def enumerate_sessions(token):
    """Функция для перечисления сессий и отображения их в удобочитаемом виде"""
    response = send_command(token, "EnumerateSessions")
    if response:
        sessions_data = response.json().get("data", {}).get("sessions", [])
        current_session_index = response.json().get("data", {}).get("currentSessionIndex", None)

        if not sessions_data:
            click.echo("Нет доступных сессий.")
            return

        click.echo("Доступные сессии:\n")
        for idx, session in enumerate(sessions_data):
            session_name = session.get("sessionName", "Неизвестная сессия")
            click.echo(f"Сессия {idx + 1}: {session_name}")

            save_headers = session.get("saveHeaders", [])
            if not save_headers:
                click.echo("  Нет сохранений для этой сессии.")
            else:
                for save_idx, save in enumerate(save_headers):
                    save_name = save.get("saveName", "Неизвестное сохранение")
                    play_duration = save.get("playDurationSeconds", 0)
                    save_time = save.get("saveDateTime", "Неизвестная дата")
                    is_modded = "Да" if save.get("isModdedSave", False) else "Нет"
                    build_version = save.get("buildVersion", "Неизвестная версия")
                    
                    # Преобразование времени игры в часы, минуты и секунды
                    hours, remainder = divmod(play_duration, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    click.echo(f"  Сохранение {save_idx + 1}: {save_name}")
                    click.echo(f"    Дата сохранения: {save_time}")
                    click.echo(f"    Время игры: {hours}ч {minutes}м {seconds}с")
                    click.echo(f"    Версия игры: {build_version}")
                    click.echo(f"    Модифицированное сохранение: {is_modded}")
            
            if idx == current_session_index:
                click.echo(f"  * Это текущая активная сессия")

        click.echo("\nПеречисление завершено.")



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
    """Отображение меню для выбора команды"""
    click.echo("\nВыберите команду:")
    click.echo("1. Показать статус сервера")
    click.echo("2. Сохранить игру")
    click.echo("3. Выключить сервер")
    click.echo("4. Перечислить сессии")
    click.echo("5. Выйти\n")


@click.command()
@click.option('--host', 'host', default="localhost:7777", help='Host:port to connect to')
@click.option('--password', hide_input=True, help='Password for server authentication.')
def cli(host, password):
    """CLI tool to authenticate and interact with the Satisfactory Dedicated Server API."""
    config = read_config()
    token = config.get("server", "token")

    if not token:
        # Если токен отсутствует, запрашиваем пароль
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

    # Меню после аутентификации
    while True:
        display_menu()
        choice = click.prompt("Введите номер команды", type=int)

        if choice == 1:
            get_server_status(token)
        elif choice == 2:
            save_name = click.prompt("Введите имя для сохранения")
            save_game(token, save_name)
        elif choice == 3:
            confirm_shutdown = click.confirm("Вы уверены, что хотите выключить сервер?", default=False)
            if confirm_shutdown:
                shutdown_server(token)
        elif choice == 4:
            enumerate_sessions(token)
        elif choice == 5:
            click.echo("Выход из программы.")
            break
        else:
            click.echo("Неверный выбор, попробуйте снова.")


if __name__ == '__main__':
    cli()
