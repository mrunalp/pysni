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


#
#  main():
#
if __name__ == '__main__':
   ip   = os.environ['OPENSHIFT_PYSNI_IP']
   port = int(os.environ['OPENSHIFT_PYSNI_PORT'])
   app = imp.load_source('application', 'wsgi/application')

   sni_ip = os.environ['OPENSHIFT_PYSNI_SNI_IP']
   sni_port = int(os.environ['OPENSHIFT_PYSNI_SNI_PORT'])

   fwtype="wsgiref"
   for fw in ("cherrypy"):
      try:
         imp.find_module(fw)
         fwtype = fw
      except ImportError:
         pass

   print('Starting WSGIServer type %s on %s:%d ... ' % (fwtype, ip, port))
   if fwtype == "cherrypy":
      import cherrypy
      s1 = cherrypy.process.servers.ServerAdapter(cherrypy.engine,
                                                  cherrypy.wsgiserver.CherryPyWSGIServer(
            (ip, port), app.application, server_name=os.environ['OPENSHIFT_APP_DNS']) )

      s2 = cherrypy.process.servers.ServerAdapter(cherrypy.engine,
                                                  cherrypy.wsgiserver.CherryPyWSGIServer(
            (sni_ip, sni_port), app.application, server_name=os.environ['OPENSHIFT_APP_DNS']) )

      s1.subscribe
      s2.subscribe

      cherrypy.engine.start()

   else:
      from wsgiref.simple_server import make_server
      make_server(ip, port, app.application).serve_forever()
