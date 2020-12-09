import sys
import threading, _thread
from bitstring import BitArray
import socket


"""

Two flows:
    Non-connect
        1. Establish incoming connection from browser
        2. Receive request
        3. Modify & forward to destination
        4. Receive from destination
        5. Send to browser

    Connect
        1. Establish incoming TCP connection from browser
        2. Establish outgoing TCP connection with destination
        3. Continually act as pass-through

    def handle_non_connect(browser_to_proxy):
        print("handling non-connect")
        # These are all connection objects
        browser_to_proxy = establish or pass in from caller function)

        while True: or while connection is open
            if new_data_from_browser:
                reformat packet
                dest_response = send_request_to_destination
                edit response
                brower_to_proxy.send (edited response)



"""
HOST = '127.0.0.1'
HOST_NAME = "[Proxy server]"
PORT_MAX_LENGTH = 5

def run():
    if len(sys.argv) != 2:
        logp("Usage: python p3.py <port_num>")
        return
    
    try:
        PORT_NUM = int(sys.argv[1])
    except:
        logp("Usage: python p3.py <port_num>")
        return


    # bind to socket, just like p1
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT_NUM))
        s.listen()
        logp("Proxy listening on " + str(HOST) + ":" + str(PORT_NUM))
        while True:

            conn, addr = s.accept()
            _thread.start_new_thread(handle_request, (conn,))


def handle_request(conn):
    try:
        res = conn.recv(1024)
    except:
        return None
    # if res:
    #     print(res.decode().split('\n')[0])
    try:
        host, port, req_type, http_msg = parse_request(res)
    except:
        return None
    if req_type == "CONNECT":
        # logp("Starting CONNECT thread")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

        conn.send(b'HTTP/1.0 200 OK\r\n\r\n')

        threads = []
        thread_two = threading.Thread(target=handle_connect, args=(s, conn))
        thread_one = threading.Thread(target=handle_connect, args=(conn, s))
        threads.append(thread_one)
        threads.append(thread_two)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # print("joined")
    else:
        # logp("Starting non_CONNECT thread")
        _thread.start_new_thread(handle_non_connect, (host, port, http_msg, conn))


# Returns the host, port, req_type, http_msg
def parse_request(res):
    # logp("Parsing request")
    res_decoded = res.decode(errors='ignore')

    req_type = None
    host = None
    port = None
    http_msg = ""
    lines = res_decoded.split('\n')
    for i, line in enumerate(lines):
        if i == 0:
            split = line.split(' ')

            req_type = split[0]
            
            host = split[1]  # could contain port
            

            split_i = 0
            for i, c in enumerate(reversed(host)):
                if c == ":":
                    split_i = i
                    break

            # If port is not there, use 80. If https:// is present, use 443
            if split_i > PORT_MAX_LENGTH or host.find(':') == -1:
                port = 80
                if line.find('https://') != -1:
                    port = 443
            else:
                temp = host
                host = host[:len(host) - (split_i + 1)]
                port = int(temp[-split_i:])

            # Get rid of http[s]s
            if host.find('http://') != -1:
                host = host.split('http://')[1]
            elif host.find('https://') != -1:
                host = host.split('https://')[1]

            # Get rid of anything after the /
            if host.find('/') != -1:
                host = host.split('/')[0]

            http_msg += split[0] + " " + host + " HTTP/1.0\r\n"
        elif line.find('Proxy-Connection') != -1:
            http_msg += "Proxy-Connection: close\r\n"
        elif line.find('Connection') != -1:
            http_msg += "Connection: close\r\n"
        else:
            http_msg += line + "\n"

    # logp("Returning from parse request " + host + " " + str(port) + " " + req_type + " " + http_msg)
    print(">>> {} {}".format(req_type, host))
    return (host, port, req_type, http_msg)


def logp(str):
    print(HOST_NAME + " " + str)


def handle_non_connect(host, port, http_msg, conn):
    # logp("handling non-connect " + host + " " + str(port))
    # logp("In handle non connect " + str(port))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        # logp("After connect")
        ba = BitArray()
        ba.append(http_msg.encode())
        s.send(ba.tobytes())
        while True:
            response = s.recv(1024)
            if response:
                conn.send(response)
            else:
                break
        s.close()
        conn.close()


def handle_connect(src, dst):
    while True:
        data = None
        try:
            data = src.recv(1024)
            # print("data " + str(len(data)))
        except Exception as e:
            # print(e)
            break

        if data:
            dst.send(data)
        else:
            break
    dst.close()


if __name__ == "__main__":
    run()


