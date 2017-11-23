import sys
from collections import namedtuple
import time
import string
import re, binascii

#Function to compute the 32 bit binary of the ip address
def IptoBinary(address):
    binaryStr = ''
    chunkList = address.split('.')
    for chunk in chunkList:
        binChunk = '{0:08b}'.format(int(chunk))
        binaryStr += binChunk
    return binaryStr

# Tuple for rules
Rule = namedtuple('Rule', 'direction action ip host subnet ports flag')

# List of all rules
rules = []

if __name__ == "__main__":
    # getting the arguments when server is running with no options
    rulesFile = sys.argv[1]
    
    # Reading config file and store the rules to the rule list
    file = open(rulesFile, 'r')
    for line in file:
        ruleList = line.split()
        # If there is something in the ruleslist
        if ruleList:
            # if there is a line with a comment, set rule to none
            if ruleList[0][0]=="#":
                rules.append(Rule(None,None,None,None,None,None,None))
                continue
            
            # If there is not flag in the rule, set flag to empty
            elif len(ruleList)==4:
                direction = ruleList[0]
                action = ruleList[1]
                ip = ruleList[2]
                ports = ruleList[3].split(',')
                flag = ''
            
            # If there is a flag, set the flag in the rule
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

            # If the ip address is not a wild card, split the CIDR address, and get the binary ip
            if not ip == '*':
                subnet,host=ip.split('/')
                subnet = IptoBinary(subnet)
            # Otherwise, set host to empty and subnet to 0
            else:
                host = ''
                subnet = 0
                
            # Store the rule to the rules list
            rules.append(Rule(direction,action,ip,host,subnet,ports,flag))
                
        # If ruleslist is empty, set rule to none
        else:
            rules.append(Rule(None,None,None,None,None,None,None))
        
    # Close the file
    file.close()

    # Start reading from the standard input
    for line in sys.stdin:
        
        # Flag to see if the packet is already printed put
        printed = False
        
        # Get the packet info from the line
        pDirection, pIp, pPort, pFlag = line.split()
        
        # Get the packet's binary ip address
        binaryPip = IptoBinary(pIp)
        
        # loop through all the rules
        for idx,rule in enumerate(rules):
            
            # if the action specified in the rule is none do nothing
            if rule.action == None:
                continue
        
            # See if a rule applies to a packet
            if rule.direction == pDirection and ( rule.ip == '*' or (rule.subnet[:int(rule.host)] == binaryPip[:int(rule.host)])) and (rule.ports[0] == '*' or pPort in rule.ports):
                
                # if the rule's flag is established
                if rule.flag == 'established':
                    # See if the packets flag is also established
                    if pFlag == '1':
                        # Print the rule
                        print(rule.action, '('+str(idx+1)+')', pDirection, pIp, pPort, pFlag)
                        # set flag to ture and come out of the loop
                        printed = True
                        break
                    else:
                        continue
                else:
                    #Print the rule and set printed to true
                    print(rule.action, '('+str(idx+1)+')', pDirection, pIp, pPort, pFlag)
                    printed = True
                    break
            else:
                continue
        
        # If no rule applies to the packet, drop it
        if not printed:
            print('drop()', pDirection, pIp, pPort, pFlag)



