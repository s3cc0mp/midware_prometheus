import urllib.request
import urllib.parse
import csv
import json
import os.path
import time
from datetime import datetime, timedelta
import pprint

def write_to_csv(configs, url, out_dir):
    now = time.time()
    title_time = datetime.strftime(datetime.fromtimestamp(now), '%Y%m%d_%H_%M')
    date_time = datetime.strftime(datetime.fromtimestamp(now), '%Y%m%d_%H:%M:%S')
    
    pp = pprint.PrettyPrinter(indent = 4)

    for config in configs:
        # retrieve configuration
        ip = config['ip']
        exporter = config['exporter']
        probe = config['probe']
        metrics = config['metrics']
        write_metrics = config['write_metrics']
        csv_file = os.path.join(out_dir, probe + '@' + title_time + '.csv')
        
        # Query prometheus server metrics that appear in the configuration file
        for metric_name, metric_query in metrics.items():
            prom_url = url + '/api/v1/query?query=' + urllib.parse.quote(metric_query)
            with urllib.request.urlopen(prom_url) as res:
                metrics_json = json.loads(res.read().decode())
            # The quering result is in JSON format
            result = metrics_json['data']['result']
            # check if the query is successful
            if metrics_json['status'] == 'success':
                for res in result:
                    submetric_field = []
                    # Write every metric label (submetric) that you want to write into the csv file
                    for submetric in write_metrics:
                        if not submetric in res['metric']:
                            break
                        else:
                            submetric_field.append(res['metric'][submetric])
                    else:
                        # write value to csv file
                        value = res['value']
                        with open(csv_file, 'a', newline = '') as csvfile:
                            csv_writer = csv.writer(csvfile)
                            csv_writer.writerow([value[1], metric_name, *submetric_field, ip, date_time])

def wait_till_second(second):
    second_str = '{:02d}'.format(second)
    while True:
        curr_date = datetime.strftime(datetime.fromtimestamp(time.time()), '%S')
        if curr_date == second_str:
            return
        
if __name__ == '__main__':
    with open('config.json') as f:
        configs = json.load(f)
    while True:
        wait_till_second(0)
        write_to_csv(configs['configs'], configs['url'], configs['out_Dir'])
