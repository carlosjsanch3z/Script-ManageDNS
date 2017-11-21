#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, commands

# Check args
def checkargvs(num):
    if num > 1 and num <= 5:
        return True
    else:
        return False

# Check first parameter
def firstparameter(f):
    if f == '-a' or f == '-b':
        return True
    else:
        return False

# Add entry type A
def AddEntryDir(name, ip):
    ips = ip.split('.')
    a = ('%s         IN      A       %s'%(name, ip))
    # Add the name on DNS direct
    commands.getoutput('echo "%s" >> /etc/bind/db.charlie.gonzalonazareno.org'%a)
    # Detect Network
    if ips[0] == '172' and ips[1] == '22':
        ptr = ('%s.%s           IN      PTR     %s'%(ips[3],ips[2], name))
        commands.getoutput('echo "%s" >> /etc/bind/db.172.22'%ptr)
    elif ips[0] == '10' and ips[1] == '0' and ips[2] == '0':
        ptr = ('%s       IN      PTR      %s'%(ips[3], name))
        commands.getoutput('echo "%s" >> /etc/bind/db.10.0.0'%ptr)
    else:
        exit("Rare address.\nUse: 172.22.X.X or 10.0.0.X")
    RestartService()


# Add entry type alias

def AddEntryAlias(alias, name):
    cname = ('%s         IN      CNAME       %s'%(alias, name))
    commands.getoutput('echo "%s" >> /etc/bind/db.charlie.gonzalonazareno.org'%cname)
    RestartService()

# Delete entry (A o Alias)

def DelEntry(name):
    # Save variables
    data = commands.getoutput('cat /etc/bind/db.charlie.gonzalonazareno.org|egrep "^%s"'%name)
    attributes = data.split()
    # If list is empty then list == 'empty'
    if attributes:
        e_type = attributes[2]
    else:
        e_type = 'empty'

    if e_type == 'A':
        # If type A, get NETWORKING and Delete it on his zone reverse
        ip = attributes[3]
        Init = ip.split(".")
        if Init[0] == '172':
            ptr = commands.getoutput('cat /etc/bind/db.172.22|egrep ".*PTR.*%s"'%name)
            commands.getoutput('sed -i".temp" \'/%s/ d\' /etc/bind/db.172.22'%ptr)

        elif Init[0] == '10':
            ptr = commands.getoutput('cat /etc/bind/db.10.0.0|egrep ".*PTR.*%s"'%name)
            commands.getoutput('sed -i".temp" \'/%s/ d\' /etc/bind/db.10.0.0'%ptr)

        # Delete entry type A and his Alias
        # "-i" create a temporary file before do the delete
        commands.getoutput('sed -i".temp" \'/%s/ d\' /etc/bind/db.charlie.gonzalonazareno.org'%name)

    elif e_type == 'CNAME':
        # Delete Alias only
        commands.getoutput('sed -i".temp" \'/%s/ d\' /etc/bind/db.charlie.gonzalonazareno.org'%name)
    else:
        exit('Not found: %s'%name)
    RestartService()


# Reload service DNS without restart
def RestartService():
    commands.getoutput('rndc reload')


# Start program
# Check privileges
if os.geteuid() == 0:
    # Check how many argvs
    if checkargvs(len(sys.argv)):
        # Check -a or -b
        if firstparameter(sys.argv[1]):
            # If type -a
            if sys.argv[1] == '-a':
                # If there is no 4: ERROR
                if len(sys.argv) <= 4:
                    exit("!Need more parameters!\nExample: GestionaDNS.py -a -dir/alias {name} {IP/name}")
                # If there are 4 parameters : WORKS
                elif sys.argv[2] == '-dir' or sys.argv[2] == '-alias' and len(sys.argv) == 5:
                    if sys.argv[2] == '-dir':
                        AddEntryDir(sys.argv[3],sys.argv[4])
                    elif sys.argv[2] == '-alias':
                        AddEntryAlias(sys.argv[3],sys.argv[4])
                else:
                    exit("Need more parameters!")
            # If type -b
            elif sys.argv[1] == '-b':
                if len(sys.argv) == 3:
                    ## Delete entry + Alias + Ip's zones
                    DelEntry(sys.argv[2])
                else:
                    exit("You must write a name for delete it.\nExample: GestionaDNS.py -b {name}")
        else:
            exit("The first parameter must be '-a' or '-b'!")
    else:
        exit("You need write any argument!")
else:
    exit("You need to have root privileges to run this script!")
