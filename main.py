import threading
import time

from NetworkNode import NetworkNode
import ProjectDefinitions



def main():
    networkBoss = NetworkNode(None)
    nodes = [NetworkNode(networkBoss) for _ in range(ProjectDefinitions.NETWORK_NODE_COUNT)]

    print("Adresele nodurilor din retea:")
    print(f"networkBoss: {networkBoss}")
    for _ in range(ProjectDefinitions.NETWORK_NODE_COUNT):
        print(f"node number {_}: {nodes[_]}")

    for node in [networkBoss, *nodes]:
        print(f"Communication keys for node {node}: {node.getDhExchangeKeys()}")



    threads = []

    threads.append(threading.Thread(target = networkBoss.frontendTransact,
                                    args = (nodes[0], 3)))
    threads.append(threading.Thread(target = networkBoss.frontendTransact,
                                    args = (nodes[5], 7)))
    threads.append(threading.Thread(target = nodes[5].frontendTransact,
                                    args = (nodes[1], 2)))
    threads.append(threading.Thread(target = nodes[0].frontendTransact,
                                    args = (nodes[1], 1)))
    threads.append(threading.Thread(target = networkBoss.frontendTransact,
                                    args = (nodes[3], 5)))

    for th in threads:
        th.start()
        #time.sleep(1.5)

    for th in threads:
        th.join()

    print("Valorile din noduri dupa tranzactii:")
    print(f"networkBoss amount: {networkBoss.getValue()}")
    for _ in range(ProjectDefinitions.NETWORK_NODE_COUNT):
        print(f"node number {_}: {nodes[_].getValue()}")



if __name__ == "__main__":
    main()