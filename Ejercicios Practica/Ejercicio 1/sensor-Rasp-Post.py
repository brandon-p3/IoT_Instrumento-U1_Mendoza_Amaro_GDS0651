import network
import time
from machine import Pin, time_pulse_us
from umqtt.simple import MQTTClient

# Configuración Wi-Fi
wifi_ssid = "INFINITUM46AC"  # Cambia por tu SSID
wifi_password = "Md9f2WxYnU"  # Cambia por tu contraseña

# Configura tu broker MQTT
mqtt_broker = "192.168.1.175"  # IP de tu Raspberry Pi
mqtt_port = 1883 
mqtt_topic = "gds0651/sensor"  # Tema donde se publicarán los datos
 # Tema donde se publicarán los datos
mqtt_client_id = "sensor_{}".format(int(time.time()))  # ID único

# Pines del sensor ultrasónico HC-SR04
TRIGGER_PIN = 5
ECHO_PIN = 18

trigger = Pin(TRIGGER_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# Conexión Wi-Fi con manejo de errores
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Conectando a la red Wi-Fi...')
        wlan.connect(wifi_ssid, wifi_password)
        
        timeout = 10  # Esperar hasta 10 segundos para la conexión
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        print('Conexión Wi-Fi exitosa:', wlan.ifconfig())
    else:
        print("Error: No se pudo conectar a Wi-Fi")
        return False
    return True

# Conexión MQTT con manejo de errores
def connect_mqtt():
    try:
        client = MQTTClient(mqtt_client_id, mqtt_broker, mqtt_port)
        client.connect()
        print("Conectado al broker MQTT")
        return client
    except Exception as e:
        print("Error al conectar al broker MQTT:", e)
        return None

# Función para medir la distancia con el sensor HC-SR04
def measure_distance():
    trigger.off()
    time.sleep_us(2)
    trigger.on()
    time.sleep_us(10)
    trigger.off()

    pulse_time = time_pulse_us(echo, 1, 30000)  # Tiempo en microsegundos
    if pulse_time < 0:
        return None  # Fallo en la medición

    distance = (pulse_time / 2) * 0.0343  # Conversión a cm
    return round(distance, 2)

# Enviar datos del sensor por MQTT solo si cambian
def publish_data(client, last_distance):
    if client is None:
        print("MQTT no está conectado")
        return last_distance

    try:
        distance = measure_distance()
        if distance is not None and distance != last_distance:
            payload = "{}".format(distance)
            client.publish(mqtt_topic, payload)
            print("Distancia enviada:", payload, "cm")
            return distance  # Actualizar el último valor enviado
        else:
            print("Distancia sin cambios, no se envía")
            return last_distance
    except Exception as e:
        print("Error al medir la distancia:", e)
        return last_distance

# Main
if connect_wifi():  # Conectar a Wi-Fi
    client = connect_mqtt()  # Conectar a MQTT
    last_distance = None  # Última distancia medida

    while True:
        last_distance = publish_data(client, last_distance)  # Enviar datos solo si cambia
        time.sleep(2)  # Medir cada 2 segundos
else:
    print("No se pudo establecer conexión Wi-Fi. Reinicia el dispositivo.")

