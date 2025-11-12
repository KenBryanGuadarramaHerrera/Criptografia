import rsa

# Generar par de llaves RSA de 2048 bits
public_key, private_key = rsa.newkeys(2048)

# Guardar la clave privada del servidor
with open('authority_private.pem', 'wb') as f:
    f.write(private_key.save_pkcs1())

# Guardar la clave pública del servidor
with open('authority_public.pem', 'wb') as f:
    f.write(public_key.save_pkcs1())

print("✅ Llaves de Autoridad generadas: authority_private.pem y authority_public.pem")
