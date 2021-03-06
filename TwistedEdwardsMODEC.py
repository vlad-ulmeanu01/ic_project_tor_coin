import ModuloOps

class TwistedEdwardsMODEC:
    def __init__(self, a: int, d: int, mod: int):
        self.a = a
        self.d = d
        self.mod = mod
        self.modOps = ModuloOps.ModuloOps(mod)



    #y = ? ai ax^2 + y^2 = 1 + dx^2y^2.
    def getYs(self, x: int) -> int:
        #ysq = (a*x*x - 1) / (d*x*x - 1) AOELU iar ai incurcat ordinea..

        ysq = (self.a * x % self.mod * x % self.mod - 1) % self.mod
        ysq = ysq * self.modOps.inv_mod((self.d * x % self.mod * x % self.mod - 1) % self.mod) % self.mod

        y1 = self.modOps.sqrt(ysq)
        
        return (y1, -y1 % self.mod)



    def isPointOnCurve(self, point: tuple) -> bool:
        x, y = point
        y1, y2 = self.getYs(x)
        return y == y1 or y == y2


    #calculez point1 + point2.
    def add(self, point1: tuple, point2: tuple) -> tuple:
        x1, y1 = point1
        x2, y2 = point2
        dxyprod = self.d * x1 % self.mod * x2 % self.mod * y1 % self.mod * y2 % self.mod

        #x3 = (x1*y2 + y1*x2) / (1 + self.d * x1*x2*y1*y2)
        #y3 = (y1*y2 - self.a*x1*x2) / (1 - self.d * x1*x2*y1*y2)

        x3 = (x1 * y2 % self.mod + y1 * x2 % self.mod) % self.mod
        x3 = x3 * self.modOps.inv_mod((1 + dxyprod) % self.mod) % self.mod

        y3 = (y1 * y2 % self.mod - self.a * x1 % self.mod * x2 % self.mod) % self.mod
        y3 = y3 * self.modOps.inv_mod((1 - dxyprod) % self.mod) % self.mod

        return (x3, y3)

    #calculez point * k = point + point + .. + point de k ori.
    def scalarMul(self, point: tuple, k: int) -> tuple:
        ans = (0, 1) #element neutru.
        p2 = 1

        while k:
            if k & p2:
                ans = self.add(ans, point)
                k ^= p2

            point = self.add(point, point)
            p2 <<= 1

        return ans

    def compressPoint(self, point: tuple) -> int:
        #cum pot sa folosesc 256 de biti, iar toate numerele sunt >= 0 && < 2^255-19 < 2^255 =>
        #=> mai am un bit gol. curba Ed25519 este simetrica atat fata de Ox, cat si fata de Oy.
        #folosesc bitul suplimentar pentru a spune daca punctul este dedesubt/peste Ox.
        #(1 bit) sub/peste + 255 biti coord x.
        if point[1] == self.getYs(point[0])[0]:
            return point[0] #msb este 0.
        return point[0] | (1<<255) #msb este 1.

    def decompressPoint(self, compressedPoint: int) -> tuple:
        side = compressedPoint & (1<<255)
        compressedPoint ^= side #acum compressedPoint == x.
        
        y1, y2 = self.getYs(compressedPoint)
        if side == 0:
            return (compressedPoint, y1)
        return (compressedPoint, y2)
