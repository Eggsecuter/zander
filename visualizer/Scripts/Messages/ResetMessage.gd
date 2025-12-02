class_name ResetMessage extends ReceiveMessage

var start: bool

func from_json(data: Dictionary):
	start = data.get('start', false)
