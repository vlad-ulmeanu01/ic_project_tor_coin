import random
import time

import TwistedEdwardsMODEC
import ProjectDefinitions
import ModuloOps
import EdDSA

"""
NetworkNode: nod din retea.
"""
class NetworkNode:
    def __init__(self, networkBoss: "NetworkNode"):

        #ajutor functii modulo.
        self.modOps = ModuloOps.ModuloOps((1<<255) - 19)

        #clasa cu functii Ed25519. a = -1, d = -121665 / 121666
        self.edmec = TwistedEdwardsMODEC.TwistedEdwardsMODEC(-1 + self.modOps.mod,
                        (-121665 + self.modOps.mod) * self.modOps.inv_mod(121666) % self.modOps.mod,
                        self.modOps.mod)

        #punct ales ca generator pentru curba.
        self.edGenerator = (
            15112221349535400772501151409588531511454012693041857206046113283949847762202,
            46316835694926478169428394003475163141307993866256225615783033603165251855960)

        #ordinul puncutului ales ca generator in clasa modulor 2^255-19.
        self.edGeneratorOrder = 8 * 7237005577332262213973186563042994240857116359379907606001950938285454250989
        
        #cheie secreta folosita in comunicare = scalar din clasa de resturi Z/modZ
        self.commPrivKey = random.randint(1, self.modOps.mod - 1)

        #cheie publica folosita in comunicare = punct de pe curba Ed25519 = priv * G.
        self.commPublicKey = self.edmec.scalarMul(self.edGenerator, self.commPrivKey)



        #clasa semnare/verificare
        self.eddsa = EdDSA.EdDSA(self.edGenerator, self.edGeneratorOrder,
                                 self.edmec, self.modOps)

        #cheie secreta folosita in semnarea mesajelor.
        self.signPrivKey = random.randint(1, self.modOps.mod - 1)

        #cheie publica folosita in verificarea mesajelor de alte noduri (ca au fost semnate de nodul asta)
        self.signPublicKey = self.edmec.scalarMul(self.edGenerator, self.signPrivKey)






        #set cu adresele nodurilor din retea.
        self.networkNodesSet = set()

        #vector cu adresele nodurilor din retea.
        self.networkNodes = []

        #valoarea nodului din retea.
        self.value = 0

        #chei private de schimb Diffie-Hellman folosind curba eliptica Ed25519.
        #hashmap-ul contine perechi de tip (adresa nod din retea, cheie privata de schimb)
        #pt un nod 'NetworkNode object at 0xA' care contine o pereche tip
        # ('NetworkNode object at 0xB', 555) => A, B comunica intre ei folosind cheia simetrica 555.
        self.dhExchangeKeys = {}

        #TODO hash secret pentru identificarea tranzactiei curente.
        #TODO ledger cu informatii despre alte tranzactii.

        # adaug adresa noului nod in ledgerele celorlalte noduri.

        if networkBoss == None:
            self.value = ProjectDefinitions.NETWORK_BOSS_INIT_VALUE
            self.networkNodesSet.add(self)
            self.networkNodes.append(self)
        else:
            for othNode in networkBoss.networkNodes:
                #generez cheile private de comunicare DH.
                self.generateCommKey(othNode)
                othNode.generateCommKey(self)

                #adaug adresa noului nod in multimile nodurilor deja existente.
                if othNode != networkBoss:
                    #networkBoss nu este inclus aici ptc nu vreau sa modific lista prin care iterez.
                    othNode.getNetworkNodesSet().add(self)
                    othNode.getNetworkNodes().append(self)

            networkBoss.getNetworkNodesSet().add(self)
            networkBoss.getNetworkNodes().append(self)

            self.networkNodesSet = networkBoss.getNetworkNodesSet().copy()
            self.networkNodes = networkBoss.getNetworkNodes()[::] #copy.deepcopy(networkBoss.networkNodes)


    """
    @self vrea sa ii dea lui @recipient @amount. Doar functia aceasta poate fi apelata
    de catre client, nu si backendTransact.
    """
    def frontendTransact(self, recipient: "NetworkNode", amount: int):
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
    def backendTransact(self, recipient: "NetworkNode", amount: int):
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
    def backendAddValue(self, amount: int, spendTime = None):
        if spendTime == None:
            time.sleep(random.uniform(ProjectDefinitions.TIME_WAIT_LOW_BOUND,
                                      ProjectDefinitions.TIME_WAIT_HI_BOUND))
        self.value += amount
        #TODO trebuie bagat in ledgere informatia.
        print(f"(DEBUG backendAddValue) {self} primeste {amount} bani.")



    """
    """
    def backendSubValue(self, amount: int, spendTime = None):
        #assert(self.value >= amount)
        #TODO trebuie sa verifici din ledgerele celorlalti daca ai destul value
        #ca sa scazi amount.

        if spendTime == None:
            time.sleep(random.uniform(ProjectDefinitions.TIME_WAIT_LOW_BOUND,
                                      ProjectDefinitions.TIME_WAIT_HI_BOUND))
        self.value -= amount
        #TODO trebuie bagat in ledgere informatia.
        print(f"(DEBUG backendSubValue) {self} pierde {amount} bani.")



    """
    genereaza cheia Diffie-Hellman EC care trebuie folosita de self si otherNode.
    functia baga cheia comuna DOAR in dictionarul lui self, otherNode TREBUIE sa apeleze si el functia din
    partea lui pentru a afla cheia comuna.
    """
    def generateCommKey(self, otherNode: "NetworkNode"):
        if otherNode in self.getDhExchangeKeys():
            return

        self.getDhExchangeKeys()[otherNode] = self.edmec.scalarMul(
            otherNode.getPublicCommKey(),
            self.commPrivKey
        )



    """
    de aici in jos sunt doar gettere si settere.
    """
    def getPublicCommKey(self):
        return self.commPublicKey

    def getNetworkNodesSet(self):
        return self.networkNodesSet

    def getNetworkNodes(self):
        return self.networkNodes

    def getValue(self):
        return self.value
    
    def getDhExchangeKeys(self):
        return self.dhExchangeKeys
