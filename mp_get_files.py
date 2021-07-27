import serial
import sys
import glob
import re
import binascii

READ_BUFFER_SIZE = 1024
MP_CONSOLE_MAGIC = b'>>> '

def write_remove_echo(s, str):
    s.write(str)
    s.read(len(str))

def remove_echo(s):
    s.read(READ_BUFFER_SIZE)

def read_to_the_end(s):
    full_read = bytearray()
    read_buffer = bytearray()
    end = -1
    while end < 0:
        end = read_buffer.find(MP_CONSOLE_MAGIC)
        read_buffer = s.read(READ_BUFFER_SIZE)
        full_read += read_buffer
        if len(full_read) == 0:
            break

        print('.', end='', flush=True)
    print('')
    return full_read

def find_mp_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    else:
        raise EnvironmentError('Unsupported platform')

    mp_ports = []
    for port in ports:
        try:
            s = serial.Serial(port=port, timeout=2)
            write_remove_echo(s, b'\r\n')
            ret = read_to_the_end(s)
            if(ret == MP_CONSOLE_MAGIC):
                mp_ports.append(port)
            s.close()
        except (OSError, serial.SerialException):
            pass
    return mp_ports

def relist(text):
    exp = '\'(.*?)\''
    list = re.findall(exp, text.decode())
    return list

def list_files(s):
    write_remove_echo(s, b'import os\r\n')
    write_remove_echo(s, b'os.listdir()\r\n')
    ret = read_to_the_end(s)
    return relist(ret[:-6])

def get_file(file):
    write_remove_echo(s, f'f = open(\'{file}\', \'rb\')\r\n'.encode())
    write_remove_echo(s, b'while True:\r\n')
    write_remove_echo(s, b'd = f.read(1024)\r\n')
    write_remove_echo(s, b'\'\'.join(\'{:02x}\'.format(x) for x in d)\r\n')
    write_remove_echo(s, b'if not d:\r\n')
    write_remove_echo(s, b'break\r\n')
    write_remove_echo(s, b'\r\n\r\n\r\n')
    ret = read_to_the_end(s).replace(b"\'\r\n\'", b"")[:-7]
    ret = ret[ret.find(b'\r\n\'')+3:]
    open(file, 'wb').write(binascii.unhexlify(ret))

if __name__ == "__main__":
    files_list = []
    s = None

    ports = find_mp_ports()

    if len(ports):
        print(f"Available ports: {ports}")
        if len(ports) > 1:
            port = input(f"Choose the MicroPython port you would like to use: ")
        else:
            port = ports[0]
            
        s = serial.Serial(port=port, timeout=2)
        files_list = list_files(s)
    else:
        print("Did not find MicroPython boards")
        exit()
    

    if len(files_list):
        while(True):
            n = 0
            for file in files_list:
                print(f"{n}: {file}")
                n +=1

            last_file = len(files_list)-1
            choice = sys.maxsize
            while(int(choice) > len(files_list)):
                choice = input(f"Which file do you want to fetch? [0-{last_file}]: ")
            
            chosen_file = files_list[int(choice)]
            print(f"Fetching {chosen_file}")
            f = get_file(chosen_file)
            print(f"{chosen_file} fetched!")
    else:
        print("Board is empty")