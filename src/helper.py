def ConfigSectionMap(Config, section):
    dict1 = {}
    options = Config.options(section)
    
    for option in options:
        
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def addDistinct(self, newElem):
    try:
        self.index(newElem)
    except ValueError:
        self.append(newElem)
    
def apduTypeName(apduType):
    if (apduType == 0):
        return "Confirmed Request" 
    elif (apduType == 1):
        return "Unconfirmed Request"
    elif (apduType == 2):
        return "Simple ACK" 
    elif (apduType == 3):
        return "Complex ACK"
    elif (apduType == 4):
        return "Segmented ACK" 
    elif (apduType == 5):
        return "Error"
    elif (apduType == 6):
        return "Reject" 
    elif (apduType == 7):
        return "Abort"
    else:
        return "Unkown Service Type " + apduType

def objectTypeName(stringName):
        if (stringName == 'analogInput') : return 0 
        if (stringName ==  'analogOutput') : return 1
        if (stringName ==  'analogValue') : return 2
        if (stringName ==  'binaryInput') : return 3
        if (stringName ==  'binaryOutput') : return 4
        if (stringName ==  'binaryValue') : return 5
        if (stringName ==  'calendar') : return 6
        if (stringName ==  'command') : return 7
        if (stringName ==  'device') : return 8
        if (stringName ==  'eventEnrollment') : return 9
        if (stringName ==  'file') : return 10
        if (stringName ==  'group') : return 11
        if (stringName ==  'loop') : return 12
        if (stringName ==  'multiStateInput') : return 13
        if (stringName ==  'multiStateOutput') : return 14
        if (stringName ==  'notificationClass') : return 15
        if (stringName ==  'program') : return 16
        if (stringName ==  'schedule') : return 17
        if (stringName ==  'averaging') : return 18
        if (stringName ==  'multiStateValue') : return 19
        if (stringName ==  'trendLog') : return 20
        if (stringName ==  'lifeSafetyPoint') : return 21
        if (stringName ==  'lifeSafetyZone') : return 22
        if (stringName ==  'accumulator') : return 23
        if (stringName ==  'pulseConverter') : return 24
        if (stringName ==  'eventLog') : return 25
        if (stringName ==  'globalGroup') : return 26
        if (stringName ==  'trendLogMultiple') : return 27
        if (stringName ==  'loadControl') : return 28
        if (stringName ==  'structuredView') : return 29
        if (stringName ==  'accessDoor') : return 30
        if (stringName ==  'accessCredential') : return 32
        if (stringName ==  'accessPoint') : return 33
        if (stringName ==  'accessRights') : return 34
        if (stringName ==  'accessUser') : return 35
        if (stringName ==  'accessZone') : return 36
        if (stringName ==  'credentialDataInput') : return 37
        if (stringName ==  'networkSecurity') : return 38
        if (stringName ==  'bitstringValue') : return 39
        if (stringName ==  'characterstringValue') : return 40
        if (stringName ==  'datePatternValue') : return 41
        if (stringName ==  'dateValue') : return 42
        if (stringName ==  'datetimePatternValue') : return 43
        if (stringName ==  'datetimeValue') : return 44
        if (stringName ==  'integerValue') : return 45
        if (stringName ==  'largeAnalogValue') : return 46
        if (stringName ==  'octetstringValue') : return 47
        if (stringName ==  'positiveIntegerValue') : return 48
        if (stringName ==  'timePatternValue') : return 49
        if (stringName ==  'timeValue') : return 50        
        return None
    

def apduServiceName(apduType, apduService):
    if (apduType == 0) or (apduType == 2) or (apduType == 3):
        if (apduService == 0):
            return "Acknowledge Alarm"
        elif (apduService == 1):
            return "COV Notification"
        elif (apduService == 2):
            return "Event Notification"
        elif (apduService == 3):
            return "Get Alarm Summary"
        elif (apduService == 4):
            return "Get Enrollment Summary"
        elif (apduService == 29):
            return "Get Event Information"
        elif (apduService == 5):
            return "Subscribe COV"
        elif (apduService == 28):
            return "Subscribe COV Property"
        elif (apduService == 27):
            return "Life Safety Operation"
        elif (apduService == 6):
            return "Atomic Read File"
        elif (apduService == 7):
            return "Atomic Write File"
        elif (apduService == 8):
            return "Add List Element"
        elif (apduService == 9):
            return "Remove Liste Element"
        elif (apduService == 10):
            return "Create Object"
        elif (apduService == 11):
            return "Delete Object"
        elif (apduService == 12):
            return "Read Property"
        elif (apduService == 13):
            return "Read Prop Conditional"
        elif (apduService == 14):
            return "Read Prop Multiple"
        elif (apduService == 26):
            return "Read Range"
        elif (apduService == 15):
            return "Write Property"
        elif (apduService == 16):
            return "Write Prop Multiple"
        elif (apduService == 17):
            return "Device Communication Protocol"
        elif (apduService == 18):
            return "Private Transfer"
        elif (apduService == 19):
            return "Text Message"
        elif (apduService == 20):
            return "Reinitialize Device"
        elif (apduService == 21):
            return "VT Open"
        elif (apduService == 22):
            return "VT Close"
        elif (apduService == 23):
            return "VT Data"
        elif (apduService == 24):
            return "Authenticate"
        elif (apduService == 25):
            return "Request Key"
        else:
            return "Unknown Service ID " + str(apduService)
    elif (apduType == 1):
        if (apduService == 0):
            return "I Am"
        elif (apduService == 1):
            return "I Have"
        elif (apduService == 2):
            return "COV Notification"
        elif (apduService == 3):
            return "Event Notification"
        elif (apduService == 4):
            return "Private Transfer"
        elif (apduService == 5):
            return "Text Message"
        elif (apduService == 6):
            return "Time Synchronization"
        elif (apduService == 7):
            return "Who Has"
        elif (apduService == 8):
            return "Who is"
        elif (apduService == 9):
            return "UTC Time Synchronization"
        else:
            return "Unknown Service ID " + str(apduService)
    elif (apduType == 4):
        return "Unknown Service ID " + str(apduService) 
    elif (apduType == 5):
        return "Unknown Service ID " + str(apduService)
    elif (apduType == 6):
        return "Unknown Service ID " + str(apduService)
    elif (apduType == 7):
        return "Unknown Service ID " + str(apduService)
    else:
        return "Unkown Service Type " + apduType
