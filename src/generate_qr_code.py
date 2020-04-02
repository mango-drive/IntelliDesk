import qrcode
import json
import random
import string

class QRCode:
    def __init__(self, object_type, display_text):
        self.data = {
            "object_type": object_type,
            "id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=3)),
            "display_text": display_text
        }

    def to_string(self):
        string = "o: {}, i: {}, t: {}".format(
            self.data["object_type"],
            self.data["id"],
            self.data["display_text"]
        )
        print(string)
        return string

qr_codes = [
    QRCode("test barcode", "ABCDEFGH"),
    QRCode("test barcode", "98735298"),
    QRCode("test barcode", "ALKJB837"),
    QRCode("test barcode", "AOIEBBKJ"),
]

for q in qr_codes:
    qr = qrcode.QRCode(
        version = 1,
        error_correction = qrcode.constants.ERROR_CORRECT_H,
        box_size = 3,
        border = 5
    )
    qr.add_data(q.data["display_text"])
    qr.make(fit=True)
    img = qr.make_image()
    img.save("../img/{}.jpg".format(q.data["display_text"]))




