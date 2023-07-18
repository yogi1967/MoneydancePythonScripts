#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Initializer file for extension - this will only run from build 3056 onwards - otherwise ignored

import imp, datetime                                                                                                    # noqa
import __builtin__ as builtins                                                                                          # noqa
from java.lang import System, RuntimeException                                                                          # noqa
from com.moneydance.apps.md.controller import AppEventManager                                                           # noqa
global debug

_THIS_IS_ = "extract_data"

class _QuickAbortThisScriptException(Exception): pass

def _specialPrint(_what):
    dt = datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
    print(_what)
    System.err.write(_THIS_IS_ + ":" + dt + ": ")
    System.err.write(_what)
    System.err.write("\n")

def _decodeCommand(passedEvent):
    param = ""
    uri = passedEvent
    command = uri
    theIdx = uri.find('?')
    if(theIdx>=0):
        command = uri[:theIdx]
        param = uri[theIdx+1:]
    else:
        theIdx = uri.find(':')
        if(theIdx>=0):
            command = uri[:theIdx]
            param = uri[theIdx+1:]
    return command, param

msg = "\n#####################################################################\n"\
      "%s: %s_init.py initializer script running - doing nothing - will exit....\n"\
      "#####################################################################\n" %(_THIS_IS_,_THIS_IS_)

_specialPrint(msg)
