from pathlib import Path
from typing import NamedTuple, List, Dict


class Action(NamedTuple):
    file: Path
    action: str
    targets: List[Path]
    inputs: List[Path]
    headers: Dict[str, str]
