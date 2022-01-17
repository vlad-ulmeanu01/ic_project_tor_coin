import hashlib

import TwistedEdwardsMODEC
import ModuloOps



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



modOps = ModuloOps.ModuloOps((1<<255) - 19)

edmec = TwistedEdwardsMODEC.TwistedEdwardsMODEC(-1 + modOps.mod,
            (-121665 + modOps.mod) * modOps.inv_mod(121666) % modOps.mod,
            modOps.mod)

eddsa = EdDSA((15112221349535400772501151409588531511454012693041857206046113283949847762202, 46316835694926478169428394003475163141307993866256225615783033603165251855960),
              8 * 7237005577332262213973186563042994240857116359379907606001950938285454250989,
              edmec,
              modOps)

s = "HoI!"
privKey = 69420
pubKey = edmec.scalarMul((15112221349535400772501151409588531511454012693041857206046113283949847762202, 46316835694926478169428394003475163141307993866256225615783033603165251855960), privKey)

signature = eddsa.sign(s, privKey, pubKey)
print(signature)
print(eddsa.verify(s, signature, pubKey))


"""
def convertHexStrToInt(s):
    ans = 0
    for ch in s:
        if ord(ch) >= ord('0') and ord(ch) <= ord('9'):
            ans = ans * 16 + ord(ch) - ord('0')
        else:
            assert(ord(ch) >= ord('a') and ord(ch) <= ord('f'))
            ans = ans * 16 + ord(ch) - ord('a') + 10
    return ans

print(convertHexStrToInt(hashlib.sha256("HoI!".encode()).hexdigest()))
"""