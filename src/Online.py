from SocketWrapper import *
from InputParser import InputParser
from Board import Board
import sys

PORT_NUMBER = 1972

WHITE = True
BLACK = False

def makeMove(move, board):
    print("Making move : " + move.notation)
    board.makeMove(move)

def runOnlineServer(name="White"):
    host = getLocalIP()
    try:
        s = bindSocket(host, PORT_NUMBER, 0)
    except OSError:
        print("Error starting online game, are you already hosting a game?")
        sys.exit()
    print()
    print("Hosting on {}".format(host))
    print("Waiting for opponent to connect...")
    print()
    connection = None
    try:
        connection, addr = accept(s)

        print("Welcoming connection from {}".format(addr[0]))

        sendMessage(connection, name, addr)
        recieved = waitForMessage(connection)
        if recieved:
            print("Connected to {}!".format(recieved))
            opponentName = recieved
        else:
            print("Connection denied")
            closeSocket(s)
            sys.exit()

        #Setup game
        board = Board()
        parserWhite = InputParser(board, WHITE)
        parserBlack = InputParser(board, BLACK)

        while True:
            print()
            print(board)
            print()
            if board.isCheckmate():
                print("Checkmate! You lose!")
                sendMessage(connection, "checkmate")
                closeSocket(connection)
                return
            elif board.isStalemate():
                print("Stalemate! It's a draw")
                sendMessage(connection, "stalemate")
                closeSocket(connection)
                return
            else:
                sendMessage(connection, str(board))

            while True:
                move = None
                command = input("It's your move, {}. Move ? ".format(name))
                try:
                    move = parserWhite.parse(command)
                    break
                except ValueError as error:
                    print("%s" % error)
                    continue
            makeMove(move, board)
            print()
            print(board)
            print()
            if board.isCheckmate():
                print("Checkmate! You win!")
                sendMessage(connection, "checkmate")
                closeSocket(connection)
                return
            elif board.isStalemate():
                print("Stalemate! It's a draw!")
                sendMessage(connection, "stalemate")
                closeSocket(connection)
                return

            sendMessage(connection, str(board))
            print("Waiting for {} to move...".format(opponentName))
            while True:
                opponentMove = waitForMessage(connection)
                try:
                    move = parserBlack.parse(opponentMove)
                    sendMessage(connection, "ok")
                    break
                except:
                    sendMessage(connection, "error")
            makeMove(move, board)
        closeSocket(connection)
    except KeyboardInterrupt:
        if connection:
            closeSocket(connection)
    except BrokenPipeError:
        print("You were disconnected")
        if connection:
            closeSocket(connection)
        sys.exit()

def connectOnlineServer(host, name="Black"):
    try:
        s = connectSocket(host, PORT_NUMBER)
    except:
        choice = input("Host didn't respond. " 
                    "Search local network for a host [Yn] ? ").lower()
        if 'y' in choice:
            s = None
        else:
            sys.exit()
    if s is None:
        subnet = '192.168.1.'
        hostsAttempted = 0
        for i in range(0, 256):
            try:
                host = subnet + str(i)
                print("Trying to connect to {}".format(host))
                s = connectSocket(host, PORT_NUMBER)
                break
            except KeyboardInterrupt:
                sys.exit()
            except:
                s = None
                hostsAttempted += 1
        if s is None:
            print("{} hosts attempted, none were available".format(hostsAttempted))
            sys.exit()        
    try:
        print()
        print("Connecting to {}".format(host))
        recieved = waitForMessage(s)

        if recieved:
            print("Connected to {}!".format(recieved))
            opponentName = recieved
            sendMessage(s, name)
        else:
            print("Connection denied")
            closeSocket(s)
            sys.exit()

        while True:
            msg = waitForMessage(s)
            if msg in ("stalemate", "checkmate"):
                if msg == "checkmate":
                    print("Checkmate! You win!")
                elif msg == "stalemate":
                    print("Stalemate! It's a draw")
                closeSocket(s)
                return
            if not msg:
                print("Opponent disconnected.")
                closeSocket(s)
                sys.exit()

            print()
            print(msg)
            print()
            print("Waiting for {} to move...".format(opponentName))
            msg = waitForMessage(s)
            if msg in ("stalemate", "checkmate"):
                if msg == "checkmate":
                    print("Checkmate! You lose!")
                elif msg == "stalemate":
                    print("Stalemate! It's a draw")
                closeSocket(s)
                return
            if not msg:
                print("Opponent disconnected.")
                closeSocket(s)
                sys.exit()

            print()
            print(msg) #Got opponent's move
            print()
            while True:
                command = input("It's your move, {}. Move ? ".format(name))
                sendMessage(s, command)
                response = waitForMessage(s)
                if response == 'ok':
                    break
                else:
                    print("Invalid move.")
        closeSocket(s)
    except KeyboardInterrupt:
        closeSocket(s)
    except BrokenPipeError:
        print("You were disconnected")
        closeSocket(s)
        sys.exit()
