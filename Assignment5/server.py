import sys
from collections import namedtuple
import time
import string
import re, binascii

def IptoInt(address):
    binaryStr = ''
    chunkList = address.split('.')
    for chunk in chunkList:
        binChunk = '{0:08b}'.format(int(chunk))
        binaryStr += binChunk
    ipInt = int(binaryStr,2)
    return ipInt

Rule = namedtuple('Rule', 'direction action ip bottomIp topIp ports flag')
rules = []

if __name__ == "__main__":
    # getting the arguments when server is running with no options
    rulesFile = sys.argv[1]
    
    # Reading config file and store the rules to the rule list
    file = open(rulesFile, 'r')
    for line in file:
        ruleList = line.split()
        if ruleList[0][0]=="#":
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
            addressNum = 32-int(host)
            addressNum = 2**addressNum
            bottomRange = IptoInt(subnet)
            topRange = bottomRange+addressNum
        else:
            bottomRange = 0
            topRange = 0

#        print(direction,action,ip,port,flag);
        rules.append(Rule(direction,action,ip,bottomRange,topRange,ports,flag))

    file.close()

    for line in sys.stdin:
        printed = False
        pDirection, pIp, pPort, pFlag = line.split()
        intPip = IptoInt(pIp)
        for idx,rule in enumerate(rules):
#            print('ports result:', pPort in rule.ports, '   ip results:', ( rule.ip == '*' or ((rule.bottomIp <= intPip) and (intPip < rule.topIp))), '  bottomRange:',rule.bottomIp,'   IP:',intPip,'   topRange:',rule.topIp,'  direction results:', rule.direction == pDirection)
            if rule.direction == pDirection and ( rule.ip == '*' or (rule.bottomIp <= intPip and intPip <rule.topIp)) and (rule.ports[0] == '*' or pPort in rule.ports):
#                print('passed the loop')
                if rule.flag == 'established':
                    if pFlag == '1':
#                        print(rule.bottomIp, '>=', intPip,'<',rule.topIp)
                        print(rule.action, '('+str(idx+1)+')', pDirection, pIp, pPort, pFlag)
                        print()
                        printed = True
                        break
                    else:
                        continue
                else:
                    #handle all packets
#                    print(rule.bottomIp, '>=', intPip,'<',rule.topIp)
                    print(rule.action, '('+str(idx+1)+')', pDirection, pIp, pPort, pFlag)
                    print()
                    printed = True
                    break
            else:
                continue
        if not printed:
#            print(rule.bottomIp, '>=', intPip,'<',rule.topIp)
            print('drop()', pDirection, pIp, pPort, pFlag)
            print()



