import sys
import pyotp
import time

def get_otp(secret):
    while True:
        try:
            totp = pyotp.TOTP(secret).now()
            remaining = 30 - int(time.time()) % 30
            print("%s %s - %s [%d] " % (totp[:3], totp[3:], totp, remaining), end = "\r")
            time.sleep(1)
        except: break

if __name__ == "__main__":
    get_otp(sys.stdin.read().strip().replace(" ", "").upper())