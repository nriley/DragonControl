port = 9090
# see also <https://github.com/apache/thrift/blob/master/tutorial/py/PythonServer.py>
# and <https://github.com/apache/thrift/blob/master/tutorial/py/PythonClient.py>

from dragon import Dragon
import natlink

class DragonHandler(Dragon.Iface):
	def __init__(self):
		natlink.natConnect(True)

	def __del__(self):
		natlink.natDisconnect()

	def getMicState(self, ):
		return Dragon.MicState._NAMES_TO_VALUES[natlink.getMicState()]

	def setMicState(self, newState):
		pass

processor = Dragon.Processor(DragonHandler())

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

transport = TSocket.TServerSocket(port=port)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()
# can't use natlink (even with "thread safety" enabled) if server is threaded
server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

server.serve()

