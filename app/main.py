from typing import Optional

from MQTT_Objects.Classes.mqttClass import mqttClass
from Dependencies import loadConfig
import time
import asyncio
import threading
from Dependencies.dio_controller import VecowIO
import logging

IP = loadConfig.return_config_value("ip")
PORT = loadConfig.return_config_value("port")
PUBLISH_TOPIC = loadConfig.return_config_value("complete_topic")
POSITION_TOPIC = loadConfig.return_config_value("position_topic")
DIO_COUNT = loadConfig.return_config_value("dio_count")
DIO_RESET_DELAY = loadConfig.return_config_value("dio_reset_delay")
DIO_BLOCK_SIZE = loadConfig.return_config_value("dio_block_size")

DIO_BANKS = DIO_COUNT // DIO_BLOCK_SIZE

if DIO_COUNT % DIO_BLOCK_SIZE != 0:
    raise ValueError(f"Error: dio_count must be a multiple of dio_block_size. Received dio_count={DIO_COUNT} and dio_block_size={DIO_BLOCK_SIZE}.")

logging.basicConfig(
    filename=f'./logs/dio_{time.strftime("%Y%m%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - [PID %(process)d] - %(levelname)s - %(message)s',
    force=True,  # Force configuration even if the logger was previously configured
    filemode='a'  # Append mode instead of overwrite
)

def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def setup_dio_control():
    try:
        dio = VecowIO()
        logging.info("Digital I/O controller initialized successfully")
        return dio
    except Exception as e:
        raise Exception(f"Failed to initialize Digital I/O controller: {e}")

async def listen_for_data(data: mqttClass) -> Optional[str]:
    try:
        msg = await data.ListenForMessage()

    except Exception as e:
        raise Exception(f"Error occurred while listening for message: {e}")
    if msg is None:
        logging.warning("Received None message from MQTT. Skipping processing.")
        return None
    
    msg_decoded = msg.decode('utf-8') if isinstance(msg, bytes) else str(msg)

    if msg_decoded is not None:
        logging.info("data received for plc." + str(msg_decoded))
        return msg_decoded

    return None

async def reset_io_after_delay(dio_controller: VecowIO, delay: int):
    # This function will reset all digital IO to 0.
    # this will be better as a loop to make it more expanisve
    await asyncio.sleep(delay)
    for i in range(DIO_COUNT):
        if i < DIO_COUNT/DIO_BANKS:
            dio_controller.set_do_pin(1, i, 0)
        else:
            dio_controller.set_do_pin(2, i - int(DIO_COUNT/DIO_BANKS), 0)
    logging.info(f"Digital IO reset to 0 after delay of. {delay} seconds.")
    return

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
        # create a function to make this more expansive in future
        dio_state = dio_values[i]
        if i < DIO_COUNT/2:
            dio_controller.set_do_pin(1, i, dio_state)
        else:
            dio_controller.set_do_pin(2, i - int(DIO_COUNT/DIO_BANKS), dio_state)
    pass

def main():
    data = mqttClass()
    data.ConnectToServer(IP, PORT)
    data.SubscribeToTopic(POSITION_TOPIC)

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
            completed = f"dio updated at{time.time()}"
            data_bytes = completed.encode('utf-8') if isinstance(completed, str) else completed
            data.PublishMessage(PUBLISH_TOPIC, data_bytes)
            asyncio.run_coroutine_threadsafe(reset_io_after_delay(dio_controller, DIO_RESET_DELAY), loop)

if __name__ == "__main__":
    main()