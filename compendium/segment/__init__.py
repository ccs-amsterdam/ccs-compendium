"""
Init segments (phases)
"""

from compendium.segment.checksegment import CheckSegment
from compendium.segment.folderstructure import FolderStructureSegment
from compendium.segment.github import GithubSegment
from compendium.segment.pyenv import PyEnvSegment

SEGMENTS = [
        GithubSegment,
        FolderStructureSegment,
        PyEnvSegment,
        CheckSegment,
    ]
