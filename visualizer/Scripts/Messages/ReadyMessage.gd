class_name ReadyMessage extends SendMessage

func get_type() -> String:
	return 'ready'

func to_json() -> String:
	return JSON.stringify({})
