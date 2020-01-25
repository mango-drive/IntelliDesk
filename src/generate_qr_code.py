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
    QRCode("mode", "Cook"),
    QRCode("mode", "Clean"),
    QRCode("con", "Plate"),
    QRCode("con", "Bowl"),
    QRCode("con", "Glass"),
    QRCode("ing", "Bread"),
    QRCode("ing", "Tomatoes"),
    QRCode("ing", "Chicken"),
    QRCode("ing", "Salad"),
]

for q in qr_codes:
    qr = qrcode.QRCode(
        version = 1,
        error_correction = qrcode.constants.ERROR_CORRECT_H,
        box_size = 3,
        border = 2
    )
    qr.add_data(q.to_string())
    qr.make(fit=True)
    img = qr.make_image()
    img.save("../img/{}.jpg".format(q.data["display_text"]))




