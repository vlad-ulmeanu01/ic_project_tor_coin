import random
from collections import deque

import TwistedEdwardsMODEC
import ProjectDefinitions
import ModuloOps
import EdDSA
import AESCipher

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
        #semnatura <=> "Nodul C -> Nodul D <hash tranzactie emis de A>".
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

        #coada cu tranzactii in asteptare. tranzactiile pleaca 2 cate 2 => nu mai este clar pentru o parte
        #terta care valuta in care parte s-a dus.
        self.transactionsQueue = deque()

        #chei private de schimb Diffie-Hellman folosind curba eliptica Ed25519.
        #hashmap-ul contine perechi de tip (adresa nod din retea, cheie privata de schimb)
        #pt un nod 'NetworkNode object at 0xA' care contine o pereche tip
        # ('NetworkNode object at 0xB', 555) => A, B comunica intre ei folosind cheia simetrica 555.
        self.dhExchangeKeys = {self: 0}


        #fiecare tranzactie vine cu un hash de identificare emis de platitorul principal. hashul de
        #identificare se perinda pe la toti intermediarii si ajunge in cele din urma la destinatie.

        #nodurile intermediare au datoria de a retine hashul de identificare intr-un ledger privat
        #si de a transmite hashul mai departe in lant. ledgerul de aici trebuie sa fie privat pentru
        #ca o parte terta ar putea sa vada fluxul unui hash pentru a determina trimitatorul/destinatarul.
        #nodurile intermediare trebuie sa pastreze hashul in caz ca se demareaza o operatie de tip "blame"
        #si trebuie sa demonstreze ca au avut la un moment dat valuta cautata.
        self.privateTransactionLedger = set()

        #nodul destinatar scrie DOAR in ledgerul echivalent public. astfel, trimitatorul original poate
        #sa vada ca destinatarul a primit valuta, insa o parte terta nu poate sti cine a trimis-o. (nici
        #macar intermediarii)
        self.publicTransactionLedger = set()


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
            self.backendTransact(None, recipient, 1, None)



    """
    @self trebuie sa ii dea lui @recipient @amount.
    @self tocmai a primit @amount de la @fromWho.
    @self are o sansa ?? sa ii dea direct lui @recipient banii si
    o sansa 1 - ?? sa ii dea @amount altui nod din retea si sa il roage pe el
    sa apeleze transact cu aceiasi parametri.
    
    @message este de forma (cata valuta am primit,
                            hashul tranzactiei (singurul lucru care trb sa ramana privat),
                            semnatura specifica tranzactiei curente).
    @message este criptat cu AES256, initial value = 0, cheia folosita este deja determinata prin
    protocolul Diffie-Hellman EC.
    """
    def backendTransact(self, fromWho: "NetworkNode", recipient: "NetworkNode", amount: int,
                        encMessage: bytes):
        #fromWho == None => sunt in primul apel al tranzactiei curente, nu pot sa imi dau singur bani.
        if fromWho != None:
            #decodeaza mesajul si verifica semnatura.

            assert(fromWho in self.dhExchangeKeys)

            msg = AESCipher.AESCipher(self.dhExchangeKeys[fromWho]).decrypt(encMessage)
            msgAmount, msgTransactionHash, msgSignature = self.backendDecodeMessage(msg)

            #!!!! msg != mesajul cu care verific semnatura!!!!!
            #trebuie sa construiesc mesajul cu care verific semnatura din msg.
            msgToVerifySignature = str(msgAmount) + "|" +\
                                 str(fromWho) + "|" +\
                                 str(self) + "|" +\
                                 str(msgTransactionHash)

            assert(msgAmount == amount)
            assert(self.eddsa.verify(msgToVerifySignature, msgSignature, fromWho.getPublicSignKey()))

            #daca sunt aici inseamna ca fromWho chiar a semnat mesajul primit.
            transactionHash = msgTransactionHash
        else:
            #encMessage este si el None.
            #generez transactionHash aici.
            transactionHash = random.randint(1, (1<<256) - 1)


        if fromWho != None: #daca e prima tranzactie as aduna de la mine la mine
            self.backendAddValue(amount)

        if self == recipient:
            self.publicTransactionLedger.add(transactionHash)
            return

        self.privateTransactionLedger.add(transactionHash)

        #de aici incepe urmatoarea tranzactie pe lant.
        self.backendSubValue(amount)

        self.transactionsQueue.append((recipient, transactionHash, amount)) #ai nev si DE TRANSACTION HASH
        print(f"(DEBUG backendTransact) {self} baga in coada {amount} bani.")

        while len(self.transactionsQueue) >= 2:
            trans1 = self.transactionsQueue.popleft()
            trans2 = self.transactionsQueue.popleft()

            if random.randint(0, 1) == 1:
                #50% sansa sa amestec primele 2 tranzactii din coada.
                trans1, trans2 = trans2, trans1

            for recipient, transactionHash, amount in (trans1, trans2):
                print(f"(DEBUG backendTransact) {self} pierde {amount} bani.")

                sendTo = random.choice(self.networkNodes) #aleg alt nod din retea.
                #TODO trebuie sa alegi othNode pe care nu l-ai mai ales deja.

                if random.random() < ProjectDefinitions.RAND_THRESHOLD_DIRECT_TRANSACTION:
                    sendTo = recipient #trimit direct la destinatie.

                assert(sendTo in self.dhExchangeKeys)
                encMessageToSend = AESCipher.AESCipher(self.dhExchangeKeys[sendTo]).encrypt(
                    self.backendEncodeMessage(sendTo, amount, transactionHash)
                )

                #ai incurcat sendTo cu recipient VV ;OOOOOO
                sendTo.backendTransact(self, recipient, amount, encMessageToSend)





    """
    """
    def backendAddValue(self, amount: int):
        self.value += amount
        #TODO trebuie bagat in ledgere informatia.
        print(f"(DEBUG backendAddValue) {self} primeste {amount} bani.")



    """
    """
    def backendSubValue(self, amount: int):
        #assert(self.value >= amount)
        #TODO trebuie sa verifici din ledgerele celorlalti daca ai destul value
        #ca sa scazi amount.

        self.value -= amount
        #TODO trebuie bagat in ledgere informatia.
        #print(f"(DEBUG backendSubValue) {self} pierde {amount} bani.")
        #nu pun aici ca nu arata exact cand pleaca banii din nod.



    """
    genereaza cheia Diffie-Hellman EC care trebuie folosita de self si otherNode.
    functia baga cheia comuna DOAR in dictionarul lui self, otherNode TREBUIE sa apeleze si el functia din
    partea lui pentru a afla cheia comuna.
    """
    def generateCommKey(self, otherNode: "NetworkNode"):
        if otherNode in self.getDhExchangeKeys():
            return

        self.getDhExchangeKeys()[otherNode] = self.edmec.compressPoint(
            self.edmec.scalarMul(otherNode.getPublicCommKey(), self.commPrivKey)
        )

    """
    calculeaza in functie de self, @recipient, @amount, @transactionHash => @signature
    codeaza @amount, @transactionHash si @signature intr-un string. string-ul urmeaza sa fie trecut
    prin AES, apoi trimis altcuiva. delimitatorul folosit aici este '|'.
    """
    def backendEncodeMessage(self, recipient: "NetworkNode", amount: int, transactionHash: int) -> str:
        msg = str(amount) + "|" + str(self) + "|" + str(recipient) + "|" + str(transactionHash)

        R, s = self.eddsa.sign(msg, self.signPrivKey, self.signPublicKey)
        #self a semnat urmatorul mesaj: "self -> recipient <amount> valuta cu hash-ul tranzactiei ..."
        #(hash eliberat de trimitatorul care a inceput lantul).
        
        return str(amount) + "|" +\
               str(transactionHash) + "|" +\
               str(self.edmec.compressPoint(R)) + "|" +\
               str(s)

    """
    decodeaza un mesaj primit prin AES. tuplul are pe prima pozitie @amount, pe a doua @transactionHash,
    pe a treia un tuplu <=> cu semnatura EdDSA tip (R, s).
    """
    def backendDecodeMessage(self, message: str) -> tuple:
        amount, transactionHash, compressedR, s = map(int, message.split('|'))
        return (amount,
                transactionHash,
                (self.edmec.decompressPoint(compressedR), s))

    """
    de aici in jos sunt doar gettere si settere.
    """
    def getPublicCommKey(self):
        return self.commPublicKey

    def getPublicSignKey(self):
        return self.signPublicKey

    def getNetworkNodesSet(self):
        return self.networkNodesSet

    def getNetworkNodes(self):
        return self.networkNodes

    def getValue(self):
        return self.value

    def getDhExchangeKeys(self):
        return self.dhExchangeKeys
