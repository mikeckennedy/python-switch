"""
switchlang - Adds switch blocks to Python

See https://github.com/mikeckennedy/python-switch for full details.
Copyright Michael Kennedy (https://twitter.com/mkennedy)
License: MIT
"""

__version__ = '0.1.0'
__author__ = 'Michael Kennedy <michael@talkpython.fm>'
__all__ = ['switch', 'closed_range']

from .__switchlang_impl import switch
from .__switchlang_impl import closed_range
