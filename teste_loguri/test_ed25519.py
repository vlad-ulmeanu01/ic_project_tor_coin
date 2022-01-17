import TwistedEdwardsMODEC
import ModuloOps

#curba TwistedEdwards Ed25519 este folosita de Monero.
#mod = 2^255 - 19.
#a = -1.
#d = -121665/121666

modOps = ModuloOps.ModuloOps((1<<255) - 19)

edmec = TwistedEdwardsMODEC.TwistedEdwardsMODEC(-1 + modOps.mod,
            (-121665 + modOps.mod) * modOps.inv_mod(121666) % modOps.mod,
            modOps.mod)

print(f"a: {edmec.a}, d: {edmec.d}")

#2,  6, 7,  10, 11, 12,  14, 15, 16, 17,  24, 25, 26, 27, 28, 29,  31, 32,  34, 35,  37, 38, ...
#ex pt x = 3 ysq ^ ((mod-1) / 2) != 1 modulo mod. ysq din getYs(3) (quadratic non-residue.)

p1 = (15112221349535400772501151409588531511454012693041857206046113283949847762202,
      46316835694926478169428394003475163141307993866256225615783033603165251855960)
#p1 generator cu ordinul 8 * 7237005577332262213973186563042994240857116359379907606001950938285454250989
#                            ^^ prim.

"""
x = 38
p1 = (x, edmec.getYs(x)[0])

print(p1)
"""

for i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 20, 100, 1000, 10000):
    print(f"{p1} * {i} = {edmec.scalarMul(p1, i)}")
    print(f"is on curve? {edmec.isPointOnCurve(edmec.scalarMul(p1, i))}")
