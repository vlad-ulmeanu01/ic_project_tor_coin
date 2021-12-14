import multiprocessing

from NetworkNode import NetworkNode
import proj_def



def main():
    networkBoss = NetworkNode(None)
    nodes = [NetworkNode(networkBoss) for _ in range(proj_def.NETWORK_NODE_COUNT)]

    print("Adresele nodurilor din retea:")
    print(f"networkBoss: {networkBoss}")
    for _ in range(proj_def.NETWORK_NODE_COUNT):
        print(f"node number {_}: {nodes[_]}")

    processes = []

    processes.append(multiprocessing.Process(target = networkBoss.frontendTransact,
                                            args = (nodes[5], 3)))
    processes.append(multiprocessing.Process(target = networkBoss.frontendTransact,
                                            args = (nodes[11], 7)))
    processes.append(multiprocessing.Process(target = nodes[11].frontendTransact,
                                            args = (nodes[7], 2)))
    processes.append(multiprocessing.Process(target = nodes[5].frontendTransact,
                                            args = (nodes[7], 1)))
    processes.append(multiprocessing.Process(target = networkBoss.frontendTransact,
                                            args = (nodes[8], 5)))

    for proc in processes:
        proc.start()

    for proc in processes:
        proc.join()

    print("Valorile din noduri dupa tranzactii:")
    print(f"networkBoss amount: {networkBoss.getValue()}")
    for _ in range(proj_def.NETWORK_NODE_COUNT):
        print(f"node number {_}: {nodes[_].getValue()}")



if __name__ == "__main__":
    main()