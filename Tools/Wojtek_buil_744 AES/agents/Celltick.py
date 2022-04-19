# v0.9
# python

import Results
import Tags
import CharacterTable
import STK

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


class MTI:
    DELIVER = 0


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
    
    # right ?
    length = min(length, len(foo) - 1)
    
    result = hexstring(foo, length + 1)
    del foo[:length + 1]
    return result
    

messageVersions = {
0b00: "Version 1.0", 
0b01: "Version 2.0", 
0b10: "Version 3.0", 
0b11: "Version 4.0"
}

messageTypes = {
0b00: "Emergency Content Message (RFU)", 
0b01: "Content Message", 
0b10: "Command Message", 
0b11: "Personalized Content Message"
}

states = {
0b000: "Deactivate", 
0b001: "RFU", 
0b010: "No Change", 
0b011: "RFU", 
0b100: "RFU", 
0b101: "RFU", 
0b110: "Activate", 
0b111: "Activate - Unblock"
}


opcodes = {
0x00: "RFU", 
0x01: "RFU", 
0x02: "RFU", 
0x03: "Phone Parameters", 
0x04: "NOT SUPPORTED", 
0x05: "Fixed & Default Menu Items", 
0x06: "Application Parameters", 
0x07: "Server Address", 
0x08: "CB Channel", 
0x09: "Notification", 
0x0A: "NOT SUPPORTED", 
0x0B: "NOT SUPPORTED", 
0x0C: "IMEI Request", 
0x0D: "Service Center Address", 
0x0E: "Server Identification", 
0x0F: "Change Server Identification", 
0x10: "Change Language", 
0x11: "Multi Language Support", 
0x12: "3rd Party", 
0x13: "Icons Support", 
0x14: "Personalization Channels Command", 
0x15: "Mobile Specific Channels Command", 
0x16: "Service Channels Command", 
0x17: "Base URL Data", 
0x18: "Activity Tracking Type"
}

textCodings = {
0b00: "GSM default", 
0b01: "UCS2 compression for non-Asian languages (0x81)", 
0b10: "UCS2 compression for Asian languages (0x82)", 
0b11: "UCS2"
}

extendedActions = {
0x00: "Launch URL - WAP", 
0x01: "Launch URL - HTML", 
0x02: "Send USSD", 
0x03: "Send USSD 2", 
0x04: "Menu Item", 
0x05: "3rd Party Activation", 
0x06: "Activity Tracking", 
0x10: "Icon", 
0x11: "Channels list element"
}

def decodeCommand(foo):
    
    line = opcodes[foo[0]]
    while len(line) < 36:
        line = line + "."
    length = 1 + 1 + foo[1]
    
    line = line + " [" + hexstring(foo, length) + "]"
    del foo[:length]
    return [line]


def decodeAction(foo):
    
    result = []
    
    details = foo.pop(0)
    dynamicMenu  = (details & 0b10000000) >> 7
    actionType   = (details & 0b01110000) >> 4
    numberLength = (details & 0b00001111)
    
    if actionType == 0:
        # WAP
        line = "    WAP [%.2X" % details
        
        # action details
        # number
        # b|bbbbbbb = add option id|length of content
        # content
        
        line = line + hexstring(foo, numberLength)
        del foo[:numberLength]
        
        contentLength = foo[0] & 0x7F
        
        line = line + hexstring(foo, contentLength + 1)
        del foo[:contentLength + 1]
        
        if dynamicMenu:
            # length of title | title
            line = line + poplv(foo) + "]"
        else:
            # fixed index
            index = foo.pop(0)
            line = line + "%.2X]" % index
            # line = line + ' index no. %d' % index
            
        result.append(line)
        
    elif actionType == 1:
        # Set Up Call
        line = "    Set Up Call [%.2X" % details
        
        line = line + hexstring(foo, numberLength)
        del foo[:numberLength]
        
        # contentLength = foo[0] & 0x7F
        # 
        # line = line + hexstring(foo, contentLength + 1)
        # del foo[:contentLength + 1]
        
        if dynamicMenu:
            # length of title | title
            line = line + poplv(foo) + "]"
        else:
            # fixed index
            index = foo.pop(0)
            line = line + "%.2X]" % index
        
        result.append(line)
        
    elif actionType == 2:
        # Regular SMS
        line = "    Regular SMS [%.2X" % details
        
        line = line + hexstring(foo, numberLength)
        del foo[:numberLength]
        
        contentLength = foo[0] & 0x7F
        
        line = line + hexstring(foo, contentLength + 1)
        del foo[:contentLength + 1]
        
        if dynamicMenu:
            # length of title | title
            line = line + poplv(foo) + "]"
        else:
            # fixed index
            index = foo.pop(0)
            line = line + "%.2X]" % index
        
        result.append(line)
        
    elif actionType == 3:
        # Celltick SMS
        line = "    Celltick SMS [%.2X" % details
        
        line = line + hexstring(foo, numberLength)
        del foo[:numberLength]
        
        contentLength = foo[0] & 0x7F
        
        line = line + hexstring(foo, contentLength + 1)
        del foo[:contentLength + 1]
        
        if dynamicMenu:
            # length of title | title
            line = line + poplv(foo) + "]"
        else:
            # fixed index
            index = foo.pop(0)
            line = line + "%.2X]" % index
        
        result.append(line)
        
    elif actionType == 4:
        # Store
        line = "    Store (NOT SUPPORTED) [%.2X" % details
        
        line = line + hexstring(foo, numberLength)
        del foo[:numberLength]
        
#        contentLength = foo[0] & 0x7F
#        
#        line = line + hexstring(foo, contentLength + 1)
#        del foo[:contentLength + 1]
        
        if dynamicMenu:
            # length of title | title
            line = line + poplv(foo) + "]"
        else:
            # fixed index
            index = foo.pop(0)
            line = line + "%.2X]" % index
        
        result.append(line)
        
    elif actionType == 5:
        # Forward
        line = "    Forward (NOT SUPPORTED) [%.2X" % details
        
        line = line + hexstring(foo, numberLength)
        del foo[:numberLength]
        
        contentLength = foo[0] & 0x7F
        
        line = line + hexstring(foo, contentLength + 1)
        del foo[:contentLength + 1]
        
        if dynamicMenu:
            # length of title | title
            line = line + poplv(foo) + "]"
        else:
            # fixed index
            index = foo.pop(0)
            line = line + "%.2X]" % index
        
        result.append(line)
        
    elif actionType == 6:
        # Free Text
        line = "    Free Text [%.2X" % details
        
        line = line + hexstring(foo, numberLength)
        del foo[:numberLength]
        
        contentLength = foo[0] & 0x7F
        
        line = line + hexstring(foo, contentLength + 1)
        del foo[:contentLength + 1]
        
        if dynamicMenu:
            # length of title | title
            line = line + poplv(foo) + "]"
        else:
            # fixed index
            index = foo.pop(0)
            line = line + "%.2X]" % index
        
        result.append(line)
        
    elif actionType == 7:
        # Action Extension
        length = foo[0]
        action = foo[1]
        result.append("    %s [%.2X%s]" % \
            (extendedActions[action], details, hexstring(foo, length + 1)))
        del foo[:length + 1]
        
    else:
        result.append("%.2X" % details)
        # eh?
    
    return result



def boolstr(flag):
    if flag:
        return "True"
    else:
        return "False"


current = -1
toCome = [1, 2, 3, 4]
part_1 = []
part_2 = []
part_3 = []
part_4 = []

def add_part(part):
    
    global current
    global toCome
    global part_1
    global part_2
    global part_3
    global part_4
    
    
    # id
    # seq no | total
    
    if part[0] == 0:
        return []
    
    if part[0] != current:
        part_1 = []
        part_2 = []
        part_3 = []
        part_4 = []
        total = part[1] % 16
        if total == 4:
            toCome = [1, 2, 3, 4]
        elif total == 3:
            toCome = [1, 2, 3]
        elif total == 2:
            toCome = [1, 2]
        else:
            toCome = [1]
        current = part[0]
        
    seqno = part[1] / 16
    if seqno == 1:
        part_1 = copy.copy(part)
        del part_1[:2]
    elif seqno == 2:
        part_2 = copy.copy(part)
        del part_2[:2]
    elif seqno == 3:
        part_3 = copy.copy(part)
        del part_3[:2]
    else:
        part_4 = copy.copy(part)
        del part_4[:2]
    toCome.remove(seqno)
    
#    print seqno
#    print toCome
#    print hexstring(part_1, len(part_1))
#    print hexstring(part_2, len(part_2))
#    print hexstring(part_3, len(part_3))
#    print hexstring(part_4, len(part_4))
    
    if len(toCome) > 0:
        return []
    
    current = -1
    
    result = []
    # result.append('<div style="background-color: #f0f0f0; padding: 10px; border: solid; border-width: 1px;">\n')
    
    full = []
    full.extend(part_1)
    full.extend(part_2)
    full.extend(part_3)
    full.extend(part_4)
    
    # print hexstring(full, len(full))
    
    # message header length
    # message details byte no. 1
    
    details1 = full[1]
    messageType = (details1 & 0b00110000) >> 4
    
    if messageType == 0b10:
        result.append('<div style="background-color: #ffffc0; padding: 10px; border: solid; border-width: 1px;">\n')
        result.extend(decodeCommandPacket(full, 1))
    else:
        result.append('<div style="background-color: #f0f0f0; padding: 10px; border: solid; border-width: 1px;">\n')
        result.extend(decodeContentPacket(full, 1))
    
    # h4x0r
    result[1] = result[0] + result[1]
    result[0] = ""
    
    result.append("</div>\n")
    return result



def decodeContentPacket(foo, index):
    
    result = []
    
    if index == 1:
        # we'll only try to decode the CBDD holding first page
        
        length = foo.pop(0) # the message header length
        
        # well, in fact the message header length is a 9-bit value where the MSB
        # is found as bit no. 4 of the following byte, so
        length = length + ((foo[0] & 0b00001000) << 5)
        
        result.append("Message Header Length = " + str(length) + " bytes")
        
        header = foo[:length]
        
        # the text screens will follow the header
        screens = foo[length:]
        
        # foo = header
        # del foo[length:]
        
        details1 = header.pop(0)
        details2 = header.pop(0)
        
        messageVersion     = messageVersions[(details1 & 0b11000000) >> 6]
        messageType        =                 (details1 & 0b00110000) >> 4
        flagExtendedHeader =                 (details1 & 0b00001000) >> 3
        textCoding         =                 (details1 & 0b00000110) >> 1
        flagResponse       =                  details1 & 0b00000001
        
        flagBeep        = (details2 & 0b10000000)
        flagFlash       = (details2 & 0b01000000)
        flagMSCI        = (details2 & 0b00100000)
        flagSCI         = (details2 & 0b00010000)
        numberOfActions = (details2 & 0b00001111)
        
        result.append("Message Details = " + hextoo(details1) + " " + hextoo(details2))
        result.append("........Version = " + messageVersion)
        result.append("........Type = " + messageTypes[messageType])
        result.append("........Extended Header = " + boolstr(flagExtendedHeader))
        result.append("........Text Coding = " + textCodings[textCoding])
        result.append("........Response Message = " + boolstr(flagResponse))
        result.append("........Beep Message = " + boolstr(flagBeep))
        result.append("........Flash Message = " + boolstr(flagFlash))
        result.append("........Mobile Specific Channel Indicator = " + boolstr(flagMSCI))
        result.append("........Service Channel Indicator = " + boolstr(flagSCI))
        result.append("........Number of Actions = " + str(numberOfActions))
        
        if messageType == 0b11:
            result.append("    [Personal Channel #%.2X]" % header.pop(0))
        
        if textCoding == 0b01:
            result.append("    [Decompression Offset = %.2X]" % header.pop(0))
        elif textCoding == 0b10:
            result.append("    [Decompression Offset = %.2X%.2X]" % (header.pop(0), header.pop(0)))
        
        if flagMSCI:
            result.append("    [Mobile Specific Channel #%.2X]" % header.pop(0))
        
        if flagSCI:
            result.append("    [Service Channel #%.2X]" % header.pop(0))
        
        if numberOfActions > 0:
            numberlength = header.pop(0)
            if numberlength > 0:
                result.append("    [Default Number %s]" % hexstring(header, numberlength))
                del header[:numberlength]
            
            contentlength = header.pop(0)
            if contentlength > 0:
                result.append('    [Default Content "%s"]' % totext(header, contentlength))
                del header[:contentlength]
        
        for i in range(numberOfActions):
            try:
                result.extend(decodeAction(header))
            except IndexError:
                # return what we've gathered so far
                return result
        
        if len(header) > 0:
            result.append(hexstring(header, len(header)))
            result.append('"%s"' % totext(header, len(header)))
        
        # result.append('--- end-of-header ---')

        if len(screens) == 0:
            # return what we've gathered so far
            return result
            
        numberOfScreens = screens.pop(0)
        result.append("Number of screens = " + hextoo(numberOfScreens))
        
        for i in range(numberOfScreens):
            try:
                h_length = screens[0]
                result.append("Screen Header [" + hexstring(screens, h_length) + "]")
                
                del screens[:h_length]
                
                c_length = screens.pop(0)
                result.append("Content Length = %d" % c_length)
                
                c_length = min(c_length, len(screens))
                result.append(decorate_screen('"%s"' % totext(screens, c_length)))
                
                del screens[:c_length]
                
            except IndexError:
                # todo: display non-complete screens
                return result
        
    else:
        # page 2, 3, ...
        screens = foo
    
    if len(screens) > 0:
        result.append(hexstring(screens, len(screens)))
        result.append(decorate_screen('"%s"' % totext(screens, len(screens))))
    
    return result


def decodeCommandPacket(foo, index):
    
    result = []
    
    # todo: 
    # can a command span several pages ?
    # if carried in an sms, how would we identify a sequence (id always zero) ?
    
    length = foo.pop(0) # the message header length
    result.append("Message Header Length = " + str(length) + " bytes")
    
    # delete any unused bytes at the end
    padding = foo[length:]
    del foo[length:]
    
    details1 = foo.pop(0)
    details2 = foo.pop(0)
    
    messageVersion = messageVersions[(details1 & 0xC0) >> 6]
    messageType    = messageTypes[(details1 & 0x30) >> 4]
    nextState      = states[(details1 & 0x0E) >> 1]
    numberOfCommands = details2 & 0x0F
    
    result.append("Message Details = " + hextoo(details1) + " " + hextoo(details2))
    result.append("........Version = " + messageVersion)
    result.append("........Type = " + messageType)
    result.append("........State = " + nextState)
    result.append("........Number of Commands = " + str(numberOfCommands))
    
    for i in range(numberOfCommands):
        result.extend(decodeCommand(foo))
    
    if len(foo) > 0:
        result.append("eh ?")
        result.append(hexstring(foo, len(foo)))

    return result



# decoding from the page header and onwards
def decode(foo):
    
    result = []
    
    soapbox = add_part(foo)
    
    ID    = foo.pop(0)
    total = foo[0] % 16
    index = foo[0] / 16
    foo.pop(0)
    
    line = "Message ID = " + hextoo(ID)
    if ID == 0:
        result.append(line + " (Command Message via SMSDD)")
    elif ID == 1:
        result.append(line + " (NULL Message)")
    elif ID > 0x80:
        result.append(line + " (Content Message via SMSDD)")
    else:
        result.append(line + " (Cell Broadcast)")
    result.append("Page no. " + str(index) + " of " + str(total))
    
    if ID == 0:
        # decoding a command message, smsdd
        result.extend(decodeCommandPacket(foo, index))
    
    elif ID == 1:
        # null message, there's nothing to decode
        result.append(hexstring(foo, len(foo)))
        
    elif ID < 0x80:
        # on a cell broadcast the type cannot be inferred from the id
        
        if index == 1 and total == 1 and ((foo[1] & 0b00110000) >> 4) == 0b10:
            result.extend(decodeCommandPacket(foo, index))
        else:                    
            result.extend(decodeContentPacket(foo, index))
        
    else:
        # decoding a content message, smsdd
        result.extend(decodeContentPacket(foo, index))
        
        
    result.extend(soapbox)
    
    return result



def xtractTlv(foo):
    
    result = []
    
    tag = foo.pop(0)
    
    length = foo.pop(0)
    if length == 0x81:  # 2-byte length ?
        length = foo.pop(0)
    
    if tag | 0x80 == 0x81:
        # result.append("Command details tag = " + hex(tag))
        for n in range(length): 
            foo.pop(0)
        
    elif tag | 0x80 == 0x82:
        # result.append("Device identities tag = " + hex(tag))
        for n in range(length): 
            foo.pop(0)
        
    elif tag | 0x80 == 0x83:
        # result.append("Result tag = " + hex(tag))
        result.append("General result = " + decorate_result(Results.generalResult[foo[0]]))
        for n in range(length): 
            foo.pop(0)
        
    elif tag | 0x80 == 0x85:
        result.append("Alpha identifier tag = " + hex(tag))
        # result.append("Length = " + str(length) + " bytes")
        text = ''
        for n in range(length): 
            text = text + char(foo.pop(0))
        result.append(decorate_alphaid(text))
        
    elif tag | 0x80 == 0x8B:
        result.append("SMS TPDU tag = " + hex(tag))
        result.append("........Length = " + str(length) + " bytes")
        
        flags = foo.pop(0)
        length = length - 1
        result.append("........[RP|UDHI|SRI|RFU|RFU|MMS|MTI] = " + hex(flags))
        
        mti = flags & 0x03
        if mti == MTI.DELIVER:
            # TP-OA
            ll = 1 + 1 + ((foo[0] + 1) >> 1)
            tpoa = ""
            for i in range(ll):
                tpoa = tpoa + hextoo(foo.pop(0))
                length = length - 1
            result.append("........TP-OA = " + tpoa);
            
            result.append("........TP-PID = " + hex(foo.pop(0)))
            result.append("........TP-DCS = " + hex(foo.pop(0)))
            length = length - 2
            
            result.append("........TP-SCTS = " + hexstring(foo, 7))
            length = length - 7
            del foo[0:7]
            
            udl = foo.pop(0)
            length = length - 1
            result.append("........TP-UDL = " + hex(udl))
            
            result.append("---oo0oo---")
            
            result.extend(decode(foo[:length]))
            
            del foo[0:length]
        else:
            del foo[0:length]
        
    elif tag | 0x80 == 0x8C:
        result.append("Cell Broadcast page tag = " + hex(tag))
        if length != 88:
            result.append("........Length = " + str(length) + " bytes <-- INVALID LENGTH")
        
        # 1-2   Serial Number
        # 3-4   Message Identifier
        # 5     Data Coding Scheme
        # 6     Page Parameter
        # 7-88  Content of Message
        
        result.append("........Serial Number      = " + hexstring(foo, 2))
        del foo[:2]
        result.append("........Message Identifier = " + hexstring(foo, 2))
        del foo[:2]
        dcs  = foo.pop(0)
        ppar = foo.pop(0)
        result.append("........Data Coding Scheme = " + hextoo(dcs))
        result.append("........Page Parameter     = " + hextoo(ppar))
        
        length = length - 6
        
        result.append("---oo0oo---")
        result.extend(decode(foo[:length - 1])) # last byte should be ignored
        
        del foo[:length]
        
        
    elif tag | 0x80 == 0x8D:
        # result.append("Text string tag = " + hex(tag))
        # result.append("Length = " + str(length) + " bytes")
        
        length = length - 1
        dcs = foo.pop(0)
        # result.append("Data coding scheme = " + hex(dcs))
        
        text = ''
        
        if dcs == 0x08: # unicode string
            for n in range(length / 2):
                text = text + "&#x" + hextoo(foo.pop(0)) + hextoo(foo.pop(0)) + ";"
        else:
            for n in range(length): 
                text = text + char(foo.pop(0))
        
        result.append(decorate_text(text))
        
    elif tag | 0x80 == 0x8F: # item tag

        itemIdentifier = foo.pop(0)
        length = length - 1
        # result.append("Item tag = " + hex(tag))
        # result.append("Length = " + str(length) + " bytes")
        result.append("Identifier of item = " + hex(itemIdentifier))
        
        itemText = ''
        if foo[0] == 0x80:
            foo.pop(0)
            length = length - 1
            for n in range(length / 2):
                itemText = itemText + "&#x" + hextoo(foo.pop(0)) + hextoo(foo.pop(0)) + ";"
        else:
            for n in range(length): 
                itemText = itemText + char(foo.pop(0))
        result.append(decorate_item(itemText))
        
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


def decorate_command(s):
    return '<b style="color:blue">' + s + '</b>'

def decorate_response(s):
    return '<b style="color:red">' + s + '</b>'

def decorate_result(s):
    return '<em style="color:blue">' + s + '</em>'

def decorate_screen(s):
    return '<b style="color:darkgreen">' + s + '</b>'

def decorate_text(s):
    return '<b style="color:darkgreen">"' + s + '"</b>'


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


def decomposeProactiveCommand(data):
    
    # get rid of the proactive sim command tag
    data.pop(0)
    # and the length
    if data.pop(0) == 0x81:
        data.pop(0)
    # command details | device identities | ...
    lines = "[FETCH]" + newline + \
        "Type of command = " + decorate_command(typeOfCommand[data[3]]) + newline

    while data:
        foo = xtractTlv(data)
        for line in foo:
            lines = lines + line + newline

    """
    if data[3] == 0x21:
        # display text gets special treatment
        locateTlv(0x0D, data)
        
        foo = xtractTlv(data)
        for line in foo:
            lines = lines + line + newline
    
    elif data[3] in [0x24, 0x25]:
        # so does select item and set up menu
        while (data[0] | 0x80) not in [0x85, 0x8F]:
            xtractTlv(data) # ignore return value
        
        while data:
            foo = xtractTlv(data)
            for line in foo:
                lines = lines + line + newline
    """    
        
    return lines

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


def decomposeEnvelope(data):

    tag = data.pop(0) # get the type of the envelope
    
    length = data.pop(0)
    if length == 0x81:  # 2-byte length ?
        length = data.pop(0)
    
    if tag == 0xD1:
        result = ["[ENVELOPE (SMS-PP DOWNLOAD)]"]
    elif tag == 0xD2:
        result = ["[ENVELOPE (CELL BROADCAST DOWNLOAD)]"]
    elif tag == 0xD3:
        result = ["[ENVELOPE (MENU SELECTION)]"]
    else:
        result = ["[ENVELOPE]"]
    
    while data:
        result.extend(xtractTlv(data))
    
    return result



def __onCommand(s):
    
    j = findBar(s)
    command = sequenize(s[:j])
    response = sequenize(s[j + 1:])
    
    ins = command[1]
    
    if ins == 0x12:
        
        return STK.decomposeProactiveCommand(response[:-2]) # + newline
        
    elif ins == 0x14:
    
        return decomposeTerminalResponse(command[5:]) # + newline
        
    elif ins == 0xC2:
        
        result = ""
        for line in decomposeEnvelope(command[5:]):
            result = result + line + newline
        return result
        
    elif ins in gsmInstructions:
        
        return "[" + gsmInstructions[ins] + "]" + newline
    
    else:
        
        return "[UNKNOWN]" + newline



def onCommand(s):
    foo = __onCommand(s)
    f = open('./Celltick.html', 'a')
    f.write("<!-- {0} -->\n".format(s))
    f.write("<p>\n")
    f.write(foo)
    f.write("</p>\n")
    return "OK"



def recreate(filename):
    # delete and recreate
    f = open(filename, 'w')
    f.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n')
    f.write('<html>\n')
    f.write('<head>\n')
    f.write('<link rel="stylesheet" type="text/css" href="treestyle.css"/>\n')
    f.write('<script type="text/javascript" src="treescript.js"></script>\n')
    f.write('<link rel="stylesheet" type="text/css" href="styling.css"/>\n')
    f.write('<script type="text/javascript" src="toggle.js"></script>\n')
    f.write('</head>\n')
    f.write('<body>\n')
    return f

def onReset(s):
    f = recreate('./Celltick.html')
    
    global global_id
    ulid = "id%.3d" % global_id
    global_id = global_id + 1
    
    f.write('<ul class="TreeView" id="%s"><li class="Collapsed">[Card reset]<ul><li>%s</li></ul></li></ul>\n' % (ulid, s))
    f.write('<script type="text/javascript" language="javascript">SetupTreeView("%s");</script>\n' % ulid)
    
    f.write(newline)
    
    return "OK"



def run():

    s = "A01200006C|D06A8103012400820281820F0D01416D6973686120506174656C0F10024B61726973686D61204B61706F6F720F0B034C6172612044757474610F0804636861726765730F06054A4F4B45530F0D064E657874204D6573736167650F090750726576696F75730F0508457869749000"
    print onCommand(s)
    
#    s = "A0C2000060D25E820283810C580056101AF21133135B30050B04812524F50E2130383136203030323031623133B0800946494E44204F555421B4812123F0800763686172676573B080054A4F4B4553B0800D414D415A494E47204641435453B0800F4C5500|9000"
#    print onCommand(s)
#    
#    s = "A0C2000066D16402028381060891799708009000F00B5404048117827FF690300241336132450011422E7606103C01050A070300003C00B400B400B403140A0008001718191A1B1C1D130701014700AD002115060004000102031605000300010303080E030540000F07F0|9000"
#    print onCommand(s)
#    
#    s = "A0C2000060D25E020283810C580D501040F2112413B13037170705038117821063202142534944203030303239323665F0051103010117F006110402020103F00711050303010203B0800F4D6F726520496E666F2028534D532980800F4D6F726520496E00|9000"
#    print onCommand(s)
#    
#    s = "A0C2000060D25E020283810C580DB01040F21125123E30351807050000F0051103010118F006110402020103F00711050303010203B38117829063202142534944203030303133626235044D6F7265F0031001010102001E546174612067726F7570206900|9000"
#    print onCommand(s)
#    
#    
#    s = "A0C2000060D25E020283810C580DB01040F21125123E30351807050000F0051103010118F006110402020103F00711050303010203B38117829063202142534944203030303133626235044D6F7265F0031001010102001E546174612067726F7570206900|9000"
#    print onCommand(s)
#    
#    
#    s = "A0C2000060D25E020283810C580DD01040F211252273206E6F7420455850414E44494E472021200D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D00|9000"
#    print onCommand(s)
#    
#    print onReset("3B16969F000E011203")
#    print onCommand("A012000030|D02E8103012180820281028D1F04546174612067726F7570206973206E6F7420455850414E44494E472021201E0201019000")
#    print onCommand("A01400000C810301218002028281030112|913E")
#
#    print onCommand("A0C2000060D25E020283810C580D501040F2112413B13037170705038117821063202142534944203030303239323665F0051103010117F006110402020103F00711050303010203B0800F4D6F726520496E666F2028534D532980800F4D6F726520496E00|9000")
#    print onCommand("A0C2000060D25E020283810C580D701040F2112423666F20285741502970540052687474703A2F2F36322E39302E32382E33383A383038302F7761704170702F636F6E3F61633D706572736F6E616C70616765266D736769643D3030313638353538266F00|9000")
#    print onCommand("A0C2000060D25E020283810C580D901040F21124337069643D322672656C617465643D31F0031001010102002C53687574746C6520617374726F6E6175747320636F6D706C65746520362D686F757220737061636577616C6B0D0D0D0D0D0D0D0D0D0D0D00|9000")

    print onCommand("A0C20000AFD181AC820283810607919730071111F18B819C0405858564F97FF6102111816293008CAF13021000020200A04142434461626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261|9000")
    print onCommand("A0C20000AFD181AC820283810607911989110099898B819C0405852113F17FF6102111816293008CAF2361626162613132333435363738393041424344313233343536373839300200A0434445464748494A213132333435363738392021222324252627282920656E6464434445464748494A213132333435363738392021222324252627282920656E6464434445464748494A213132333435363738392021222324252627282920656E646443444546474444|9000")
    print onCommand("A0C20000AFD181AC820283810607911989110099898B819C0405852113F17FF6102111816293008CAF33434445464748494A213132333435363738392021222324252627282920656E6464434445464748494A213132333435363738392021222324252627282920656E6464434445464748494A213132333435363738392021222324252627282920656E6464434445464744440D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0DD0D0D0D0D0D0D0DD00D0|9000")


# initialization
recreate('./Celltick.html')
global_id = 0

# run()
