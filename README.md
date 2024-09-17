# polimorphic-cipher
Algoritmo de cifrado polimorfico

## Guía de uso

#### Disclaimer:
Este cifrado solo funciona con strings de 7 caracteres, si tiene más de eso, el string será truncado a 7 caracteres en la salida.

### Paso 1: Correr cada archivo en una terminal dedicada

![image](https://github.com/user-attachments/assets/7090675c-96be-4438-bca6-6d50cf35684c)

### Paso 2: Seleccionar FCM como primer mensaje, preferiblemente antes de ejecutar el servidor

![image](https://github.com/user-attachments/assets/7bf0c969-0357-4058-9e89-99fa42031762)

### Paso 3: El servidor requiere de un enter para recibir el nuevo mensaje
![image](https://github.com/user-attachments/assets/d6a46223-4af9-4f32-8c79-069882a521db)

## Nomenclatura de encriptación 

**FCM:** First Contact Message, mensaje que se envía para generar la tabla de llaves del cliente en el servidor, a través de una semilla.
**RM:** Regular Messages, mensaje que se envia cuando se desea escribir el texto a encriptar.
**KUM:** Key Update message, Mensaje que se envía para actualizar la tabla de llaves en el cliente y servidor
**LCM:** Last Contact Message, Mensaje que elimina la tabla de llaves existente, y suspende conexión con el servidor.


