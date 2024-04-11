def validator_phone_number(phone_number):
    phone_number = str(phone_number)
    phone_number = phone_number.replace(' ', '').replace('-', '').strip()
    if phone_number.startswith('+'):
        phone_number = phone_number[1:]
    if not phone_number.isdigit() or len(phone_number) != 11:
        return False
    return '+' + phone_number
