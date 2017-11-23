import sys
from collections import namedtuple
import time
import string
import re, binascii

def IptoBinary(address):
    binaryStr = ''
    chunkList = address.split('.')
    for chunk in chunkList:
        binChunk = '{0:08b}'.format(int(chunk))
        binaryStr += binChunk
    return binaryStr

Rule = namedtuple('Rule', 'direction action ip host subnet ports flag')
rules = []

if __name__ == "__main__":
    # getting the arguments when server is running with no options
    rulesFile = sys.argv[1]
    
    # Reading config file and store the rules to the rule list
    file = open(rulesFile, 'r')
    for line in file:
        ruleList = line.split()
        if ruleList:
            if ruleList[0][0]=="#":
                rules.append(Rule(None,None,None,None,None,None,None))
                continue

            elif len(ruleList)==4:
                direction = ruleList[0]
                action = ruleList[1]
                ip = ruleList[2]
                ports = ruleList[3].split(',')
                flag = ''

            elif len(ruleList)==5:
                direction = ruleList[0]
                action = ruleList[1]
                ip = ruleList[2]
                ports = ruleList[3].split(',')
                flag = ruleList[4]
                if not flag == 'established':
                    continue
            else:
                break

            if not ip == '*':
                subnet,host=ip.split('/')
                subnet = IptoBinary(subnet)
            else:
                host = ''
                subnet = 0

            rules.append(Rule(direction,action,ip,host,subnet,ports,flag))
                
        else:
            rules.append(Rule(None,None,None,None,None,None,None))
        

    file.close()

    for line in sys.stdin:
        printed = False
        pDirection, pIp, pPort, pFlag = line.split()
        binaryPip = IptoBinary(pIp)
        for idx,rule in enumerate(rules):
            if rule.action == None:
                continue
            
            if rule.direction == pDirection and ( rule.ip == '*' or (rule.subnet[:int(rule.host)] == binaryPip[:int(rule.host)])) and (rule.ports[0] == '*' or pPort in rule.ports):
                if rule.flag == 'established':
                    if pFlag == '1':
                        print(rule.action, '('+str(idx+1)+')', pDirection, pIp, pPort, pFlag)
#                        print()
                        printed = True
                        break
                    else:
                        continue
                else:
                    #handle all packets
                    print(rule.action, '('+str(idx+1)+')', pDirection, pIp, pPort, pFlag)
#                    print()
                    printed = True
                    break
            else:
                continue
        if not printed:
            print('drop()', pDirection, pIp, pPort, pFlag)
#            print()



