import requests
import json
from crypto_utils import CryptoManager

# Usamos CryptoManager solo para las funciones matemáticas de ayuda (blinding/unblinding)
# pero simulamos que las llaves son del cliente.
helper = CryptoManager()

BASE_URL = "http://127.0.0.1:5000"

def main():
    print("=== SISTEMA DE VOTACIÓN ELECTRÓNICA ===")
    print("1. Registrarse")
    print("2. Votar")
    option = input("Selecciona: ")

    if option == '1':
        user = input("Usuario: ")
        pwd = input("Password: ")
        res = requests.post(f"{BASE_URL}/register", json={'username': user, 'password': pwd})
        
        if res.status_code == 200:
            data = res.json()
            print("\n[EXITO] Registro completado.")
            print("Guardando tu llave privada en 'my_key.pem'...")
            with open(f"{user}_key.pem", "w") as f:
                f.write(data['private_key_pem'])
        else:
            print("Error:", res.text)

    elif option == '2':
        user = input("Usuario para autenticar derecho a voto: ")
        pwd = input("Password: ")
        voto = input("¿Por quién votas? (Candidato A / Candidato B): ")

        # 1. Obtener parámetros públicos del servidor (n, e)
        params = requests.get(f"{BASE_URL}/public_params").json()
        n_serv = int(params['n'])
        e_serv = int(params['e'])

        # 2. CEGADO (Blinding) - Ocurre localmente
        # El servidor NUNCA ve el voto real, solo ve números aleatorios
        blinded_val, r = helper.blind_message(voto, n_serv, e_serv)
        print(f"\n[CLIENTE] Voto cegado generado: {blinded_val.__str__()[:20]}...")

        # 3. Solicitar Firma al Servidor
        payload = {
            'username': user,
            'password': pwd,
            'blinded_hash': str(blinded_val)
        }
        res = requests.post(f"{BASE_URL}/sign_blinded", json=payload)
        
        if res.status_code != 200:
            print("Error obteniendo firma:", res.json())
            return

        blinded_sig = int(res.json()['blind_signature'])
        print(f"[CLIENTE] Firma ciega recibida: {str(blinded_sig)[:20]}...")

        # 4. DESCEGADO (Unblinding) - Ocurre localmente
        real_signature = helper.unblind_signature(blinded_sig, r, n_serv)
        print(f"[CLIENTE] Firma descegada obtenida. Lista para votar.")

        # 5. Enviar voto a la urna (Anónimo)
        # Nota: Aquí NO enviamos el usuario, solo el voto y la firma
        vote_payload = {
            'vote': voto,
            'signature': str(real_signature)
        }
        res_vote = requests.post(f"{BASE_URL}/vote", json=vote_payload)
        print("\nRespuesta de la urna:", res_vote.json())

if __name__ == "__main__":
    main()