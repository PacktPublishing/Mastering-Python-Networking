import ntop, interface, json

ifnames = []
try:
    for i in range(interface.numInterfaces()):
        ifnames.append(interface.name(i))

except Exception as inst:
    print type(inst) # the exception instance
    print inst.args # arguments stored in .args
    print inst # __str__ allows args to printed directly

ntop.printHTMLHeader('Mastering Python Networking', 1, 0)
ntop.sendString("Here are my interfaces: <br>")
ntop.sendString(json.dumps(ifnames, sort_keys=True, indent=4))
ntop.printHTMLFooter()

