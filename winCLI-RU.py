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

# Глобальная переменная для URL сервера
SERVER_URL = None


def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')


def authenticate(password):
    """Аутентификация на сервере и получение токена Bearer."""
    response = send_command(None, "PasswordLogin", {"Password": password, "MinimumPrivilegeLevel": "Administrator"})
    if response:
        token_data = response.json()
        return token_data.get("data").get('authenticationToken')
    return None


def get_server_options(token):
    """Получить и отобразить параметры сервера."""
    response = send_command(token, "GetServerOptions")
    if response:
        options_data = response.json().get("data", {}).get("serverOptions", {})
        if not options_data:
            click.echo("Параметры не найдены в ответе сервера.")
            return

        click.echo("\nПараметры сервера:\n")
        for key, value in options_data.items():
            click.echo(f"  {key}: {value}")

        click.echo("\nЗапрос параметров завершен.")
    else:
        click.echo("Ответ от сервера не получен.")


def shutdown_server(token):
    response = send_command(token, "Shutdown")
    if response:
        click.echo("Статус сервера:")
        click.echo(json.dumps(response.json(), indent=4))


def save_game(token, name):
    """Сохранить игру с заданным именем."""
    response = send_command(token, "SaveGame", {"SaveName": name})
    if response:
        click.echo("Игра сохранена.")
    return


def get_server_status(token):
    """Получить и отобразить статус сервера."""
    response = send_command(token, "QueryServerState")
    if response:
        server_state = response.json().get("data", {}).get("serverGameState", {})
        if not server_state:
            click.echo("Не удалось получить состояние сервера.")
            return

        click.echo("\nСтатус сервера:\n")
        click.echo(f"  Активная сессия: {server_state.get('activeSessionName', 'Нет активной сессии')}")
        click.echo(f"  Сессия для автозагрузки: {server_state.get('autoLoadSessionName', 'Не установлена')}")
        click.echo(f"  Подключенные игроки: {server_state.get('numConnectedPlayers', 0)} из {server_state.get('playerLimit', 'неизвестно')}")
        click.echo(f"  Текущий техуровень: {server_state.get('techTier', 'неизвестно')}")
        click.echo(f"  Активная схема: {server_state.get('activeSchematic', 'неизвестно')}")
        click.echo(f"  Фаза игры: {server_state.get('gamePhase', 'Нет фазы')}")
        click.echo(f"  Игра запущена: {'Да' if server_state.get('isGameRunning') else 'Нет'}")
        click.echo(f"  Игра на паузе: {'Да' if server_state.get('isGamePaused') else 'Нет'}")
        click.echo(f"  Средняя частота кадров: {server_state.get('averageTickRate', 'неизвестно')} FPS")
        
        total_duration = server_state.get('totalGameDuration', 0)
        hours, remainder = divmod(total_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        click.echo(f"  Общее время игры: {hours}ч {minutes}м {seconds}с")
        click.echo("\nЗапрос статуса завершен.")


def enumerate_sessions(token):
    """Перечислить сессии."""
    response = send_command(token, "EnumerateSessions")
    if response:
        sessions_data = response.json().get("data", {}).get("sessions", [])
        current_session_index = response.json().get("data", {}).get("currentSessionIndex", None)

        if not sessions_data:
            click.echo("Доступных сессий нет.")
            return

        click.echo("Доступные сессии:\n")
        for idx, session in enumerate(sessions_data):
            session_name = session.get("sessionName", "Неизвестная сессия")
            click.echo(f"Сессия {idx + 1}: {session_name}")

            save_headers = session.get("saveHeaders", [])
            if not save_headers:
                click.echo("  Сохранений для этой сессии нет.")
            else:
                for save_idx, save in enumerate(save_headers):
                    save_name = save.get("saveName", "Неизвестное сохранение")
                    save_version = save.get("saveVersion", "Неизвестная версия")
                    build_version = save.get("buildVersion", "Неизвестная версия")
                    map_name = save.get("mapName", "Неизвестная карта")
                    play_duration = save.get("playDurationSeconds", 0)
                    save_time = save.get("saveDateTime", "Неизвестная дата")
                    is_modded = "Да" if save.get("isModdedSave", False) else "Нет"

                    hours, remainder = divmod(play_duration, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    click.echo(f"  Сохранение {save_idx + 1}: {save_name}")
                    click.echo(f"    Версия сохранения: {save_version}")
                    click.echo(f"    Время игры: {hours}ч {minutes}м {seconds}с")
                    click.echo(f"    Дата сохранения: {save_time}")
            
            if idx == current_session_index:
                click.echo(f"  * Это текущая активная сессия.")

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

        jsonreq = {"function": funcName}

        if data:
            jsonreq["data"] = data

        response = requests.post(SERVER_URL, headers=headers, verify=False, json=jsonreq)

        if response.status_code >= 200 and response.status_code < 300:
            click.echo(f"Команда успешно выполнена: {response.status_code}")
            return response
        else:
            click.echo(f"Не удалось выполнить команду: {response.status_code} {response.reason}")
            click.echo(response.text)
            return None
    except requests.exceptions.RequestException as e:
        click.echo(f"Произошла ошибка: {e}")
        raise e


def display_menu():
    """Отобразить меню для выбора команды."""
    click.echo("\nВыберите команду:")
    click.echo("1. Показать статус сервера")
    click.echo("2. Сохранить игру")
    click.echo("3. Выключить сервер")
    click.echo("4. Перечислить сессии")
    click.echo("5. Показать параметры сервера")
    click.echo("6. Выйти\n")


@click.command()
@click.option('--host', 'host', default="localhost:7777", help='Хост:порт для подключения')
@click.option('--password', hide_input=True, help='Пароль для аутентификации на сервере.')
@click.option('--command', type=click.Choice(['status', 'save', 'shutdown', 'sessions', 'options'], case_sensitive=False), help='Выполнить указанную команду.')
@click.option('--save_name', default=None, help='Имя сохранения для команды "save".')
def cli(host, password, command, save_name):
    """CLI-инструмент для аутентификации и взаимодействия с API выделенного сервера Satisfactory."""
    global SERVER_URL  # Нужно использовать глобальную переменную
    SERVER_URL = f'https://{host}/api/v1'  # Обновляем глобальную переменную SERVER_URL

    config = read_config()
    token = config.get("server", "token")

    if not token:
        # Если токена нет, запросить пароль
        password = click.prompt("Пароль", hide_input=True) if not password else password

        click.echo("Аутентификация...")
        token = authenticate(password)
        if token:
            config['server']['token'] = token
            save_config(config)
        else:
            click.echo("Аутентификация не удалась.")
            return

    if command:
        # Выполнение команды, переданной через CLI
        if command == 'status':
            get_server_status(token)
        elif command == 'save':
            if not save_name:
                save_name = click.prompt("Введите имя для сохранения")
            save_game(token, save_name)
        elif command == 'shutdown':
            if click.confirm("Вы уверены, что хотите выключить сервер?", default=False):
                shutdown_server(token)
        elif command == 'sessions':
            enumerate_sessions(token)
        elif command == 'options':
            get_server_options(token)
    else:
        # Переход к интерактивному меню
        while True:
            display_menu()
            choice = click.prompt("Введите номер команды", type=int)

            clear_screen()

            if choice == 1:
                get_server_status(token)
            elif choice == 2:
                save_name = click.prompt("Введите имя для сохранения")
                save_game(token, save_name)
            elif choice == 3:
                if click.confirm("Вы уверены, что хотите выключить сервер?", default=False):
                    shutdown_server(token)
            elif choice == 4:
                enumerate_sessions(token)
            elif choice == 5:
                get_server_options(token)
            elif choice == 6:
                click.echo("Выход из программы.")
                break
            else:
                click.echo("Неверный выбор, попробуйте снова.")



if __name__ == '__main__':
    cli()
