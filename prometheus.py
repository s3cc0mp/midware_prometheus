import urllib.request
import urllib.parse
import csv
import json
import os.path
import time
from datetime import datetime

def write_to_csv(configs, out_dir):
    now = time.time()
    title_time = datetime.strftime(datetime.fromtimestamp(now), '%Y%m%d_%H_%M')
    date_time = datetime.strftime(datetime.fromtimestamp(now), '%Y%m%d_%H:%M:%S')

    for config in configs:
        ip, port = config['ip'], config['port']
        monitor_metrics = config['monitor_metrics']
        exporter = config['exporter']
        directory = config['directory']
        url = 'http://' + ip + ':' + str(port) + '/metrics'
        with urllib.request.urlopen(url) as res:
            metrics = res.read().decode()
        metrics_str = metrics.split('\n')

        for metric_str in metrics_str:
            monitor_flag = False
            for monitor_metric in monitor_metrics:
                if metric_str.startswith(monitor_metric + ' ') or metric_str.startswith(monitor_metric + '{'):
                    monitor_flag = True
                    break
            if monitor_flag: # last one
                metric_name = ' '.join(metric_str.split(' ')[:-1])
                metric_value = metric_str.split(' ')[-1]
                csv_file = os.path.join(out_dir, directory, exporter + '@' + title_time + '.csv')
                if not os.path.exists(os.path.join(out_dir, directory)):
                    os.mkdir(os.path.join(out_dir, directory))
                if not os.path.exists(csv_file):
                    with open(csv_file, 'w', newline = '') as csvfile:
                        pass
                with open(csv_file, 'a', newline = '') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow([metric_value, metric_name, ip, date_time])

def wait_till_second(second):
    second_str = '{:02d}'.format(second)
    while True:
        curr_date = datetime.strftime(datetime.fromtimestamp(time.time()), '%S')
        if curr_date == second_str:
            return
        

if __name__ == '__main__':
    with open('prom_config.json') as f:
        configs = json.load(f)
    configs = configs['configs']
    while True:
        wait_till_second(0)
        write_to_csv(config)

        
