import Results
import Tags
import CharacterTable

import copy

newline = "<br />\n"
# newline = "\n"

typeOfCommand = {
0x01: "REFRESH", 
0x02: "MORE TIME", 
0x03: "POLL INTERVAL", 
0x04: "POLLING OFF", 
0x05: "SET UP EVENT LIST", 
0x10: "SET UP CALL", 
0x11: "SEND SS", 
0x12: "SEND USSD", 
0x13: "SEND SHORT MESSAGE", 
0x14: "SEND DTMF", 
0x15: "LAUNCH BROWSER", 
0x20: "PLAY TONE", 
0x21: "DISPLAY TEXT", 
0x22: "GET INKEY", 
0x23: "GET INPUT", 
0x24: "SELECT ITEM", 
0x25: "SET UP MENU", 
0x26: "PROVIDE LOCAL INFORMATION", 
0x27: "TIMER MANAGEMENT", 
0x28: "SET UP IDLE MODEL TEXT", 
0x30: "PERFORM CARD APDU", 
0x31: "POWER ON CARD", 
0x32: "POWER OFF CARD", 
0x33: "GET READER STATUS", 
0x34: "RUN AT COMMAND", 
0x35: "LANGUAGE NOTIFICATION", 
0x40: "OPEN CHANNEL", 
0x41: "CLOSE CHANNEL", 
0x42: "RECEIVE DATA", 
0x43: "SEND DATA", 
0x44: "GET CHANNEL STATUS"
}


# rebinding the builtin hex function 
# (e.g. 9 -> "0x09" and not "0x9")
def hex(n):
    return "0x%.2X" % n

def hextoo(n):
    return "%.2X" % n

def char(n):
    if n < 0x80:
        return CharacterTable.table[n] # chr(n)
    else:
        return '.'

def hexstring(foo, length):
    result = ""
    for i in range(length):
        result = result + hextoo(foo[i])
    return result

def totext(foo, length):
    result = ""
    for i in range(length):
        result = result + char(foo[i])
    return result

def poplv(foo):
    length = foo[0]
    length = min(length, len(foo) - 1) # right ?
    result = hexstring(foo, length + 1)
    del foo[:length + 1]
    return result


def xtractTlv(foo):
    
    result = []
    pop = []
    
    tag = foo.pop(0); pop.append(tag)
    
    length = foo.pop(0); pop.append(length)
    if length == 0x81:  # 2-byte length ?
        length = foo.pop(0); pop.append(length)
    
    tag_nocr = tag & 0x7f
    if tag_nocr in Tags.simpleTlvTags:
        name = Tags.simpleTlvTags[tag_nocr][:-4] # strip the ' tag'
    else:
        name = "Unknown tag ({0})".format(hex(tag))
    
    result.append("{0} [{1}{2}]<br />".format(name, hexstring(pop, len(pop)), hexstring(foo, length)))
    
    for n in range(length): 
        foo.pop(0)
    
    return result
    
    
def get_alphaid(foo):
    
    foo.pop(0) # ignore tag
    
    length = foo.pop(0)
    if length == 0x81:  # 2-byte length ?
        length = foo.pop(0)
    
    # todo: handle the two other unicode encodings
    text = ''
    if foo[0] == 0x80:
        foo.pop(0)
        length = length - 1
        for n in range(length / 2):
            text = text + "&#x" + hextoo(foo.pop(0)) + hextoo(foo.pop(0)) + ";"
    else:
        for n in range(length): 
            text = text + char(foo.pop(0))
    
    return text
    # return decorate_alphaid(text)


def get_textstring(foo):
    
    foo.pop(0) # ignore tag
    
    length = foo.pop(0)
    if length == 0x81:  # 2-byte length ?
        length = foo.pop(0)
    
    dcs = foo.pop(0)
    length = length - 1
    
    text = ''
    if dcs == 0x08: # unicode string
        for n in range(length / 2):
            text = text + "&#x" + hextoo(foo.pop(0)) + hextoo(foo.pop(0)) + ";"
    else:
        for n in range(length): 
            text = text + char(foo.pop(0))
    
    return text
    # return decorate_text(text)
    

def get_item(foo):
    
    foo.pop(0) # ignore tag
    
    length = foo.pop(0)
    if length == 0x81:  # 2-byte length ?
        length = foo.pop(0)

    itemIdentifier = foo.pop(0)
    length = length - 1
    
    itemText = ''
    if foo[0] == 0x80:
        foo.pop(0)
        length = length - 1
        for n in range(length / 2):
            itemText = itemText + "&#x" + hextoo(foo.pop(0)) + hextoo(foo.pop(0)) + ";"
    else:
        for n in range(length): 
            itemText = itemText + char(foo.pop(0))
            
    return itemIdentifier, itemText



    
    """
    elif tag | 0x80 == 0x83:
        # result.append("Result tag = " + hex(tag))
        result.append("General result = " + decorate_result(Results.generalResult[foo[0]]))
        for n in range(length): 
            foo.pop(0)
        
    elif tag | 0x80 == 0x90: # Item identifier tag
        result.append("Item identifier tag = " + hex(tag))
        result.append("&nbsp;&nbsp;&nbsp;&nbsp;Identifier of item chosen = <b>" + hex(foo.pop(0)) + "</b>")
        
    else:
        if tag in Tags.simpleTlvTags.keys():
            result.append(Tags.simpleTlvTags[tag] + " = " + hex(tag))
        else:
            result.append("Unknown tag = " + hex(tag))
            
        del foo[0: length]
        
    return result
    """

def decorate_command(s):
    return '<b style="color:blue">' + s + '</b>'

def decorate_response(s):
    return '<b style="color:red">' + s + '</b>'

def decorate_result(s):
    return '<em style="color:blue">' + s + '</em>'

def decorate_screen(s):
    return '<b style="color:darkgreen">' + s + '</b>'

def decorate_text(s):
    return '<b style="color:darkgreen">"' + s + '"</b><br />'


def indent(s):
    return '&nbsp;&nbsp;&nbsp;&nbsp;' + s;

def decorate_alphaid(s):
    return indent('<b style="color:black">"' + s + '"</b>')

def decorate_item(s):
    return indent('&gt;&gt; <b style="color:black">"' + s + '"</b>')


def locateTlv(tag, data):
    
    while (data[0] | 0x80) != (tag | 0x80):
        # print "%.2X" % data[0]
        data.pop(0)
        length = data.pop(0)
        if length == 0x81:
            length = data.pop(0)
        del data[:length]

def equal(tag1, tag2):
    # ignore the comprehension required flag
    return (tag1 | 0b10000000) == (tag2 | 0b10000000)
    
def friendlyView(data):
    
    # command details | device identities | ...
    
    # i.e. command details tag | length | command number | type of command | command qualifier
    commandType = data[3]
    
    if commandType == 0x21:
        # display text gets special treatment
        locateTlv(0x0D, data)
        textstring = get_textstring(data)
        lines = []
        lines.append('<table class=boxed>')
        lines.append('<tr class=head><td>{0}</td></tr>'.format(textstring))
        lines.append('</table>')
        return lines
        
    elif commandType in [0x24, 0x25]:
        # so does select item and set up menu
        lines = []
        lines.append('<table class=boxed>')
        
        titleAdded = False
        while data:
            if equal(data[0], 0x05):
                alphaid = get_alphaid(data)
                lines.append('<tr class=head><td colspan="2">{0}</td></tr>'.format(alphaid))
                titleAdded = True
            elif equal(data[0], 0x0F):
                if not titleAdded:
                    lines.append('<tr class=head><td colspan="2">&nbsp;</td></tr>')
                    titleAdded = True
                    
                identifier, text = get_item(data)
                lines.append('<tr><td>{0:X}</td><td>{1}</td></tr>'.format(identifier, text))
            else:
                xtractTlv(data) # ignore return value
                
        lines.append('</table>')
        return lines
    else:
        return []

elementId = 0

def decomposeProactiveCommand(data):
    
    # get rid of the proactive sim command tag
    data.pop(0)
    # and the length
    if data.pop(0) == 0x81:
        data.pop(0)
    # command details | device identities | ...
    
    lines = []
    
    global elementId
    elementId = elementId + 1
    lines.append('<div class="expander" onclick="toggle(\'id_{0}\')">'.format(elementId))
    
    lines.append("[FETCH]<br />")
    lines.append("Type of command = " + decorate_command(typeOfCommand[data[3]]) + "<br />")
    
    # friendly view
    lines.extend(friendlyView(list(data))) # passing a copy of the list
    
    lines.append('</div>') # end of the viewable clickable part
    
    
    # techno babble - hidden by default
    lines.append('<div class="expandable">')
    lines.append('<span id="id_{0:d}" style="display: none">'.format(elementId))
    
    while data:
        foo = xtractTlv(data)
        for line in foo:
            lines.append(line)
            
    lines.append('</span>')
    lines.append('</div>')
    
    result = ""
    for line in lines:
        result = result + line + "\n"
    return result

# command details | device identities | result | ...
def decomposeTerminalResponse(data):
    
    command = data[3]
    lines = "[TERMINAL RESPONSE]" + newline + \
        "Type of command = " + decorate_response(typeOfCommand[command]) + newline
    
    while data:
        foo = xtractTlv(data)
        for line in foo:
            lines = lines + line + newline
    
    """
    locateTlv(0x83, data)
    
    foo = xtractTlv(data)
    for line in foo:
        lines = lines + line + newline
    """
    
    return lines



