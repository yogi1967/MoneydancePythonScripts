#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# This is a Python 'stub' file.
# It's purpose is to provide 'type hinting' to your IDE

# This is so that the 'magic' objects that appear at run-time, provided by Moneydance (to the Python Interpreter)
# can be properly understood and resolved...

# This file does not get executed at run-time, should never be run, and should not contain actual executable code.
# You do not need this file to run the code, only for editing in an IDE environment.

# Last updated August 2023

###############################################################################
# MIT License
#
# Copyright (c) 2020-2024 Stuart Beesley - StuWareSoftSystems
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################
from com.moneydance.apps.md.controller import Main as Main
from com.moneydance.apps.md.view.gui import MoneydanceGUI as MoneydanceGUI
from com.infinitekind.moneydance.model import AccountBook as AccountBook
from java.lang import ClassLoader as ClassLoader    # Really com.moneydance.apps.md.controller.ModuleLoader.FMClassLoader (but cannot reference that)

moneydance = Main()                             # type: Main
moneydance_ui = MoneydanceGUI()                 # type: MoneydanceGUI
moneydance_data = AccountBook()                 # type: AccountBook

moneydance_extension_loader = ClassLoader()     # type: ClassLoader
moneydance_extension_parameter: str = ""