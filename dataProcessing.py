import time
import serial
import threading
from sqlalchemy import create_engine, text
import os
import pandas as pd

# Configuración de la base de datos
db_config = {
    "host": "localhost",
    "user": "miguel",
    "password": "200202",
    "database": "sensores"
}

# Configuración de los sensores
bt_port = "/dev/rfcomm0"  # Sensor DHT22
baud_rate = 115200

bt_port1 = "/dev/rfcomm1"  # Sensor KY-001
baud_rate1 = 115200

# Función para insertar datos en la base de datos
def insertar_datos(sensor, temperatura=None, humedad=None):
    try:
        conn = f"mariadb+mariadbconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        engine = create_engine(conn)
        with engine.connect() as connection:
            if sensor == "DHT22":
                query = text("""
                    INSERT INTO sensores_data (sensor, temperatura, humedad, timestamp)
                    VALUES (:sensor, :temperatura, :humedad, :timestamp)
                    """)
                connection.execute(query, {
                    "sensor": sensor,
                    "temperatura": temperatura,
                    "humedad": humedad,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                })
            else:
                query = text("""
                    INSERT INTO sensores_data2 (sensor, temperatura, timestamp)
                    VALUES (:sensor, :temperatura, :timestamp)
                    """)
                connection.execute(query, {
                    "sensor": sensor,
                    "temperatura": temperatura,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                })
        print(f"Datos insertados en la base de datos: {sensor}, {temperatura}, {humedad}")
        connection.close()
    except Exception as e:
        print(f"Error general: {e}")

# Creación de archivos JSON y envío de datos al servidor remoto
def datos_json():
    try:
        conn = f"mariadb+mariadbconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        engine = create_engine(conn)
        query = "SELECT * FROM sensores_data"
        df = pd.read_sql(query,conn)
        df.to_json('/home/miguel/Desktop/Programas/sensores_data.json', orient='records', indent=4)

        engine = create_engine(conn)
        query = "SELECT * FROM sensores_data2"
        df = pd.read_sql(query,conn)
        df.to_json('/home/miguel/Desktop/Programas/sensores_data2.json', orient='records', indent=4)
    except Exception as e:
        print(f"Error general: {e}")

    servidor = "xxxxxxx" 
    ruta_html = "xxxxxx"  
    ruta_css = "xxxxxxx"
    contrasena = "xxxxxxx"

    comando = f"sshpass -p '{contrasena}' scp sensores_data.json {servidor}:{ruta_html}"
    resultado = os.system(comando)

    comando = f"sshpass -p '{contrasena}' scp sensores_data2.json {servidor}:{ruta_css}"
    resultado = os.system(comando)

    if resultado == 0:
        print("Conexión con servidor Web correcta")
    else:
        print("Error al enviar el archivo HTML al servidor.")

# Hilo 1 - Sensor DHT22
def esp32dth11():
    try:
        with serial.Serial(bt_port, baud_rate, timeout=1) as bt_serial:
            print("Conectado a la ESP32 - Sensor DHT22")
            while True:
                if bt_serial.in_waiting > 0:
                    data = bt_serial.readline().decode("utf-8").strip()
                    print(data)
                    try:
                        temperatura, humedad = data.split(",")
                        if temperatura and humedad:
                            insertar_datos("DHT22", temperatura, humedad)
                        else:
                            print(f"Datos no válidos: {data}")
                    except ValueError:
                        print(f"Error al procesar los datos: {data}")
                    datos_json()
                    time.sleep(180)
    except serial.SerialException as e:
        print(f"Error con el puerto serie: {e}")
    except Exception as e:
        print(f"Error general: {e}")

# Hilo 2 - Sensor KY-001
def esp32ky001():
    try:
        with serial.Serial(bt_port1, baud_rate1, timeout=1) as bt_serial:
            print("Conectado a la ESP32 - Sensor KY-001")
            while True:
                if bt_serial.in_waiting > 0:
                    data = bt_serial.readline().decode("utf-8").strip()
                    print(data)
                    if data:
                        insertar_datos("KY-001", temperatura=data)
                    datos_json()
                    time.sleep(180)
    except serial.SerialException as e:
        print(f"Error con el puerto serie: {e}")
    except Exception as e:
        print(f"Error general: {e}")

hilo1 = threading.Thread(target=esp32dth11)
hilo2 = threading.Thread(target=esp32ky001)

hilo1.start()
print("Ejecutando Hilo1 - Sensor DHT22")
hilo2.start()
print("Ejecutando Hilo2 - Sensor KY-001")