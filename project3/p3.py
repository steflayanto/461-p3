import sys
import threading, _thread
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
        conn, addr = s.accept()
        with conn:
            while True:
                """
                # TODO: make sure connection obj works as we think and a port won't be doubly used. might need to maintain a global list of ports
                if new request:
                    threading.thread or whatever handle_request(connection_object, req)
                    thread( funct_name, args=[]) something like this
        
                """
                res = conn.recv(1024)
                print(res.decode().split('\n')[0])
                handle_request(res, conn)


def handle_request(res, conn):
    host, port, user_agent, req_type = parse_request(res)
    if req_type == "CONNECT":
        handle_connect(host, port, user_agent, req_type, conn)
        conn.close()
    else:
        handle_non_connect(host, port, user_agent, req_type, conn)
        conn.close()
    pass


# Takes in data from a CONNECT or non-CONNECT and removes
# - keep-alive
# Returns the host, port, user_agent, req_type
def parse_request(res):
    logp("Parsing request")
    # split the first line into spaces and get the host + port
    res_decoded = res.decode()
    split = res_decoded.split(' ')

    req_type = split[0]
    host = split[1] # could contain port

    # If port is not there, use 80. If https:// is present, use 443
    if host.find(':') == -1:
        port = 80
        if res_decoded.find('https://') != -1:
            port = 443
    else:
        split_hp = res_decoded.split(':')
        host = split_hp[0]
        port = res_decoded.split(':')[1]

    user_agent = res_decoded.split('User-Agent: ')[1].split("\r\n")[0]

    logp("Returning from parse request " + host  + " " + port + " " + user_agent + " " + req_type)
    return (host, port, user_agent, req_type)
    # return host, port

def logp(str):
    print(HOST_NAME + " " + str)

def build_http(host, port, user_agent, req_type, opt_msg):
    logp("Building http send " + host + " " + port)
    res = req_type + " " + host + ":" + port + " " + "HTTP/1.1\r\n"
    res += user_agent + "\r\n"
    res += "Proxy-Connection: close\r\n"
    res += "Connection: close\r\n"
    res += "Host: " + host + ":" + port + "\r\n"
    res += opt_msg + "\r\n"
    pass
    # return host, req_type, additional fields as necessary

def handle_non_connect(host, port, user_agent, req_type, conn):
    logp("handling non-connect" + host + " " + port)
    # These are all connection objects
    # browser_to_proxy = establish or
    # pass in from caller function)

    # while True:
    pass

def handle_connect(host, port, user_agent, req_type, conn):
    pass

if __name__ == "__main__":
    run()


