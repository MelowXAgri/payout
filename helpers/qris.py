def convert_crc16(data):
    crc = 0xFFFF
    for char in data:
        crc ^= ord(char) << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    hex_crc = hex(crc & 0xFFFF)[2:].upper()
    return hex_crc.zfill(4)

def generate_qris(amount):
    amount = str(amount)
    # qris = "00020101021126670016COM.NOBUBANK.WWW01189360050300000879140214451524662597130303UMI51440014ID.CO.QRIS.WWW0215ID20232633000480303UMI5204481253033605802ID5920KLMX STORE OK11646236006SERANG61054211162070703A01630438B3"
    qris = "00020101021126670016COM.NOBUBANK.WWW01189360050300000879140214510401201018130303UMI51440014ID.CO.QRIS.WWW0215ID20232612457400303UMI5204481253033605802ID5920WINDASHOPP OK11304556006SERANG61054211162070703A0163042758"
    qris = qris[:-4]
    step1 = qris.replace("010211", "010212")
    step2 = step1.split("5802ID")
    price = f"54{len(amount):02d}{amount}"
    price += "5802ID"
    fix = step2[0].strip() + price + step2[1].strip()
    fix += convert_crc16(fix)
    return fix

def create_qr_code(data):
    return f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={data}"

def get_qris_payment(amount):
    qris_code = generate_qris(amount)
    qris_url = create_qr_code(qris_code)
    return qris_url, qris_code