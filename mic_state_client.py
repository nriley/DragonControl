import rpyc

def mic_state_changed(state):
	print 'mic state changed to', state

if __name__ == '__main__':
	c = rpyc.connect('shirley7', 9999)
	print 'initial mic state', c.root.get_mic_state()

	c.root.set_mic_state_callback(mic_state_changed)
	c.serve_all()
