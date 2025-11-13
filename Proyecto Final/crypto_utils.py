from Crypto.PublicKey import RSA
from Crypto.Hash import SHAKE128
from Crypto.Util.number import bytes_to_long, long_to_bytes, inverse
import random

class CryptoManager:
    def __init__(self):
        # Generamos la llave maestra de la "Autoridad Electoral" (Admin)
        # En un sistema real, estas llaves se cargarían de un archivo seguro.
        self.admin_key = RSA.generate(2048)
        self.admin_pub = self.admin_key.publickey()

    def get_admin_pub_params(self):
        """Devuelve (n, e) para que el usuario pueda cegar el voto"""
        return (self.admin_pub.n, self.admin_pub.e)

    def generate_user_keys(self):
        """Genera par de llaves para el usuario nuevo"""
        key = RSA.generate(2048)
        return key.export_key(), key.publickey().export_key()

    def hash_msg(self, message):
        """Uso de SHAKE128 para obtener un hash numérico"""
        shake = SHAKE128.new(message.encode('utf-8'))
        # Leemos 64 bytes para alta seguridad
        return bytes_to_long(shake.read(64))

    # --- PROTOCOLO DE FIRMA CIEGA ---

    def blind_message(self, message, pub_n, pub_e):
        """
        CLIENTE: Cega el mensaje.
        m' = (H(m) * r^e) mod n
        """
        m = self.hash_msg(message)
        r = random.randint(2, pub_n - 1) # Factor de cegado aleatorio
        
        # r^e mod n
        blind_factor = pow(r, pub_e, pub_n)
        # m * r^e mod n
        m_blinded = (m * blind_factor) % pub_n
        
        return m_blinded, r

    def sign_blinded(self, m_blinded):
        """
        SERVIDOR: Firma el mensaje cegado sin verlo.
        s' = (m')^d mod n
        """
        # Usamos la llave privada del admin (d)
        s_blinded = pow(m_blinded, self.admin_key.d, self.admin_key.n)
        return s_blinded

    def unblind_signature(self, s_blinded, r, pub_n):
        """
        CLIENTE: Quita el factor de cegado para obtener la firma válida.
        s = s' * r^(-1) mod n
        """
        r_inv = inverse(r, pub_n)
        s = (s_blinded * r_inv) % pub_n
        return s

    def verify_signature(self, message, signature, pub_n, pub_e):
        """
        URNA: Verifica s^e mod n == H(m)
        """
        m_hash = self.hash_msg(message)
        # Verificación matemática RSA pura
        hash_from_sig = pow(int(signature), pub_e, pub_n)
        return hash_from_sig == m_hash