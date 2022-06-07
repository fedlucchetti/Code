TARGET=client server
normal: $(TARGET)
client: client.cpp
	gcc -Wall client.cpp -o client
server: server.cpp
	gcc -Wall server.cpp -o server
clean:
	$(RM) $(TARGET)
