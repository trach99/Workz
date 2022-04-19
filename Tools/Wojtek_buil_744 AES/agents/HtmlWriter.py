# v0.9
# python

import Results
import Tags
import CharacterTable


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


gsmInstructions = {
0xA4: "SELECT", 
0xF2: "STATUS", 
0xB0: "READ BINARY", 
0xD6: "UPDATE BINARY", 
0xB2: "READ RECORD", 
0xDC: "UPDATE RECORD", 
0xA2: "SEEK", 
0x32: "INCREASE", 
0x20: "VERIFY CHV", 
0x24: "CHANGE CHV", 
0x26: "DISABLE CHV", 
0x28: "ENABLE CHV", 
0x2C: "UNBLOCK CHV", 
0x04: "INVALIDATE", 
0x44: "REHABILITATE", 
0x88: "RUN GSM ALGORITHM", 
0xFA: "SLEEP", 
0xC0: "GET RESPONSE", 
0x10: "TERMINAL PROFILE", 
0xC2: "ENVELOPE", 
0x12: "FETCH", 
0x14: "TERMINAL RESPONSE"
}


# rebinding the builtin hex function 
# (e.g. 9 -> "0x09" and not "0x9")
def hex(n):
    return "0x%.2X" % n

# and chr as well (bad idea ?)
def chr(n):
    if n < 0x80:
        return CharacterTable.table[n] # chr(n)
    else:
        return '.'

def hextoo(n):
    return "%.2X" % n


def findBar(s):
    for i in range(len(s)):
        if s[i] == "|":
            return i;
    return -1

def sequenize(s):
    result = []
    i = 0
    while i < len(s):
        result.append(int(s[i] + s[i + 1], 16))
        i = i + 2
    return result


def xtractTLV(foo):
    
    result = []
    
    tag = foo.pop(0)
    
    length = foo.pop(0)
    if length == 0x81:  # 2-byte length ?
        length = foo.pop(0)
    
    if tag | 0x80 == 0x81: # Command details tag
        # result.append("Command details tag = " + hex(tag))
        for n in range(length): 
            foo.pop(0)
        
    elif tag | 0x80 == 0x82: # Device identities tag
        # result.append("Device identities tag = " + hex(tag))
        for n in range(length): 
            foo.pop(0)
        
    elif tag | 0x80 == 0x83: # Result tag
        # result.append("Result tag = " + hex(tag))
        result.append('General result = <em style="color:blue">"' + Results.generalResult[foo[0]] + '"</em>')
        for n in range(length): 
            foo.pop(0)
        
    elif tag | 0x80 == 0x85: # Alpha identifier tag
        # result.append("Alpha identifier tag = " + hex(tag))
        # result.append("Length = " + str(length) + " bytes")
        
        text = '&nbsp;&nbsp;&nbsp;&nbsp;"'
        
        if foo[0] == 0x80:
            foo.pop(0)
            length = length - 1
            for n in range(length / 2):
                text = text + "&#x" + hextoo(foo.pop(0)) + hextoo(foo.pop(0)) + ";"
        else:
            for n in range(length): 
                text = text + chr(foo.pop(0))
        result.append(text + '"')
        
    elif tag | 0x80 == 0x8D: # Text string tag
        # result.append("Text string tag = " + hex(tag))
        # result.append("Length = " + str(length) + " bytes")
        text = '&nbsp;&nbsp;&nbsp;&nbsp;"'
        
        length = length - 1
        dcs = foo.pop(0)
        if dcs == 0x08: # unicode string
            for n in range(length / 2):
                text = text + "&#x" + hextoo(foo.pop(0)) + hextoo(foo.pop(0)) + ";"
        else:
            for n in range(length): 
                text = text + chr(foo.pop(0))
        result.append(text + '"')
        
    elif tag | 0x80 == 0x8F: # Item tag
        itemText = '&nbsp;&nbsp;&nbsp;&nbsp;> "'
        foo.pop(0)
        length = length - 1
        if foo[0] == 0x80:
            foo.pop(0)
            length = length - 1
            for n in range(length / 2):
                itemText = itemText + "&#x" + hextoo(foo.pop(0)) + hextoo(foo.pop(0)) + ";"
        else:
            for n in range(length): 
                itemText = itemText + chr(foo.pop(0))
        result.append(itemText + '"')
        
    else:
        if tag in Tags.simpleTlvTags.keys():
            result.append(Tags.simpleTlvTags[tag] + " = " + hex(tag))
        else:
            result.append("Unknown tag = " + hex(tag))
            
        del foo[0: length]
        
    return result


def decomposeProactiveCommand(data):
    
    result = []
    
    data.pop(0) # get rid of the proactive sim command tag
    
    length = data.pop(0)
    if length == 0x81:  # 2-byte length ?
        length = data.pop(0)
    
    # now at the command details tag, so
    result.append('Type of command = <b style="color:blue">' + typeOfCommand[data[3]] + '</b>')
    
    while data:
        result.extend(xtractTLV(data))
    
    return result



# command details | device identities | result | ...
def decomposeTerminalResponse(data):
    
    result = []
    result.append('Type of command = <b style="color:red">' + typeOfCommand[data[3]] + '</b>')
    while data:
        result.extend(xtractTLV(data))
    return result


def decomposeEnvelope(data):

    result = []
    
    tag = data.pop(0) # get the type of the envelope
    
    length = data.pop(0)
    if length == 0x81:  # 2-byte length ?
        length = data.pop(0)
    
    result.append(Tags.berTlvTags[tag] + " = " + hex(tag))
    result.append("Length = " + str(length) + " bytes")
    while data:
        result.extend(xtractTLV(data))
    
    return result



def __onCommand(s):
    
    j = findBar(s)
    command = sequenize(s[:j])
    response = sequenize(s[j + 1:])
    
    ins = command[1]
    
    if ins == 0x12:
        
        # result = '[Fetch]<br />'
        result = '[FETCH]<br />'
        for line in decomposeProactiveCommand(response[:-2]):
            result = result + line + "<br />"
        return "<p>" + result + "</p>\n"
        
    elif ins == 0x14:
    
        # result = '[Terminal Response]<br />'
        result = '[TERMINAL RESPONSE]<br />'
        for line in decomposeTerminalResponse(command[5:]):
            result = result + line + "<br />"
        return "<p>" + result + "</p>\n"
        
    elif ins == 0xC2:
        
        # result = "[Envelope]<br />"
        result = "[ENVELOPE]<br />"
        for line in decomposeEnvelope(command[5:]):
            result = result + line + "<br />"
        return "<p>" + result + "</p>\n"
    
    elif ins in gsmInstructions:
        
        return "<p>[" + gsmInstructions[ins] + "]</p>\n"
    
    else:
        
        return "<p>[Unknown instruction]</p>\n"



def onCommand(s):
    s = __onCommand(s)
    f = open('./HtmlWriter.html', 'a')
    f.write(s)
    return "ok"


def onReset(s):
    f = open('./HtmlWriter.html', 'w')
    f.write("<html>\n")
    f.write("<head>\n")
    f.write('<link rel="stylesheet" type="text/css" href="style.css"/>\n')
    f.write("</head>\n")
    f.write("<body>\n")
    f.write("<p>Card reset :: " + s + "</p>\n")
    return "ok"



def run():
    s = 'A012000022|D020810301250082028182850C4149532053657276696365738F07A06D4C495645219000'
    print onCommand(s)
    
    s = "A01400001681030126010202828103010014083A95370800338603|913F"
    print onCommand(s)

    s = "A01400000D81030126010202828103021100|9000"
    print onCommand(s)

    s = "A0C20000AFD181AC820283810607919730071111F18B819C0405858564F97FF6102111816293008C00111D2471041904010103800031020203323232030103333333040103343434D0D0D0D00D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0DFF|9000"
    print onCommand(s)

