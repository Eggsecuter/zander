class_name MoveMessage extends ReceiveMessage

var grab_x: float
var grab_y: float
var place_x: float
var place_y: float
var rotation_degrees: float

func from_json(data: Dictionary):
	grab_x = data.get('grabX', 0.0)
	grab_y = data.get('grabY', 0.0)
	place_x = data.get('placeX', 0.0)
	place_y = data.get('placeY', 0.0)
	rotation_degrees = data.get('rotationDegrees', 0.0)
