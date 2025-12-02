extends Node3D

@onready var camera: MainCamera = $Camera3D
@onready var raycast = $RayCast3D

@export var debug_sphere: PackedScene

const HOST := '127.0.0.1'
const PORT := 6048
var client = StreamPeerTCP.new()
var connected = false

var buffer := ''

var started := false

func _ready():
	connect_to_server()
	set_process(true)

func connect_to_server():
	var err = client.connect_to_host(HOST, PORT)

	if err == OK:
		print("Connecting...")
	else:
		print("Failed to connect:", err)

func _process(_delta):
	client.poll()

	if Input.is_action_just_pressed("Start"):
		if not started:
			started = true

			var data = await camera.screenshot()
			var message = CameraMessage.new(data)
			send_message(message)
		else:
			get_tree().reload_current_scene()

	if client.get_status() == StreamPeerTCP.STATUS_CONNECTED:
		if not connected:
			print("Connected to server")
			connected = true

		while client.get_available_bytes() > 0:
			var character := client.get_utf8_string(1)
			buffer += character

			if character == '\n':
				var message_line := buffer.strip_edges()
				buffer = ''

				if message_line.is_empty():
					continue

				var parts = message_line.split('=', false, 1)

				if parts.size() == 2:
					handle_message(parts[0], parts[1])

func reset(message: ResetMessage):
	if message.start:
		print('Start')
		send_message(ReadyMessage.new())
	else:
		print('Stop')

func move(message: MoveMessage):
	print("Move grabX:%f grabY:%f placeX:%f placeY:%f rotationDegrees:%f" % [message.grab_x, message.grab_y, message.place_x, message.place_y, message.rotation_degrees])

	raycast.position = to_absolute(message.grab_x, raycast.position.y, message.grab_y)

	if raycast.is_colliding():
		var collider = raycast.get_collider()

		if collider is Area3D:
			var puzzle_piece = collider.get_parent()
			var tween = create_tween()

			tween.tween_property(
				puzzle_piece, "position",
				to_absolute(message.place_x, puzzle_piece.position.y, message.place_y),
				0.5
			)

			tween.tween_property(
				puzzle_piece, "rotation_degrees",
				Vector3(puzzle_piece.rotation_degrees.x, puzzle_piece.rotation_degrees.y + message.rotation_degrees, puzzle_piece.rotation_degrees.z),
				0.5
			)

			await tween.finished

	send_message(ReadyMessage.new())

func to_absolute(percentile_x: float, y: float, percentile_y: float):
	# origin
	var point = Vector3(-0.185, y, 0.15)
	
	point.x += 0.37 * percentile_x / 100
	point.z -= 0.37 * percentile_y / 100
	
	var instance = debug_sphere.instantiate()
	instance.global_position = point
	add_child(instance)
	
	print(point)
	
	return point

func send_message(message: SendMessage):
	if connected:
		client.put_utf8_string(message.get_type() + "=" + message.to_json() + "\n")

func handle_message(type: String, body: String):
	var message = JSON.parse_string(body)

	if message != null:
		match type:
			'reset':
				var resetMessage = ResetMessage.new()
				resetMessage.from_json(message)
				reset(resetMessage)
			'move':
				var moveMessage = MoveMessage.new()
				moveMessage.from_json(message)
				move(moveMessage)
