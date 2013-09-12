import threading, socket
import ConfigParser,sys, logging
from random import choice

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('serverhealthcheck.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
fh.setFormatter(formatter)

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)

log.addHandler(sh)
log.addHandler(fh)

config = ConfigParser.RawConfigParser()
config.read(sys.argv[1])

class ServerChecker(threading.Thread):
    log.info("Starting ServerChecker")
    stop_event = threading.Event()
    is_stopping = False

    def __init__(self, client, channel):
        log.info("INIT ServerChecker")
        self.client = client
        self.channel = channel
        self.down_messages = [
            "HOGGIT DEDICATED IS NOT RESPONDING. SOMEONE REPLACE THE HAMSTERS AND REMEMBER TO FEED THEM THIS TIME.",
            "HOGGIT DEDICATED IS DOWN.  !BLAME JERS / ZELLY",
            "HOGGIT DEDICATED IS DOWN.  ENSURE THE CAPACITORS STILL CONTAIN THEIR SMOKE.",
            "Hoggit dedicated is up.  JK YOU DUMB FUCK IT'S DOWN FIXITFIXITFIXITFIXIT"
        ]
        threading.Thread.__init__(self)
        self.daemon = True
        log.info( "ServerChecker INIT complete")

    def run(self):
        try:
            log.info( "ServerChecker thread start")
            while not self.is_stopping:
                log.info( "ServerChecker main loop")
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(float(config.get('health_check', 'timeout')) )
                try:
                    s.connect((config.get('health_check', 'hostname'), int(config.get('health_check', 'port')) ))
                except socket.timeout:
                    self.client.msg(self.channel, choice(self.down_messages))
                finally:
                    s.close()

                if self.stop_event.wait(60 * 20):
                    self.is_stopping = True
        except Exception, ex:
            log.debug(ex)
            self.is_stopping = True
            raise
            sys.exit(0)
