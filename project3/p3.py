import sys


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

def run():
    if len(sys.argv) != 2:
        print("Usage: python p3.py <port_num>")
        return
    
    try:
        PORT_NUM = int(sys.argv[1])
    except:
        print("Usage: python p3.py <port_num>")
        return

    
    # bind to socket, just like p1

    while True:
        # Listen for requests, spawn a new thread for each one

        """
        # TODO: make sure connection obj works as we think and a port won't be doubly used. might need to maintain a global list of ports
        if new request:
            threading.thread or whatever handle_request(connection_object, req)
            thread( funct_name, args=[]) something like this

        """

def handle_request(connection_obj, req):
    # host, req_type, req_addr, additional fields as necessary = parse_request(req)

    # detect type of request, handle based on type
    if connect is True:
        handle_connect(connection_obj)
        connection_obj.close()
    else:
        create tcp to destination connection obj
        handle_non_connect(connection_obj, tcp to destination obj) # doesn't return until done
        connection_obj.close()
        tcp_to_dest.close()

    pass

def parse_request(req):
    pass
    # return host, req_type, additional fields as necessary


run()
