# NixVenv

## A pythonesque venv like approach to system virtual environments

### What is this?

Just as Python's venv allows developers to specify virtual environments for their python projects, NixVenv goal is to provide developers with the possibility to create virtual environments for their whole system.

Have you ever met a dependency that is required but would break your code elsewhere in your system? With NixVenv you can create a virtual environment for that specific application and run it with customized files, environment variables and configurations. Once you have finished, just deactivate it and you will be back in your usual shell environment.

### Features

• Customizable environment variables
• Easy to set up configuration
• Local files support
• Local binaries support and priority

### Installation

To install NixVenv, execute in a terminal:

    git clone https://github.com/thecookingsenpai/nixvenv
    cd nixvenv
    pip install -r requirements.txt

### Usage

    python nvenv.py operation=<operation> config_file=<configuration_json>

### Command Line Arguments

#### operation=

• run: activate the nvenv environment specified by the configuration
• activate: same as above
• new: create and activate the nvenv environment specified by the configuration if not already present
• remove: remove the nvenv environment specified by the configuration

#### config_file=

Any valid json file containing a nvenv configuration (relative path).
