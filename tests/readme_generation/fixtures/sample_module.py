"""Sample module for testing AST analysis."""

import os
import sys
from pathlib import Path


def simple_function(arg1, arg2):
    """A simple function with a docstring."""
    return arg1 + arg2


def another_function():
    """Another function."""
    pass


class SampleClass:
    """A sample class."""

    def method_one(self):
        """First method."""
        pass

    def method_two(self, param):
        """Second method."""
        return param


class ChildClass(SampleClass):
    """A child class."""

    def child_method(self):
        """Child method."""
        pass