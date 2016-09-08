python init.py


init.py:
import tornado.ioloop

from tornado.options import define, options
define('port', default=9000, help='run on this port', type=int)
define('debug', default=True, help='enable debug mode')
options.parse_command_line()

import app

def runserver():
	app.run()
	loop = tornado.ioloop.IOloop.instance()
	loop.start()

if __name__ == '__main__'
	runserver()