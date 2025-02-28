import socket

# Set up the client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('10.20.1.80', 12345))  # pi 5 ip address

try:
    while True:
        prompt = input("Prompt:")

        # send res via socket to 10.20.1.1
        client_socket.send(prompt.encode())

        if prompt.lower() == "/end" or prompt.lower() == "/bye":
            break

        result = ""

        # get result from socket and display it.
        while True:
            temporary_receive = client_socket.recv(1024).decode()
            if temporary_receive != "ans-end":
                result += temporary_receive
            else:
                break
            print(result)

except KeyboardInterrupt:
    print("End controlled.")
    client_socket.close()

client_socket.close()
