"""
switchlang - Adds switch blocks to Python

See https://github.com/mikeckennedy/python-switch for full details.
Copyright Michael Kennedy (https://twitter.com/mkennedy)
License: MIT
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version('switchlang')
except PackageNotFoundError:  # pragma: no cover
    __version__ = '0.0.0'
__author__ = 'Michael Kennedy <michael@talkpython.fm>'
__all__ = ['switch', 'closed_range']

from .__switchlang_impl import switch # noqa
from .__switchlang_impl import closed_range # noqa
