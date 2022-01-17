import ProjectDefinitions
import asyncio
import random
import copy
import time

"""
NetworkNode: nod din retea.
"""
class NetworkNode:
    def __init__ (self, networkBoss: "NetworkNode"):
        self.networkNodesSet = set()
        self.networkNodes = []
        self.value = 0
        #TODO hash secret pentru identificarea tranzactiei curente.
        #TODO ledger cu informatii despre alte tranzactii.

        # adaug adresa noului nod in ledgerele celorlalte noduri.

        if networkBoss == None:
            self.value = ProjectDefinitions.NETWORK_BOSS_INIT_VALUE
            self.networkNodesSet.add(self)
            self.networkNodes.append(self)
        else:
            for othNode in networkBoss.networkNodes:
                if othNode != networkBoss:
                    othNode.networkNodesSet.add(self)
                    othNode.networkNodes.append(self)

            networkBoss.networkNodesSet.add(self)
            networkBoss.networkNodes.append(self)

            self.networkNodesSet = networkBoss.networkNodesSet.copy()
            self.networkNodes = networkBoss.networkNodes[::] #copy.deepcopy(networkBoss.networkNodes)
            pass


    """
    @self vrea sa ii dea lui @recipient @amount. Doar functia aceasta poate fi apelata
    de catre client, nu si backendTransact.
    """
    def frontendTransact (self, recipient: "NetworkNode", amount: int):
        print(f"(DEBUG frontendTransact) {self} -> {recipient}")
        for _ in range(amount):
            #transfer 1 unitate cate 1 unitate.
            #pt DEBUG pun amount unitati de fiecare data inl de 1
            self.backendSubValue(1, spendTime = False)
            self.backendTransact(recipient, 1)



    """
    @self trebuie sa ii dea lui @recipient @amount.
    @self are o sansa ?? sa ii dea direct lui @recipient banii si
    o sansa 1 - ?? sa ii dea @amount altui nod din retea si sa il roage pe el
    sa apeleze transact cu aceiasi parametri.
    """
    def backendTransact (self, recipient: "NetworkNode", amount: int):
        self.backendAddValue(amount)

        if self == recipient:
            return

        self.backendSubValue(amount)

        if random.random() < ProjectDefinitions.RAND_THRESHOLD_DIRECT_TRANSACTION:
            recipient.backendTransact(recipient, amount)
            return

        othNode = random.choice(self.networkNodes) #aleg alt nod din retea.
        #TODO trebuie sa alegi othNode pe care nu l-ai mai ales deja.

        othNode.backendTransact(recipient, amount)



    """
    """
    def backendAddValue (self, amount: int, spendTime = None):
        if spendTime == None:
            time.sleep(random.uniform(ProjectDefinitions.TIME_WAIT_LOW_BOUND,
                                      ProjectDefinitions.TIME_WAIT_HI_BOUND))
        self.value += amount
        #TODO trebuie bagat in ledgere informatia.
        print(f"(DEBUG backendAddValue) {self} primeste {amount} bani.")



    """
    """
    def backendSubValue (self, amount: int, spendTime = None):
        #assert(self.value >= amount)
        #TODO trebuie sa verifici din ledgerele celorlalti daca ai destul value
        #ca sa scazi amount.

        if spendTime == None:
            time.sleep(random.uniform(ProjectDefinitions.TIME_WAIT_LOW_BOUND,
                                      ProjectDefinitions.TIME_WAIT_HI_BOUND))
        self.value -= amount
        #TODO trebuie bagat in ledgere informatia.
        print(f"(DEBUG backendSubValue) {self} pierde {amount} bani.")



    def getValue (self):
        return self.value
