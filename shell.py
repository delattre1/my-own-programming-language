import my_own


while True:
    text = input('OWN> ')

    if text == 'quit()' or text == 'exit()':
        exit()

    #print(text)
    res, error = my_own.run('<stdin>', text)

    if error: print(error.as_string())
    else: print(res)
    #import pdb; pdb.set_trace()
