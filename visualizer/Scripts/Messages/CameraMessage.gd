class_name CameraMessage extends SendMessage

var data: PackedByteArray

func _init(_data: PackedByteArray):
		data = _data

func get_type() -> String:
	return 'camera'

func to_json() -> String:
	return JSON.stringify({"data": data})
