import json

#Tabla de llaves para guardar las llaves generadas
key_table=[]
#funcion para leer el archivo en formato json
def receive_message_from_client():
    try:
        with open("message_to_server.json", "r") as file:
            message = json.load(file)
        return message
    except:
        print("Aun no haz creado el FCM. Crealo y vuelve a correr el servidor.")
        return 0

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

#funciones de decriptacion

def f1(data, key):
    return data ^ key  # funcion XOR

def f2(data, key):
    return ((data >> 1) ^ key) & 0xFFFFFFFFFFFFFFFF # Funcion XOR con desplazamiento a la derecha

def f3(data, key):
    return ((data << 1) ^ key) & 0xFFFFFFFFFFFFFFFF # Funcion XOR con desplazamiento a la izquierda

def f4(data, key):
    return ((data >> 3) | ((data << (64 - 3)) & (2**64 - 1))) ^ key # Funcion XOR con rotación a la izquierda

#funcion que retorna el psn en base al caracter recibido
def get_psn(character): 
    return psn_table.get(character)

# Proceso de desencriptacion basado en el orden reverso del psn
def decrypt_message(encrypted_message, key_table, psn, keynum):
    functions = [f1, f2, f3, f4]
    #se convierte el hexadecimal a bits para poder operarlos bit a bit con las operaciones lógicas
    data = int.from_bytes(encrypted_message, 'big')
    
    reversed_psn = psn[::-1]
    # Order de funciones inverso
    for i in reversed_psn:
        func = functions[i-1]
        data = func(data, key_table[keynum])
     # Asegura que el largo del byte sea al menos un byte, saca la cantidad de bytes con .bitlength
    byte_length = (data.bit_length() + 7) // 8
    if byte_length == 0:
        byte_length = 1

    #la funcion decode devuelve el string representado por los bits
    return data.to_bytes(byte_length, 'big').decode(errors='ignore')

#En base a el tipo de mensaje recibido, la interfaz grafica se encarga de mostrar el output de lo solicitado
#Cada enter se vuelve a recibir el mensaje del json mas reciente
message = receive_message_from_client()
if message != 0:
    print(f"mensaje actual: {message}")
    while(message["Type"] != "LCM"):
        print("Enter para recibir mensaje más reciente")
        input()
        message= receive_message_from_client()
        if (message["Type"] == "FCM" and key_table == []):
            seed = message["Payload"]["seed"]
            key_table = generate_key_table(seed, P, Q, N)
            print(key_table)
        elif(message["Type"] == "FCM"):
            print("El FCM ya ha sido generado, prueba con un KU")
        elif message["Type"] == "RM" and key_table != []:
            encrypted_message = bytes.fromhex(message["Payload"])
            psn = get_psn(message["PSN"])
            keynum = int(message["ID"],0) -1
            print(keynum)
            decrypted_message = decrypt_message(encrypted_message, key_table, psn, keynum)
            print(f"Decrypted Message: {decrypted_message}")
        elif(message["Type"] == "RM"):
            print("Debes generar un FCM primero")
        elif (message["Type"] == "KU" and key_table != []):
            key_table = []
            seed = message["Payload"]["seed"]
            key_table = generate_key_table(seed, P, Q, N)
            print(key_table)
        elif (message["Type"] == "KU"):
            print("Aún no se ha establecido un FCM")
        elif(message["Type"] == "LCM"):
            key_table=[]