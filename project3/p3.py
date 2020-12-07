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


    def handle_connect():
        print("handling connect")
        # These are all connection objects
        browser_to_proxy = establish or pass in from caller function)
        proxy_to_dest = establish or pass in from caller function)

        while True:
            if new_data_from_browser:
                forward_to_dest

            if new_data_from_proxy:
                forward_to_browser



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
        logp("Binded on host " + str(HOST) + " on port " + str(PORT_NUM))
        while True:
            """
            # TODO: make sure connection obj works as we think and a port won't be doubly used. might need to maintain a global list of ports
            if new request:
                threading.thread or whatever handle_request(connection_object, req)
                thread( funct_name, args=[]) something like this
    
            """
            conn, addr = s.accept()
            res = conn.recv(1024)
            if res:
                print(res.decode().split('\n')[0])
                handle_request(res, conn)


def handle_request(res, conn):
    host, port, req_type, http_msg = parse_request(res)
    if req_type == "CONNECT":
        logp("Starting CONNECT thread")
        _thread.start_new_thread(handle_connect, (host, port, http_msg, conn))
    else:
        logp("Starting non_CONNECT thread")
        _thread.start_new_thread(handle_non_connect, (host, port, http_msg, conn))
    pass


# Returns the host, port, user_agent, req_type
def parse_request(res):
    logp("Parsing request")
    res_decoded = res.decode()

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
                    split_i = i - 1
                    break

            # If port is not there, use 80. If https:// is present, use 443
            if split_i > PORT_MAX_LENGTH:
                port = 80
                if line.find('https://') != -1:
                    port = 443
            else:
                host = host[:len(host) - split_i]
                print("host " + host)
                port = int(host[-split_i + 1:])

            # Get rid of http[s]s
            if host.find('http://') != -1:
                host = host.split('http://')[1]
            elif host.find('https://') != -1:
                host = host.split('https://')[1]

            # Get rid of anything after the /
            if host.find('/') != -1:
                host = host.split('/')[0]

            http_msg += split[0] + " " + split[1] + " HTTP/1.0\r\n"
        elif line.find('Proxy-Connection') != -1:
            http_msg += "Proxy-Connection: close\r\n"
        elif line.find('Connection') != -1:
            http_msg += "Connection: close\r\n"
        else:
            http_msg += line

    logp("Returning from parse request " + host + " " + str(port) + " " + req_type + " " + http_msg)
    return (host, port, req_type, http_msg)


def logp(str):
    print(HOST_NAME + " " + str)


def handle_non_connect(host, port, http_msg, conn):
    logp("handling non-connect " + host + " " + str(port))
    logp("In handle non connect " + str(port))
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            ba = BitArray()
            ba.append(http_msg.encode('utf-8'))
            s.send(ba.tobytes())
            response = s.recv(2048)
            logp("Response from server " + response.decode())
            if response:
                conn.send(response)
            s.close()
            conn.close()
        break


def handle_connect(host, port, http_msg, conn):
    pass

if __name__ == "__main__":
    run()


