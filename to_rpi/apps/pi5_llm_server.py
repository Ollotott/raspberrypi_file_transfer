import ollama
import socket
import os


def restart():
    os.system("sudo python /home/moi/llm_test.py")
    exit()


try:
    # Set up the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("socket set up!")
    server_socket.bind(('0.0.0.0', 12345))  # Use an available port
    server_socket.listen(1)  # Listen for a single connection

    print("Main Pi: Waiting for connection...")

    # Accept a connection
    client_socket, client_address = server_socket.accept()
    print(f"Main Pi: Connected to client. {client_address}")

    while True:
        # get prompt
        prompt = client_socket.recv(1024).decode()
        print(prompt)

        if prompt.lower() == "/end" or prompt.lower() == "/bye":
            print("ended communication.")
            # Close the connection
            client_socket.close()
            server_socket.close()
            exit("Ended Communication!")

        stream = ollama.chat(model='tinyllama', messages=[{'role': 'user', 'content': prompt}], stream=True,)

        for item in stream:
            print(item["message"]["content"])
            client_socket.send(item["message"]["content"].encode())

            if item["done"]:
                client_socket.send("ans-end".encode())

except OSError:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.close()
    restart()
    exit()
