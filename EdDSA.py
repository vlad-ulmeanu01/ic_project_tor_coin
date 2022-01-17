import hashlib

import TwistedEdwardsMODEC
import ModuloOps


#semneaza si verifica mesaje folosind Ed25519.
class EdDSA:
    def __init__(self, generator: tuple, generatorOrder: int,
                 edmec: TwistedEdwardsMODEC, modOps: ModuloOps):
        self.generator = generator
        self.generatorOrder = generatorOrder
        self.edmec = edmec
        self.modOps = modOps




    def sign(self, msg: str, privKey: int, pubKey: tuple) -> tuple:
        msgDigest = self.convertHexStrToInt(hashlib.sha256(msg.encode()).hexdigest())

        r = self.convertHexStrToInt(hashlib.sha256(str(privKey + msgDigest).encode()).hexdigest()) %\
            self.generatorOrder

        R = self.edmec.scalarMul(self.generator, r)

        h = self.convertHexStrToInt(hashlib.sha256(str(self.edmec.compressPoint(R) +
                                                       self.edmec.compressPoint(pubKey) +
                                                       msgDigest).encode()).hexdigest()) %\
            self.generatorOrder

        s = (r + h * privKey) % self.generatorOrder

        return (R, s)



    def verify(self, msg: str, signature: tuple, pubKey: tuple) -> bool:
        R, s = signature

        msgDigest = self.convertHexStrToInt(hashlib.sha256(msg.encode()).hexdigest())

        h = self.convertHexStrToInt(hashlib.sha256(str(self.edmec.compressPoint(R) +
                                                       self.edmec.compressPoint(pubKey) +
                                                       msgDigest).encode()).hexdigest()) %\
            self.generatorOrder

        P1 = self.edmec.scalarMul(self.generator, s)
        P2 = self.edmec.add(R, self.edmec.scalarMul(pubKey, h))

        return P1 == P2
        


    def convertHexStrToInt(self, s: str) -> int:
        ans = 0
        for ch in s:
            if ord(ch) >= ord('0') and ord(ch) <= ord('9'):
                ans = ans * 16 + ord(ch) - ord('0')
            else:
                assert(ord(ch) >= ord('a') and ord(ch) <= ord('f'))
                ans = ans * 16 + ord(ch) - ord('a') + 10
        return ans