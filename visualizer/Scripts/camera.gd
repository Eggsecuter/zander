class_name MainCamera extends Camera3D

func screenshot() -> PackedByteArray:
	await RenderingServer.frame_post_draw
	
	var image = get_viewport().get_texture().get_image()
	
	var crop_x_pct = 0.16
	var crop_y_pct = 0
	var crop_width_pct = 0.68
	var crop_height_pct = 1
	
	var crop_x = int(image.get_width() * crop_x_pct)
	var crop_y = int(image.get_height() * crop_y_pct)
	var crop_width = int(image.get_width() * crop_width_pct)
	var crop_height = int(image.get_height() * crop_height_pct)
	
	var cropped = Image.create_empty(crop_width, crop_height, false, image.get_format())
	cropped.blit_rect(image, Rect2i(crop_x, crop_y, crop_width, crop_height), Vector2i(0, 0))
	
	return cropped.save_png_to_buffer()
