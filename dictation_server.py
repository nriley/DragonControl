import natlink
import rpyc
import sys

class DragonService(rpyc.Service):
	__slots__ = ('mic_state_callback',)

	def on_connect(self):
		natlink.natConnect(True)
		self.mic_state_callback = lambda state: None
		natlink.setChangeCallback(self.change_callback)

	def on_disconnect(self):
		natlink.natDisconnect()

	def exposed_get_mic_state(self):
		return natlink.getMicState()

	def exposed_set_mic_state(self, state):
		natlink.setMicState(state)

	def exposed_set_mic_state_callback(self, callback):
		self.mic_state_callback = callback

	def change_callback(self, what, how):
		print >> sys.stderr, what, how
		if what == 'mic':
			self.mic_state_callback(how)

if __name__ == '__main__':
	from rpyc.utils.server import OneShotServer
	while True:
		OneShotServer(DragonService, port=9999).start()
