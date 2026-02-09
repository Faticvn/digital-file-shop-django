
def send_sms(phone: str, message: str):
    if not phone:
        return

    print("====== SMS SENT ======")
    print(f"TO: {phone}")
    print("MESSAGE:")
    print(message)
    print("======================")