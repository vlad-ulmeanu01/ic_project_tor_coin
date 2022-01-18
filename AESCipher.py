import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


#https://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256
class AESCipher:
    def __init__(self, key: int):
        self.bs = AES.block_size
        self.key = hashlib.sha256(str(key).encode()).digest() #self.key este bytes.

    def encrypt(self, raw: str) -> bytes:
        raw = self._pad(raw)
        iv = b'\x00' * 16
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc: bytes) -> str:
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s: str) -> str:
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s: bytes) -> bytes:
        return s[:-ord(s[len(s)-1:])]