import os
import subprocess
import json
from pprint import pprint
import sys
import shutil

environment = os.environ.copy()
config = {}
nvenv_name = ""
local_bin_folder = ""
load_file = ""
hostname = ""
username = ""

# INFO Entry point
def main(config_file="./config.json", new=False, delete=False):
    print("[ Welcome to NixVenv, the *nix compatible virtual shell environment manager ]")
    global environment, config, cmds, local_bin_folder, load_file, nvenv_name, shell, hostname, username
    p = subprocess.run("whoami", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    username = p.stdout.decode('utf-8').strip()
    p = subprocess.run("hostname", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    hostname = p.stdout.decode('utf-8').strip()
    p = subprocess.run("echo $SHELL", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    shell = p.stdout.decode('utf-8').strip()
    print(shell)
    cmds = 'echo "[ Setting environment variables ]"\n'
    config = open(config_file, "r")
    config = json.loads(config.read())
    print("[*] Config file loaded: " + config_file)
    nvenv_name = config["nvenv_name"]
    # Halt if we have to delete the environment
    if delete:
        if not os.path.exists(nvenv_name):
            print("[*] Environment does not exist: " + nvenv_name)
        else:
            shutil.rmtree(nvenv_name, ignore_errors=True)
            print("[*] Deleted environment: " + nvenv_name)
        os._exit(0)
    # Else we use the environment
    print("[*] Reading from environment: " + nvenv_name)
    local_bin_folder = os.getcwd() + "/" + nvenv_name + "/" + config["local_bin"]
    print("[*] Local bin folder: " + local_bin_folder)
    load_file = os.getcwd() + "/" + nvenv_name + "/" + config["load_file"]
    new_environment(new)
    load_config() 
    load_environment()
    
# INFO Load a configuration file
def load_config():
    global cmds, local_bin_folder, load_file, hostname
    # Overwrites replace environment variables fully or create a new one
    overwrites = config['overwrites']
    for key in overwrites:
        cmds += "export " + key + "=" + overwrites[key] + "\n"
        print("[*] Overwriting enviromental variable: " + key)
    # Additions add the value to the environment variable preserving the original value
    additions = config["additions"]
    for key in additions:
        cmds += "export " + key + "=${" + key + "}:" + additions[key] + "\n"
        print("[*] Adding to enviromental variable: " + key)
    # Setting our environment variables
    print("[*] Setting our environment variables")
    cmds += "export PATH=" + local_bin_folder + ":" + os.environ["PATH"]
    # Loading the static environment variables defined in the config file
    print("[*] Setting the environment name as " + config["nvenv_name"])
    cmds += "export NVENV_NAME=" + config["nvenv_name"] + "\n"
    print("[*] Changing to: " + config["working_dir"])
    cmds += "cd " + config["working_dir"] + "\n"
    cmds += 'echo "nvenv environment loaded: $NVENV_NAME"\n'
    # Setting up customizations
    cmds += 'export PS1="' + username + ' [' + config["nvenv_name"] + '@' + hostname+ '] :> "\n' 
    # Finally, writing to the load file
    print("[*] Writing to the load file: " + load_file)
    with open(load_file, "w") as f:
        f.write(cmds)
    
# INFO Loading the local environment fully
def load_environment():
    print("[*] Loading the environment")
    global environment, load_file, shell
    # Multiple shells are supported
    if "zsh" in shell:
        cmd = "source " + load_file + " && " + shell + " -f -d"
    else:
        cmd = shell + " --rcfile " + load_file
    # Finally, loading the environment by sourcing the load file
    print("[+] Executing: " + cmd)
    print("\nNOTE: Digit 'exit' and press ENTER to return to the previous environment\n")
    os.system(cmd)
    
# INFO Environemnt creation
def new_environment(new_flag=False):
    global cmds, local_bin_folder
    if os.path.exists(os.getcwd() + "/" + nvenv_name):
        if not new_flag:
            raise Exception("[x] Environment already exists: " + nvenv_name)
        print("[+] Environment already exists: " + nvenv_name)
        return
    # Creating the local_bin_folder if it doesn't exist
    if not os.path.exists(local_bin_folder):
        os.makedirs(local_bin_folder)
    # Reading the init commands
    init_cmds_list = config["init_cmds"]
    for cmd in init_cmds_list:
        # Replacing folders if needed
        if (cmd == "here"):
            running_dir = os.getcwd()
        elif (cmd == "nvenv_folder"):
            running_dir = os.getcwd() + "/" + nvenv_name
        elif (cmd == "local_bin_folder"):
            running_dir = local_bin_folder
        else:
            # Support for custom directories
            # REVIEW Security note: limit it to the current working directory
            if not os.path.exists(running_dir):
                raise Exception("Running directory does not exist: " + running_dir)
        # Compiling the command to be executed before the environment is activated
        single_cmd = init_cmds_list[cmd]
        actual_cmd = "cd '" + running_dir + "' && " + single_cmd
        print("[*] Executing: " + actual_cmd)
        os.system(actual_cmd)
    # Support files
    files = config["files"]
    for file in files:
        origin = file[0]
        destination = file[1]
        if not os.path.exists(origin):
            raise Exception("[x] Origin file does not exist: " + origin)
        if os.path.exists(destination):
            raise Exception("[x] Destination file already exists: " + destination)
        print("[*] Copying file: " + origin + " to: " + destination)
        shutil.copy(origin, destination)

if __name__ == '__main__':
    # Argument parsing
    args_len = len(sys.argv)
    print(sys.argv)
    filename = sys.argv[0]
    params = {
        "operation": "run",
        "config_file": "config.json",
    }
    # Getting parameters
    for param in sys.argv[1:]:
        if "operation=" in param:
            params["operation"] = param.split("=")[1]
        if "config_file=" in param:
            params["config_file"] = param.split("=")[1]
    # Sanity checks
    if not os.path.exists(params["config_file"]):
        raise Exception("[x] Config file does not exist: " + params["config_file"])
    # Runs based on operation
    if params["operation"] == "activate" or params["operation"] == "run":
        main(config_file=params["config_file"])
    elif params["operation"] == "new":
        main(config_file=params["config_file"], new=True)
    elif params["operation"] == "remove":
        main(config_file=params["config_file"], delete=True)