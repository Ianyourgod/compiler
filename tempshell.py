import copiedig as amp

while True:
	text = input('basic > ')
	result, error = amp.run('<stdin>', text)

	if error: print(error.as_string())
	else: print(result)