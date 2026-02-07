import pyqrcode


def get_qr_code_kerp(qr_text, error="L", scale=5):
    return pyqrcode.create(qr_text, error).png_as_base64_str(scale=scale, quiet_zone=1)
