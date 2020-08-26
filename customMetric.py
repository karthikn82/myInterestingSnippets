 import redis
 from time import sleep
 from boto.utils import get_instance_metadata
 from boto.ec2 import cloudwatch

 db0 = redis.Redis(port=6379,db=0)

 def myFunc():
     f = 240
     while(f): #runs for 240 seconds
         info = db0.info()

         sleep(1)
         print(info['total_connections_received'])
         f = f-1
         metadata = get_instance_metadata()
         instance_id = metadata['instance-id']
         region = metadata['placement']['availability-zone'][0:-1]
         count_metrics = {
                  'total_connections_received' : info['total_connections_received']
                  }
         send_multi_metrics(instance_id, region, count_metrics)

 def send_multi_metrics(instance_id, region, metrics, unit='Count', namespace='EC2/Redis'):
     cw = cloudwatch.connect_to_region(region)
     cw.put_metric_data(namespace, metrics.keys(), metrics.values());
 if __name__ == '__main__':
     myFunc()
