from MQTT_Objects.Classes.mqttClass import mqttClass
import cv2
from Dependencies import loadConfig
import time
import asyncio
import threading
from .Dependencies.dio_controller import VecowIO
import logger

IP = loadConfig.return_config_value("ip")
PORT = loadConfig.return_config_value("port")
TRIGGER_TOPIC = loadConfig.return_config_value("trigger_topic")
IMAGE_TOPIC = loadConfig.return_config_value("image_topic")
MESSAGE = loadConfig.return_config_value("message")
DIO_COUNT = loadConfig.return_config_value("dio_count")

def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def setup_dio_control():
    try:
        dio = VecowIO()
        logger.info("Digital I/O controller initialized successfully")
        return dio
    except Exception as e:
        logger.error(f"Failed to initialize Digital I/O controller: {e}")
        return None

async def listen_for_data(data: mqttClass) -> bool:
    try:
        msg = await data.ListenForMessage()

    except Exception as e:
        print(f"Error occurred while listening for message: {e}")
        return False
    msg_decoded = msg.decode('utf-8') if isinstance(msg, bytes) else str(msg)

    if msg_decoded == MESSAGE:
        print("data received for plc." + str(msg_decoded))
        return msg_decoded

    return False

def decode_dio_values(values: str):
    '''This function will decode the digital IO values received from the PLC and return a list of integers representing the state of each IO.'''
    data = values.split(",")
    for i in range(len(data)):
        data[i] = int(data[i])
    return data

def set_digital_io(dio_values: list, dio_controller: VecowIO):
    # This function will set the digital IO on the PLC to trigger the capture of the image.
    # it returns nothing.
    if len(dio_values) != DIO_COUNT:
        raise ValueError(f"Error: Expected {DIO_COUNT} digital IO values, but received {len(dio_values)}.")     
        
    for i in range(DIO_COUNT):
        dio_state = dio_values[i]
        dio_controller.set_do_pin(1, i, dio_state)
    pass

def main():
    data = mqttClass()
    data.ConnectToServer(IP, PORT)
    data.SubscribeToTopic(TRIGGER_TOPIC)

    loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_async_loop, args=(loop,), daemon=True)
    t.start()

    time.sleep(0.1)

    dio_controller = setup_dio_control()

    while True:
        time.sleep(0)
        msg = asyncio.run_coroutine_threadsafe(listen_for_data(data), loop).result()
        if msg is not None:
            set_digital_io(decode_dio_values(msg), dio_controller)

if __name__ == "__main__":
    main()