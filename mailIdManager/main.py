#
#  main.py
#  mailVirtual
#
#  Created by Andrea Mistrali on 25/09/09.
#  Copyright akelge@gmail.com 2009. All rights reserved.
#
# $Id$

#import modules required by application
import objc
import Foundation
import AppKit


from PyObjCTools import AppHelper

# import modules containing classes required to start application and load MainMenu.nib
import mailVirtualAppDelegate
import account

# pass control to AppKit
AppHelper.runEventLoop()
