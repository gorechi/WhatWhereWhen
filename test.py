s = 'Кошка'

def reverse_capitalize(input_string:str) -> str:
    output_string = input_string[-1::-1].lower().capitalize()
    return output_string

print(s)
print(reverse_capitalize(s))
