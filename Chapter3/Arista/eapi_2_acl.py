#!/usr/bin/env python
# Copyright (c) 2014 Arista Networks
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import argparse
import jsonrpclib
import os
import sys
import subprocess

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# EAPI script to remotely edit an access list across multiple 
# Arista switches using your editor of choice.

# From a central server with IP connectivity to your switch, run this 
# script and specify an ACL name and a series of switches you are 
# interested in editing. This then opens your $EDITOR (e.g. vi or emacs)
# with the contents of the named ACL. When you're finished, close the file
# and this script will update that ACL across all of the switches you specified.
# No more dealing with annoying line numbers in the CLI!

def main():
   parser = argparse.ArgumentParser(description="Edit Arista ACLs using your local editor")
   parser.add_argument("acl", metavar="ACL",
                       help="Name of the access list to modify")
   parser.add_argument("switches", metavar="SWITCH", nargs="+",
                       help="Hostname or IP of the switch to query")
   parser.add_argument("--username", help="Name of the user to connect as",
                       default="admin")
   parser.add_argument("--password", help="The user's password")
   parser.add_argument("--https", help="Use HTTPS instead of HTTP",
                       action="store_const", const="https", default="http")
   args = parser.parse_args()

   aclName = args.acl
   tmpfile = "/tmp/AclEditor-%s" % aclName
   apiEndpoints = getEndpoints(args.switches, args.https,
                               args.username, args.password)
   prepopulateAclFile(tmpfile, aclName, apiEndpoints)
   edits = getEdits(tmpfile)
   applyChanges(aclName, apiEndpoints, edits)
   print
   print "Done!"

def getEndpoints(switchHostnames, protocol, username, password):
   """ Check that each server is up, and return a mapping from
   hostname to jsonrpclib.Server """
   apiEndpoints = {} # mapping from hostname to the API endpoint
   for switch in switchHostnames:
      url = "{protocol}://{user}:{pw}@{hostname}/command-api".format(
         protocol=protocol, user=username, pw=password, hostname=switch)
      server = jsonrpclib.Server(url)
      try:
         # We should at least be able to 'enable'
         server.runCmds(1, ["enable"])
      except Exception as e:
         print "Unable to run 'enable' on switch", e
         sys.exit(1)
      apiEndpoints[switch] = server
   return apiEndpoints

def prepopulateAclFile(filename, aclName, apiEndpoints):
   """ Given a jsonrpclib.Server called 'switch', prepopulate
   'filename' with the ACL contents. If the ACL does not yet exist,
   just print a message """

   # Currently assume all switches have the same config, so just use a
   # random one as the sample.
   apiEndpoint = apiEndpoints.itervalues().next()
   responseList = apiEndpoint.runCmds(1, ["enable",
                                          "show ip access-lists %s" % aclName])
   response = responseList[1] # Only care about the ACL output.
   if not response["aclList"]:
      print "No existing access list named", aclName, "- creating new ACL"
   else:
      # Prepopulate the file with the existing config
      print "Editing existing access list:"
      with open(filename, "w") as f:
         for rule in response["aclList"][0]["sequence"]:
            line = str(rule["sequenceNumber"]) + " " + rule["text"] + "\n"
            print "  ", line,
            f.write(line)
   print

def getEdits(filename):
   """ Opens an editor for the user to edit the ACL, and returns a
   list of the new ACL contents """
   editor = os.environ.get("EDITOR", "vi") # default editor is "vi"
   ret = subprocess.Popen([editor, filename]).wait()
   if ret != 0:
      print "Bad editor exit. Aborting."
      sys.exit(1)
   # Read in the file as a list of lines
   aclContents = open(filename, "r").readlines()
   print "New access list:"
   print "  ", "   ".join(aclContents) 
   print
   return aclContents

def applyChanges(aclName, apiEndpoints, aclRules):
   """ Given the switch mapping and a list of the new ACL rules, apply
   the ACL to each switch """
   cmdList = ["enable",
              "configure",
              # Not the most efficient way to clear an ACL:
                 "no ip access-list %s" % aclName,
              # Now enter configuration mode for the ACL:
                 "ip access-list %s" % aclName]
   cmdList = cmdList + aclRules + ["exit"]
   
   for hostname, apiEndpoint in apiEndpoints.iteritems():
      print "Updating access list on switch", hostname, "....",
      try:
         apiEndpoint.runCmds(1, cmdList)
      except jsonrpclib.ProtocolError as e:
         print "[ERROR]"
         print "  ", e
         # jsonrpclib isn't very friendly at getting the error data as
         # specified by the spec. This is a shortcut for getting the
         # last error:
         errorResponse = jsonrpclib.loads(jsonrpclib.history.response)
         print "   Details:", errorResponse["error"]["data"][-1]["errors"]
      else:
         print "[SUCCESS]"

if __name__ == "__main__":
   main()

