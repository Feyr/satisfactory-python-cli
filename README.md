![image](https://github.com/user-attachments/assets/610e4706-63f3-44cf-b418-f4d758f2debf)

![image](https://github.com/user-attachments/assets/07ed177e-bd6b-4b7c-a80b-2fc5e0979721)



Сообщения от сервера в виде статуса и информация о сессии преведены в порядок.
<p>В настоящий момент реализовано только 3 вызова и предназначен для работы на той же машине, что и сервер или вы можете изменить исходники.

Messages from the server, such as status and session information, have been organized.
<p>Currently, only 3 calls are implemented, and it is designed to work on the same machine as the server, or you can modify the source code.

pull welcomes


-------
# Руководство по запуску приложения Python на Windows

Это руководство поможет вам установить и запустить ваше Python-приложение на Windows.

## Шаг 1: Установка Python

1. **Скачивание Python**:
   - Перейдите на [официальный сайт Python](https://www.python.org/downloads/).
   - Скачайте последнюю версию Python для Windows (выберите версию для вашей архитектуры: 32-бит или 64-бит).

2. **Установка Python**:
   - Запустите установщик Python.
   - **Обязательно отметьте** опцию **"Add Python to PATH"**.
   - Нажмите на **"Install Now"** и следуйте инструкциям на экране.

3. **Проверка установки**:
   - Откройте командную строку (нажмите `Win + R`, введите `cmd` и нажмите Enter).
   - Введите команду:
     ```bash
     python --version
     ```
   - Если установка прошла успешно, вы увидите версию Python.

## Шаг 2: Установка зависимостей

1. **Открытие командной строки**:
   - Если вы уже не в командной строке, откройте её.

2. **Установка зависимостей**:
   - Выполните следующую команду для установки необходимых библиотек:
     ```bash
     pip install click requests configparser
     ```

## Шаг 3: Настройка вашего приложения

1. **Настройка URL сервера**:
   - Откройте файл `winCLI-EN.py` или `winCLI-RU.py` в текстовом редакторе.
   - Найдите строку:
     ```python
     SERVER_URL = 'https://localhost:7777/api/v1'
     ```
   - Замените `localhost` на IP-адрес вашего сервера, если он находится на другой машине. Например:
     ```python
     SERVER_URL = 'https://192.168.1.10:7777/api/v1'
     ```

2. **Настройка параметра хоста**:
   - Найдите строку:
     ```python
     @click.option('--host', 'host', default="localhost:7777", help='Хост:порт для подключения')
     ```
   - Измените `localhost` на тот же адрес, если хотите, чтобы он был по умолчанию.

## Шаг 4: Запуск приложения

1. **Запуск программы**:
   - В командной строке перейдите в директорию, где находится ваш файл `winCLI-EN.py` или `winCLI-RU.py`:
     ```bash
     cd путь\к\вашему\проекту
     ```
   - Запустите программу с помощью команды:
     ```bash
     python winCLI-RU.py  # Или winCLI-EN.py
     ```

## Шаг 5: Компиляция программы с помощью PyInstaller

1. **Установка PyInstaller**:
   - В командной строке выполните следующую команду:
     ```bash
     pip install pyinstaller
     ```

2. **Компиляция программы**:
   - Перейдите в директорию с вашим скриптом:
     ```bash
     cd путь\к\вашему\проекту
     ```
   - Выполните команду для компиляции:
     ```bash
     pyinstaller --onefile winCLI-RU.py  # Или winCLI-EN.py
     ```
   - Этот процесс создаст несколько папок, включая `dist`, в которой будет находиться ваш исполняемый файл.

3. **Запуск скомпилированного файла**:
   - Перейдите в папку `dist`:
     ```bash
     cd dist
     ```
   - Запустите скомпилированный файл:
     ```bash
     winCLI-RU.exe  # Или winCLI-EN.exe
     ```

---

# Guide to Running Python Application on Windows

This guide will help you install and run your Python application on Windows.

## Step 1: Install Python

1. **Download Python**:
   - Go to the [official Python website](https://www.python.org/downloads/).
   - Download the latest version of Python for Windows (choose the version for your architecture: 32-bit or 64-bit).

2. **Install Python**:
   - Run the Python installer.
   - **Make sure to check** the option **"Add Python to PATH"**.
   - Click on **"Install Now"** and follow the instructions on the screen.

3. **Verify the Installation**:
   - Open Command Prompt (press `Win + R`, type `cmd`, and press Enter).
   - Type the command:
     ```bash
     python --version
     ```
   - If the installation was successful, you will see the version of Python.

## Step 2: Install Dependencies

1. **Open Command Prompt**:
   - If you are not in the command prompt already, open it.

2. **Install Dependencies**:
   - Run the following command to install the required libraries:
     ```bash
     pip install click requests configparser
     ```

## Step 3: Configure Your Application

1. **Set Server URL**:
   - Open the `winCLI-EN.py` or `winCLI-RU.py` file in a text editor.
   - Find the line:
     ```python
     SERVER_URL = 'https://localhost:7777/api/v1'
     ```
   - Replace `localhost` with the IP address of your server if it is on a different machine. For example:
     ```python
     SERVER_URL = 'https://192.168.1.10:7777/api/v1'
     ```

2. **Set Host Parameter**:
   - Find the line:
     ```python
     @click.option('--host', 'host', default="localhost:7777", help='Host:port for connection')
     ```
   - Change `localhost` to the same address if you want it to be the default.

## Step 4: Run the Application

1. **Run the Program**:
   - In the command prompt, navigate to the directory where your `winCLI-EN.py` or `winCLI-RU.py` file is located:
     ```bash
     cd path\to\your\project
     ```
   - Run the program using the command:
     ```bash
     python winCLI-RU.py  # Or winCLI-EN.py
     ```

## Step 5: Compile the Program Using PyInstaller

1. **Install PyInstaller**:
   - In the command prompt, run the following command:
     ```bash
     pip install pyinstaller
     ```

2. **Compile the Program**:
   - Navigate to the directory with your script:
     ```bash
     cd path\to\your\project
     ```
   - Run the command to compile:
     ```bash
     pyinstaller --onefile winCLI-RU.py  # Or winCLI-EN.py
     ```
   - This process will create several folders, including `dist`, where your executable file will be located.

3. **Run the Compiled File**:
   - Navigate to the `dist` folder:
     ```bash
     cd dist
     ```
   - Run the compiled file:
     ```bash
     winCLI-RU.exe  # Or winCLI-EN.exe
     ```
