# Maya4ok's File Transfer v1.1.0

A simple application for transferring files over a network using **Tkinter** for interface and **Socket** for network transfer. The program allows you to send and receive files between two devices on a local network or through open ports.

## How to use

1. **Starting the server**: On the first device from which the file will be downloaded, you need to start the server.
2. **File Transfer**: On the second device, open the program and receive the file.

**Important**: For the program to work correctly, ports must be open on one of the devices, or you must use a local network.

## Features

- **Multithreading**: Files are transferred in a separate thread, which allows you not to block the interface.
- **Transmission progress**: You can monitor the file transfer process using progress indicators.
- **Saving the IP address**: The recipient's IP address is saved for reuse.
- **Error handling**: The program carefully handles possible errors, for example, if a file is not selected or a connection error occurred.
- **Interface**: The interface style has been updated, now it looks even more convenient.

## Contributions

If you want to make changes or improvements, make a fork of the project and send a pull request.
