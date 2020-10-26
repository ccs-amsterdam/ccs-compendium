"""
Init segments (phases)
"""

from compendium.initsegment.checksegment import CheckSegment
from compendium.initsegment.folderstructure import FolderStructureSegment
from compendium.initsegment.github import GithubSegment
from compendium.initsegment.pyenv import PyEnvSegment

SEGMENTS = [
        GithubSegment,
        FolderStructureSegment,
        PyEnvSegment,
        CheckSegment,
    ]
