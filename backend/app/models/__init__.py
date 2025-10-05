"""
Models package initialization.
This file makes the models directory a Python package.
"""

from .user import User
from .itinerary import Itinerary

__all__ = ['User', 'Itinerary']
