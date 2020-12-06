from daemonize import daemon
import json, os, sys, datetime, time, logging, atexit, threading
import prometheus as prom
from logging.handlers import RotatingFileHandler

class D(daemon):

    def __init__(self, pwd):
        self.pidfile = pwd+"/.pidfile"
        self.conf_Path = pwd+"/midware_prom.conf"
        self.log_path = pwd+"/.midware.log"
        self.config = {}

        logging.getLogger().addHandler(logging.StreamHandler()) # write to stderr
        logging.getLogger().setLevel(logging.INFO) # logging level
        handler = RotatingFileHandler(self.log_path, maxBytes=6000, backupCount=7)
        logging.getLogger().addHandler(handler) # log file

    def config_setup(self):
        try:
            with open(self.conf_Path) as fp:
                self.config = json.load(fp)
            atexit.register(self._config_record) # record the config when exiting
        except:
            logging.exception("config_failed")
            sys.exit(1)
        if not os.path.isdir(self.config["prometheus_probe"]["out_Dir"]):
            logging.error("Output_Directory_DNE")
            sys.exit(1)
        logging.debug("config_complete")
    
    def _config_record(self):
        if self.config:
            with open(self.conf_Path, "w") as fp:
                json.dump(self.config, fp, indent=4)

    def run(self):
        # set up config and login to zabbix
        self.config_setup()
        prometheus_probe = self.config["prometheus_probe"]
        while True:
            for i in range(0, 60, 15):
                prom.wait_till_second(i)
                prom.write_to_csv(prometheus_probe["configs"], prometheus_probe["out_Dir"])


if __name__ == "__main__":
    if len(sys.argv)==2:
        APP = D(os.getcwd())
        if sys.argv[1] == "daemon":
            logging.debug("Send_daemon_message")
            APP.start()
        elif sys.argv[1] == "restart":
            logging.debug("Send_restart_message")
            APP.restart()
        elif sys.argv[1] == "stop":
            logging.debug("Send_stop_message")
            APP.stop()
        elif sys.argv[1] == "start":
            logging.debug("Send_start_message")
            APP.start(if_daemon=False)
        else :
            logging.error("Unkown argument")
    else:
        print("usage:")
        print("\tpython3 main.py start|restart|stop|daemon")
