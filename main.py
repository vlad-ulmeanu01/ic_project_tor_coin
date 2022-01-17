import threading

from NetworkNode import NetworkNode
import ProjectDefinitions



def main():
    networkBoss = NetworkNode(None)
    nodes = [NetworkNode(networkBoss) for _ in range(ProjectDefinitions.NETWORK_NODE_COUNT)]

    print("Adresele nodurilor din retea:")
    print(f"networkBoss: {networkBoss}")
    for _ in range(ProjectDefinitions.NETWORK_NODE_COUNT):
        print(f"node number {_}: {nodes[_]}")

    threads = []

    threads.append(threading.Thread(target = networkBoss.frontendTransact,
                                    args = (nodes[5], 3)))
    threads.append(threading.Thread(target = networkBoss.frontendTransact,
                                    args = (nodes[11], 7)))
    threads.append(threading.Thread(target = nodes[11].frontendTransact,
                                    args = (nodes[7], 2)))
    threads.append(threading.Thread(target = nodes[5].frontendTransact,
                                    args = (nodes[7], 1)))
    threads.append(threading.Thread(target = networkBoss.frontendTransact,
                                    args = (nodes[8], 5)))

    for th in threads:
        th.start()

    for th in threads:
        th.join()

    print("Valorile din noduri dupa tranzactii:")
    print(f"networkBoss amount: {networkBoss.getValue()}")
    for _ in range(ProjectDefinitions.NETWORK_NODE_COUNT):
        print(f"node number {_}: {nodes[_].getValue()}")



if __name__ == "__main__":
    main()