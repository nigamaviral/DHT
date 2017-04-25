# DHT

For mid-term report:
- All functionalities of chord
    - find_successor()
    - fix_fingers()
    - stabilize()
    ...
- Less Fault Tolerance (1 successor)
- Single copy of data
- Single Virtual Node per Physical Node


For final report:
- Multiple successors (simple task).
- Multiple copies of data (simple task).
- Possibly multiple virtual nodes inside a physical node for better load balance.
- Some analysis based on finger table size, etc. can be done.


Current implementation plan:
----------------------------
- An application to launch the chord network
- It takes 1 argument: n -> to create n nodes in mininet

- Hash function: SHA-1
- Size of finger table: log base 2 of 160 (because keys are distributed among 160 bits)


- This application gives an interface with following options:
    1. Add a node
    2. Remove a node
    3. Lookup an item (will be asynchronous) - Dont Think So
    4. Insert an item (will be asynchronous) - Dont Think So
    5. Display current network - What does this mean ?
    6. Display finger table (for debugging)
    7. Display pending requests - What does this mean ?
    8. Exit


Adding new node to chord network:
- Makes mininet request to add a node.
- Pushes the new node into chord network by calling join() of some random node in the existing network.
- Newly joined node calls stabilize() and notify() as described in paper.


Removing a node from chord network:
- Follow the algorithm as described in paper.
- Since each node monitors its finger table entries, eventually network becomes stabilized.


Lookup and insert:
- 2 kinds of request:
    - client request (CR)
    - node-to-node request (NR)
	
- The main application chooses one of the random nodes to make a client request (CR)
- This node spawns a new thread to handle the request and stores connection details in a map
- This thread makes an appropriate request (NR) looking into finger table
- If the request fails, then it continues to request the node 1 behind in the finger table.  - What does this mean ?
- If everything fails, returns key not found. Otherwise, closes the current thread and keeps the connection open.
- Once it receives back the answer, it passes the answer appropriate client by looking into map.
- When a node receives NR request, it follows same steps as mentioned above, but doesn't store any details about the connection.
- When does lookup stop ?
