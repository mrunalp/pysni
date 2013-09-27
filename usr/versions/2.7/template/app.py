#!/usr/bin/env python

#
# This file may be used instead of Apache mod_wsgi to run your python
# web application in a different framework.  A few examples are
# provided (cherrypi, gevent), but this file may be altered to run
# whatever framework is desired - or a completely customized service.
#
import imp
import os

try:
   zvirtenv = os.path.join(os.environ['OPENSHIFT_PYSNI_DIR'],
                           'virtenv', 'bin', 'activate_this.py')
   execfile(zvirtenv, dict(__file__ = zvirtenv) )
except IOError:
   pass

#
# IMPORTANT: Put any additional includes below this line.  If placed above this
# line, it's possible required libraries won't be in your searchable path
#
from gevent.pywsgi import WSGIServer


#
#  main():
#
if __name__ == '__main__':
   ip   = os.environ['OPENSHIFT_PYSNI_IP']
   port = int(os.environ['OPENSHIFT_PYSNI_PORT'])
   app = imp.load_source('application', 'wsgi/application')

   sni_ip = os.environ['OPENSHIFT_PYSNI_SNI_IP']
   sni_port = int(os.environ['OPENSHIFT_PYSNI_SNI_PORT'])

   sni_cert = os.environ['OPENSHIFT_PYSNI_SNI_CERT']
   sni_key = os.environ['OPENSHIFT_PYSNI_SNI_KEY']

   servers = []

   print('Preparing WSGIServer on %s:%d' % (ip, port))
   servers.append(WSGIServer((ip, port), app.application))

   print('Preparing SSL WSGIServer on %s:%d with %s %s' % (sni_ip, sni_port, sni_cert, sni_key))
   servers.append(WSGIServer((sni_ip, sni_port), app.application, keyfile=sni_key, certfile=sni_cert))

   print('Starting WSGIServers')
   for server in servers:
      server.start()

   print('Waiting for WSGIServers')
   try:
      servers[0]._stopped_event.wait()
   except:
      for server in servers:
         server.stop()
      raise

