class ModuloOps:
    def __init__(self, mod: int):
        self.mod = mod

    #(a^b) modulo self.mod
    def lgput(self, a: int, b: int) -> int:
        ans, p2 = 1, 1
        while b:
            if b & p2:
                ans = ans * a % self.mod
                b ^= p2
            a = a * a % self.mod
            p2 <<= 1
        return ans



    def gcd(self, a: int, b: int) -> int:
        if b == 0:
            return a
        return self.gcd(b, a%b)



    #ret (x, y) ai a*x + b*y = cmmdc(a, b)
    def gcd_ex(self, a: int, b: int) -> tuple:
        if b == 0:
            return (1, 0)
        x, y = self.gcd_ex(b, a%b)
        return (y, x - (a // b) * y)



    #daca vreau inversul modular al lui a fata de m, am nevoie de (a, m) = 1.
    #pt (a, m), gcd_ex gaseste (x, y) ai a * x + m * y = (a, m) = 1
    #(y o sa iasa negativ) => (a * x) mod m = 1 => x este inversul modular al lui a fata de m.
    def inv_mod(self, a: int) -> int:
        assert(self.gcd(a, self.mod) == 1)
        x = self.gcd_ex(a, self.mod)[0]
        if x < 0:
            x += self.mod * ((-x + self.mod - 1) // self.mod)
            
        assert(a * x % self.mod == 1)

        return x

    def sqrt(self, x: int) -> int:
        #r = ? ai r * r modulo mod = x.
        #2^255 - 19 mod 8 = 5 (https://www.rieselprime.de/ziki/Modular_square_root)
        #si fix de pe https://math.stackexchange.com/questions/518120/how-to-prove-algorithm-for-solving-a-square-congruence-when-p-%E2%89%A1-5-mod-8

        assert(self.mod & 7 == 5) # self.mod % 8 == 5.

        #Euler: x are "radacina" de ordin 2 modulo mod <-> x^((mod-1)/2) modulo mod = 1.
        assert(self.lgput(x, (self.mod - 1) >> 1) == 1)

        #cum mod = multiplu 8 + 5 => 4 | mod-1.
        #=> x^((mod-1)/4) modulo mod = +- 1.

        if self.lgput(x, (self.mod - 1) >> 2) == 1:
            return self.lgput(x, (self.mod + 3) >> 3)
            #r = x ^ ((mod+3)/8) => r^2 = x ^ ((mod+3)/4).
            #(mod+3) / 4 = (mod-1)/4 + 1. dar x^((mod-1)/4) modulo mod = 1 => r^2 modulo mod = x.

        #aici x^((mod-1)/4) modulo mod = -1.
        assert(self.lgput(x, (self.mod - 1) >> 2) == self.mod - 1)

        #cica 2^((mod-1)/2) modulo mod = -1
        #deci inmultesc r din if-ul de mai sus cu 2^((mod-1)/4) astfel incat (r_nou)^2 = -x * -1 = x (modulo mod).

        return self.lgput(x, (self.mod + 3) >> 3) * self.lgput(2, (self.mod - 1) >> 2) % self.mod