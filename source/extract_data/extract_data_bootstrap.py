#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################################################################
## Bootstrap to execute a compiled script if possible (faster load times) ##############################################
########################################################################################################################

import imp
import datetime
import __builtin__ as builtins

from java.lang import System

global moneydance, moneydance_ui, moneydance_extension_parameter, moneydance_extension_loader

_THIS_IS_ = u"extract_data"

def _specialPrint(_what):
    dt = datetime.datetime.now().strftime(u"%Y/%m/%d-%H:%M:%S")
    print(_what)
    System.err.write(_THIS_IS_ + u":" + dt + u": ")
    System.err.write(_what)
    System.err.write(u"\n")


builtins.moneydance = moneydance            # Little trick as imported module will have it's own globals
builtins.moneydance_ui = moneydance_ui      # Little trick as imported module will have it's own globals

MDEL = u"moneydance_extension_loader"
if MDEL in globals(): builtins.moneydance_extension_loader = moneydance_extension_loader

MDEP = u"moneydance_extension_parameter"
if MDEP in globals(): builtins.moneydance_extension_parameter = moneydance_extension_parameter

MD_EXTENSION_LOADER = moneydance_extension_loader

_compiledExtn = u"$py.class"
_normalExtn = u".py"

_launchedFile = _THIS_IS_ + _compiledExtn
scriptStream = MD_EXTENSION_LOADER.getResourceAsStream(u"/%s" %(_launchedFile))
if scriptStream is None:
    _specialPrint(u"@@ Will run normal (non)compiled script ('%s') @@" %(_launchedFile))
    _launchedFile = _THIS_IS_ + _normalExtn
    scriptStream = MD_EXTENSION_LOADER.getResourceAsStream(u"/%s" %(_launchedFile))
    _suffixIdx = 0
else:
    _specialPrint(u"@@ Will run pre-compiled script for best launch speed ('%s') @@" %(_launchedFile))
    _suffixIdx = 1

_startTimeMs = System.currentTimeMillis()
bootstrapped_extension = imp.load_module(_THIS_IS_,
                                         scriptStream,
                                         (u"bootstrapped_" + _launchedFile),
                                         imp.get_suffixes()[_suffixIdx])
_specialPrint(u"BOOTSTRAP launched script in %s seconds..." %((System.currentTimeMillis() - _startTimeMs) / 1000.0))

# if the extension is using an extension class, then pass pass back to Moneydance
try: moneydance_extension = bootstrapped_extension.moneydance_extension
except AttributeError: pass
