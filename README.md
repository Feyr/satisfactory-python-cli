[Смотреть README на русском](README.ru.md)




Messages from the server, such as status and session information, have been organized.
<p>Currently, only 4 calls are implemented, and it is designed to work on the same machine as the server, or you can modify the source code.

pull welcomes

* cli.py is the pure cli that can be used for scripting
* winCLI-* are text-based interactive UI that look like this:  
![image](https://github.com/user-attachments/assets/610e4706-63f3-44cf-b418-f4d758f2debf)

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
      @click.option('--host', 'host', default="localhost:7777", help='Host:port to connect to') 
     ```
   - Replace localhost with the IP address of your server if it is on another machine. For example:
   ```python
      @click.option('--host', 'host', default="192.168.1.10:7777", help='Host:port to connect to')
   ```

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
---
CLI
---

## Running the Program

1. **Navigate to the Program Directory**: Open a terminal or command prompt and navigate to the directory where the Python script is located.

2. **Execute the Script**: Run the script using the following command:

 ```bash
 python winCLI-EN.py
 ```


## Command-Line Options

When you run the program, you can use the following command-line options:

- **`--host`**: Specify the host and port for connecting to the server. The default is `localhost:7777`.
- **`--password`**: Provide the password for authentication with the server (it will be hidden when typed).
- **`--command`**: Specify a command to execute immediately. Possible commands include:
  - `status`: Get the current server status.
  - `save`: Save the game.
  - `shutdown`: Shut down the server.
  - `sessions`: List available sessions.
  - `options`: Get server options.
- **`--save_name`**: Specify the name to use when saving the game (used with the `save` command).

## Example Usage

Here are a few examples of how to use the program:

1. **Connect to the Server and Show Status**:

 ```bash
 python winCLI-EN.py --host localhost:7777 --password your_password --command status
 ```

2. **Save the Game**:

 ```bash
 python winCLI-EN.py --host localhost:7777 --password your_password --command save --save_name "MySave"
 ```

3. **Shutdown the Server**:

 ```bash
 python winCLI-EN.py --host localhost:7777 --password your_password --command shutdown
 ```

4. **List Sessions**:

 ```bash
 python winCLI-EN.py --host localhost:7777 --password your_password --command sessions
 ```

5. **Get Server Options**:

 ```bash
 python winCLI-EN.py --host localhost:7777 --password your_password --command options
 ```

## Interactive Mode

If you run the script without specifying a command, it will enter an interactive mode where you can select commands from a menu. Here's how to interact in this mode:

1. **Run the Script**:

 ```bash
 python winCLI-EN.py --host localhost:7777 --password your_password
 ```

2. **Select a Command**: After the authentication, the program will display a menu:

```
Select a command:
1. Show server status
2. Save game
3. Shut down server
4. List sessions
5. Show server options
6. Exit
```

3. **Enter the Command Number**: Type the number of the command you want to execute and press Enter.

4. **Follow Prompts**: If additional information is needed (e.g., save name), the program will prompt you to provide it.

5. **Exit the Program**: Choose the "Exit" option from the menu to close the program.

