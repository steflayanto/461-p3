import sys
import threading, _thread
from bitstring import BitArray
import socket
import asyncio


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
        # s.settimeout(2)
        s.bind((HOST, PORT_NUM))
        s.listen()
        logp("Bound on host " + str(HOST) + " on port " + str(PORT_NUM))
        while True:
            """
            # TODO: make sure connection obj works as we think and a port won't be doubly used. might need to maintain a global list of ports
            if new request:
                threading.thread or whatever handle_request(connection_object, req)
                thread( funct_name, args=[]) something like this
    
            """
            conn, addr = s.accept()
            res = conn.recv(1024) # recieve on a separate thread
            if res:
                # print(res.decode().split('\n'))
                handle_request(res, conn)


def handle_request(res, conn):
    host, port, req_type, http_msg = parse_request(res)
    if req_type == "CONNECT":
        logp("Starting CONNECT thread")
        _thread.start_new_thread(handle_connect, (host, port, http_msg, conn))
    else:
        logp("Starting non_CONNECT thread")
        _thread.start_new_thread(handle_non_connect, (host, port, http_msg, conn))
    # pass


# Returns the host, port, req_type, http_msg
def parse_request(res):
    logp("Parsing request")
    res_decoded = res.decode()
    # print("<<<", res_decoded, ">>>")
    req_type = None
    host = None
    port = None
    http_msg = ""
    lines = res_decoded.split('\r\n')
    for i, line in enumerate(lines):
        if i == 0:
            
            split = line.split(' ')
            # print(split)
            req_type = split[0]
            
            # Parse host
            host = split[1]


            if host.find('http://') != -1:
                protocol = 'http://'
                host = host.replace('http://','')


            elif host.find('https://') != -1:
                protocol = 'https://'
                host = host.replace('https://','')
            else:
                protocol = ""

            if ':' in host:
                host, port = split[1].split(':')  # could contain port
                try:
                    port = int(port)
                except:
                    port = 80
            else:
                port  = 80

            slash_idx = host.find('/')

            if slash_idx != -1:
                resource = host[slash_idx:]
                host = host[:slash_idx]
                # print("separated {} and {}".format(host, resource))
            else:
                resource = "/"

            http_msg += split[0] + " " + protocol + host + resource + " HTTP/1.0\r\n"

        elif line.find('Proxy-Connection') != -1:
            http_msg += "Proxy-Connection: close\r\n"
        elif line.find('Connection') != -1:
            http_msg += "Connection: close\r\n"
        elif line.find('Host') != -1:
            http_msg += "Host: " + host + "\r\n"
        # elif 'Upgrade-Insecure-Requests:' in line:
            # http_msg += "Upgrade-Insecure-Requests: 0\r\n"
        else:
            http_msg += line + "\r\n"
    http_msg += "\r\n"
    print("original-------------------")
    print(res_decoded)
    print("modified-------------------")
    print(http_msg)
    logp("Returning from parse request " + host + " " + str(port) + " " + req_type + " msg:" + http_msg)
    # print(">>>", req_type, host)
    # req_type = "non_connect"
    return (host, port, req_type, http_msg)
    # return (host, port, req_type, res_decoded)


def logp(str):
    print(HOST_NAME + " " + str)
    # pass


def handle_non_connect(host, port, http_msg, conn):
    logp("handling non-connect " + host + " " + str(port))
    # logp("In handle non connect " + str(port))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        logp("After connect")
        ba = BitArray()
        ba.append(http_msg.encode('utf-8'))
        s.send(ba.tobytes())
        while True:
            response = s.recv(1024)
            logp("Response from server " + response.decode(errors='ignore'))
            if response:
                conn.send(response)
            else:
                break
        s.close()
        conn.close()

# handles msg async
def response_handler(conn_recv, conn_send):
    while True:
        try:
            resp = conn_recv.recv(1024)
            if resp:
                conn_send.send(resp)
            else:
                print("Breaking due to nothing recieved")
                conn_send.close()
                break
        except Exception as e:
            print("Breaking due to exception:",e)
            conn_send.close()
            break
    return False


def handle_connect(host, port, http_msg, conn):

    # return None
    # host = host.split(":")[0]
    # port = 80
    print("handling connect")
    # These are all connection objects
    browser_to_proxy = conn
    # browser_to_proxy.settimeout(2)
    proxy_to_dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # proxy_to_dest.settimeout(2)
    try:
        proxy_to_dest.connect((host, port))
    except Exception as e:
        print("Unable to establish connection with host: {} port: {} exception: {}".format(host, port, e))
        resp = "HTTP/1.0 502 BAD GATEWAY\r\nContent-Type: text/html\r\n\r\n"
        browser_to_proxy.send(resp.encode('utf-8'))
        return None
    
    print("Established connection with host")
    
    # ACK the browser
    resp = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"
    browser_to_proxy.send(resp.encode('utf-8'))

    # Forward request to des
    proxy_to_dest.send(http_msg.encode('utf-8'))

    _thread.start_new_thread(response_handler, (browser_to_proxy, proxy_to_dest))
    _thread.start_new_thread(response_handler, (proxy_to_dest, browser_to_proxy))
    # response_handler(browser_to_proxy, proxy_to_dest)
    # response_handler(proxy_to_dest, browser_to_proxy)
    
    # print("Connection terminated.")
    # browser_to_proxy.close()
    # proxy_to_dest.close()
    return None
    while browser_to_proxy and proxy_to_dest:
        forward = response_handler(browser_to_proxy, proxy_to_dest)
        backward = response_handler(proxy_to_dest, browser_to_proxy)
        # if forward 
        # print("Waiting on browser")
        # try:
        #     while True:
        #         browser_response = browser_to_proxy.recv(1024)
        #         if browser_response:
        #             # Pull header
        #             # print(browser_response.decode(encoding='ASCII', errors='ignore'))
        #             # print("--------------------------")
        #             # print(browser_response.decode(encoding='UTF-8', errors='ignore'))
        #             # print(browser_response.decode(errors="ignore"))
        #             proxy_to_dest.send(browser_response)
        #         else:
        #             print("Empty response from browser")
        #             break
        # except:
        #     print("nothing received from browser")

        # print("Waiting on dest")
        # try:
        #     while True:
        #         dest_response = proxy_to_dest.recv(1024)
        #         # logp("Response from server " + response.decode())
        #         if dest_response: # Forward to client
        #             # print(dest_response.decode(errors="ignore"))
        #             browser_to_proxy.send(dest_response)
        #         else:
        #             print("Empty response from dest")
        #             break
        # except:
        #     print("nothing received from dest")
        # # pass
    
    # CLEANUP


if __name__ == "__main__":
    run()


