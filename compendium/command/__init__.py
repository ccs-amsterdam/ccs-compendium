from compendium.command.check import Check
from compendium.command.encrypt import Encrypt
from compendium.command.init import Init

COMMANDS = [
    Init,
    Check,
    Encrypt,
]


def get_command(name: str):
    for cmd in COMMANDS:
        if cmd.get_name() == name:
            return cmd
    raise ValueError(f"Unknown command: {name}")
