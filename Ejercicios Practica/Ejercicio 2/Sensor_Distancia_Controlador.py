from time import sleep
from hcsr04 import HCSR04
from max7219 import Matrix8x8
from machine import Pin, PWM, SPI
from time import sleep, time

spi = SPI(1, baudrate=10000000, polarity=0, phase=0, sck=Pin(25), mosi=Pin(27))
cs = Pin(26, Pin.OUT)
matrix = Matrix8x8(spi, cs, 4)

sensor = HCSR04(trigger_pin=5, echo_pin=18, echo_timeout_us=24000)

led2 = Pin(22, Pin.OUT)

pwm_servo = PWM(Pin(13), freq=50)

def mover_servo(angulo):
    duty = int(40 + (angulo / 180) * 77)
    pwm_servo.duty(duty)

def desplazar_texto(texto):
    """ Desplaza el texto en la matriz LED """
    largo_texto = len(texto) * 8 
    for desplazamiento in range(largo_texto + 32):  
        matrix.fill(0)
        matrix.text(texto, 32 - desplazamiento, 0, 1)  
        matrix.show()
        sleep(0.1) 

while True:
    distancia = sensor.distance_cm()
    print(f"Distancia: {distancia} cm")
    
    if distancia < 10:  
        desplazar_texto("Abriendo")  
        led2.on()
        mover_servo(180) 
        sleep(15) 

        desplazar_texto("Cerrando") 
        mover_servo(0)  
        led2.off()
    
    sleep(0.5)   