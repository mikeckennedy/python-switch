"""
switchlang - Adds switch blocks to Python
"""

__version__ = '0.1.1'
__author__ = 'Michael Kennedy <michael@talkpython.fm>'
__all__ = ['switch', 'closed_range']

from .__switchlang_impl import switch
from .__switchlang_impl import closed_range
