import logging
import time
#from periphery import GPIO, SPI
import orangepi.zero2w
from OPi import GPIO
import spidev

logger = logging.getLogger(__name__)

class OrangePiZero2W:
    RST_PIN = 11  # BCM 17 -> wPi 20 (Physical Pin 11)
    DC_PIN = 22  # BCM 25 -> wPi 24 (Physical Pin 36)
    CS_PIN = 24  # BCM 8  -> wPi 10 (Physical Pin 24)
    BUSY_PIN = 18  # BCM 24 -> wPi 19 (Physical Pin 35)
    PWR_PIN = 12  # BCM 18 -> wPi 21 (Physical Pin 32)
    MOSI_PIN = 19  # BCM 10 -> wPi 12 (Physical Pin 19)
    SCLK_PIN = 23  # BCM 11 -> wPi 14 (Physical Pin 23)
    
    def __init__(self):
        # Update GPIO mappings with the confirmed GPIO numbers
        try:
            logger.info("Initializing GPIOs")
            GPIO.setmode(orangepi.zero2w.BOARD)

            GPIO.setup(self.RST_PIN, GPIO.OUT)
            GPIO.setup(self.DC_PIN, GPIO.OUT)
            GPIO.setup(self.CS_PIN, GPIO.OUT)
            GPIO.setup(self.BUSY_PIN, GPIO.IN, GPIO.LOW)
            GPIO.setup(self.PWR_PIN, GPIO.OUT)
            
            logger.info("GPIOs initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize GPIOs: {e}")
            raise

        try:
            logger.info("Initializing SPI")
            self.SPI = spidev.SpiDev()
            self.SPI.open(1, 0)
            self.SPI.max_speed_hz = 12000000
            self.SPI.mode = 0b00
            logger.info("SPI initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SPI: {e}")
            raise

    def digital_write(self, pin, value):
        GPIO.output(pin, value)

    def digital_read(self, pin):
        return GPIO.input(pin)
       
    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.SPI.writebytes([data])

    def spi_writebyte2(self, data):
        self.SPI.writebytes2([data])
        
    def spi_writebytes(self, data):
        self.SPI.writebytes(data)

    def spi_writebytes2(self, data):
        self.SPI.writebytes2(data)

    def module_init(self):
        GPIO.output(self.PWR_PIN, GPIO.LOW)
        time.sleep(0.2)
        GPIO.output(self.PWR_PIN, GPIO.HIGH)
        return 0

    def module_exit(self):
        logger.debug("spi end")
        GPIO.output(self.RST_PIN, GPIO.LOW)
        GPIO.output(self.DC_PIN, GPIO.LOW)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        GPIO.output(self.PWR_PIN, GPIO.LOW)
        
        # Close GPIOs
        GPIO.cleanup(self.RST_PIN)
        GPIO.cleanup(self.DC_PIN)
        GPIO.cleanup(self.CS_PIN)
        GPIO.cleanup(self.PWR_PIN)
        GPIO.cleanup(self.BUSY_PIN)

        self.SPI.close()

