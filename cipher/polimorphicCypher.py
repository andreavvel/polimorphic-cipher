#importando librerias relevantes
import random
import hashlib
import time
import subprocess
import json
import os

#Tabla de llaves para guardar las llaves generadas
key_table=[]
P = 0xF23456789ABCDEF  # P Constante de 64-bits
Q = 0x1234567890ABCDEF  # Q Constante de 64-bits
N = 4  # Numero de llaves a generar
#tabla de psns posibles
psn_table = {
    'a': [2, 1, 4, 3],
    'b': [1, 2, 4, 3],
    'c': [4, 3, 1, 2],
    'd': [1, 2, 3, 4],
    'e': [3, 1, 4, 2],
    }  

#funcion para obtener la información de dispositivo en el dispositivo actual
def get_deviceid():
    result = subprocess.run(["wmic", "csproduct", "get", "UUID"], stdout=subprocess.PIPE)
    device_id = result.stdout.decode().split('\n')[1].strip()[:13]
    return device_id
print(get_deviceid())

#la funcion de generacion de semilla toma el id del dispositivo, el timestamp con segundos y los concatena
#luego, se le aplica un hash sha256, con esto se convierten en un hash hexadecimal 
#esto permite suficiente aleatoriedad, ya que el tiempo se toma con segundos asi que aun siendo el mismo dispostivo y a un tiempo similar, la semilla siempre cambia
def generate_seed(device_id):
    timestamp = int(time.time())
    raw_seed = f"{device_id}{timestamp}"
    # Generar SHA-256 hash
    seed = hashlib.sha256(raw_seed.encode()).hexdigest()
    # Convertir el hash a un hexadecimal de 64-bits
    seed_int = int(seed, 16) & 0xFFFFFFFFFFFFFFFF
    return seed_int

#funciones de generacion de llaves, estas permiten mayor complejidad en el proceso de generacion de llaves

#funcion que implementa suma, pero con masking de 64-bits y un XOR con la operacion AND entre la semilla y un n primo
def scrambledfun(seed, prime1):
    return ((seed + prime1) & 0xFFFFFFFFFFFFFFFF) ^ (seed & prime1)

#funcion que genera las llaves en base al resultado de la anterior y un n primo
#implementa una suma de operaciones logicas y un masking e 64-bits para dicha suma
def generationfun(P0, prime2):
    return ((P0 ^ prime2) + (P0 >> 3)) & 0xFFFFFFFFFFFFFFFF

#funcion que muta la semilla con el segundo n primo para la siguiente llave
def mutationfun(seed, prime2):
    return ((seed ^ prime2) + (seed << 2))& 0xFFFFFFFFFFFFFFFF

#funcion de generación de generacion de tabla de llaves
def generate_key_table(seed, P, Q, N):
    """Generate a key table using the seed, constants P, Q, and N."""
    keys = []
    P0 = scrambledfun(seed, P)  # Paso 1: Generar P0
    for _ in range(N):
        key = generationfun(P0, Q)  # Paso 2: Generacion de llava usando P0 y Q
        keys.append(key)
        seed = mutationfun(seed, Q)  # Paso 3: Mutar semilla para la siguiente llave
        P0 = scrambledfun(seed, P)  # Paso 4: Recalcular P0 con la nueva semilla
    return keys


#funciones de encriptacion

def f1(data, key):
    return data ^ key  # funcion XOR

def f2(data, key):
    return ((data ^ key) << 1) & 0xFFFFFFFFFFFFFFFF # Funcion XOR con desplazamiento a la izquierda

def f3(data, key):
    return ((data ^ key) >> 1) & 0xFFFFFFFFFFFFFFFF # Funcion XOR con desplazamiento a la derecha

def f4(data, key):
    return (((data ^ key) << 3) & (2**64 - 1)) | (data >> (64 - 3)) # Funcion XOR con rotación a la derecha

#funcion que genera el psn en base a la tabla de psn
def generate_random_psn(): 
    psnchar = ['a','b','c','d','e']
    #random.choice para seleccion random de caracter
    character = random.choice(psnchar)
    return psn_table.get(character), character

# Proceso de encriptacion usando el PSN para determinar el orden de la funcion
def encrypt_message(message, key_table, psn, keynum):
    functions = [f1, f2, f3, f4]
    #se convierte el mensaje a bits para poder operarlos bit a bit con las operaciones lógicas
    data = int.from_bytes(message.encode(), 'big')
    
    # Aplicar funciones basadas en el PSN
    for i in psn:
        func = functions[i - 1]
        data = func(data, key_table[keynum])
    
    # Asegura que el largo del byte sea al menos un byte, saca la cantidad de bytes con .bitlength

    byte_length = (data.bit_length() + 7) // 8
    #vuelve a convertir los bytes a hexadecimal para seguir la consistencia
    return data.to_bytes(max(byte_length, 1), 'big').hex()

#funcion que manda el mensaje al servidor por medio de un JSON
def send_message_to_server(message_id, message_type, payload, psn=None):
    message = {
        "ID": message_id,
        "Type": message_type,
        "Payload": payload,
        "PSN": psn if psn else []
    }
    with open("message_to_server.json", "w") as file:
        json.dump(message, file)

def delete_message_file():
    try:
        os.remove("message_to_server.json")
        print("JSON eliminado. Gracias por encriptar con nosotros, vuelve pronto.")
    except FileNotFoundError:
        print("Gracias por encriptar con nosotros, vuelve pronto.")

#Interfaz gráfica, con validaciones según el tipo de mensaje que manda el usuario
#En base a las selecciones, se invocan las funciones explicadas anteriormente
message_type = ""
msg_id= 1
while(message_type != "5"):
    print("Seleccione que tipo de mensaje desea mandar")
    print("1.FCM\n2.RM\n3.KU\n4.LCM\n5.Exit")
    message_type= input()
    if(message_type == "2" and key_table!= []):
        print("Digite su mensaje:")
        desired_message= input()
        psn, psnchar = generate_random_psn()
        enc_message = encrypt_message(desired_message,key_table, psn, msg_id - 1)
        send_message_to_server(bin(msg_id),"RM", enc_message, psnchar)
        print(enc_message)
        print(msg_id - 1)
        print("Mensaje enviado. Presiona enter")
        input()
    elif(message_type == "2"):
        print("Debes generar un FCM primero")
    elif(message_type == "1" and key_table == []):
        seed = generate_seed(get_deviceid())
        send_message_to_server(bin(msg_id),"FCM", {"seed": seed})
        key_table = generate_key_table(seed, P, Q, N)
        print(f"Key Table: {key_table}")
        print("Mensaje enviado. Tabla de llaves generada. Presiona enter")
        input()
    elif(message_type == "1"):
        print("FCM ya generado, prueba con un KU")
    elif(message_type == "3" and key_table != []):
        seed = generate_seed(get_deviceid())
        send_message_to_server(bin(msg_id),"KU", {"seed": seed})
        key_table = generate_key_table(seed, P, Q, N)
        print(f"Key Table: {key_table}")
        print("Tabla de llaves actualizada. Presiona enter")
        input()
    elif(message_type == "3"):
        print("No puedes actualizar una tabla que no haz creado. Crea un FCM")
    elif(message_type == "4"):
        key_table=[]
        msg_id+=1
        send_message_to_server(bin(msg_id),"LCM", "")
        print("Conexión finalizada. Genera un nuevo FCM para continuar.")
        input()
    elif(message_type== "5"):
        send_message_to_server(bin(msg_id),"LCM", "")
        delete_message_file()
    else:
        print("Debes elegir una opción válida")