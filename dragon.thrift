// thrift -out . --gen py:new_style shared.thrift

enum MicState {
	off = 0,
	on = 1,
	sleeping = 2
}

service Dragon {
	MicState getMicState(),
	void setMicState(1:MicState newState)
}
