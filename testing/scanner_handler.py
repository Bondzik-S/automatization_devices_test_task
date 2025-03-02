
class CheckQr:
    def __init__(self):
        self.color = None
        self.check_out = lambda exp, callback: callback if exp else lambda: None

    def check_in_db(self, qr):
        raise ConnectionError

    def check_len_color(self, qr):
        color = {
            3: 'Red',
            5: 'Green',
            7: 'Fuzzy Wuzzy'
        }
        self.color = color.get(len(qr))
        return self.color

    def scan_check_out_list(self, qr):
        return [
            self.check_out(not self.check_len_color(qr), lambda: [
                self.send_error(f"Error: Wrong qr length {len(qr)}")
            ]
                     ),
            self.check_out(not self.check_in_db(qr), lambda: [
                self.send_error("Not in DB")
            ]
                     )
        ]

    def check_scanned_device(self, qr: str):
        for func in self.scan_check_out_list(qr):
            if func():
                return
        message = f"hallelujah {qr}"
        self.can_add_device(message)

    @staticmethod
    def can_add_device(message: str):
        return message

    @staticmethod
    def send_error(error: str):
        return error
