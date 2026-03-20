#!/usr/bin/env python3
import time
import subprocess
import signal
import sys
import logging
import RPi.GPIO as GPIO

# RPiCarPowerHAT pins (BCM)
PIN_ACC   = 27   # HIGH when ACC present
PIN_LATCH = 25   # HIGH keeps power latched

# Timings (seconds)
ACC_CONFIRM_LOW = 3.0    # ACC must be low continuously for this long
SHUTDOWN_DELAY  = 2.0    # extra grace time after confirmed low
CHECK_INTERVAL  = 0.05   # polling interval (50ms)

# Logging
LOG_LEVEL = logging.INFO

def setup_logging():
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s %(levelname)s %(message)s",
    )

def shutdown_now():
    # If your systemd service runs as root, no sudo needed.
    subprocess.run(["/sbin/shutdown", "-h", "now"], check=False)

def cleanup(signum=None, frame=None):
    try:
        logging.info("Exiting (signal=%s). Cleaning up GPIO.", signum)
    except Exception:
        pass
    GPIO.cleanup()
    sys.exit(0)

def main():
    setup_logging()

    GPIO.setmode(GPIO.BCM)

    # Prevent floating input causing false triggers
    GPIO.setup(PIN_ACC, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Keep power latched on
    GPIO.setup(PIN_LATCH, GPIO.OUT, initial=GPIO.HIGH)
    logging.info("Latched power: GPIO%d=HIGH (ACC input on GPIO%d).", PIN_LATCH, PIN_ACC)

    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    acc_low_since = None
    shutdown_sent = False
    last_report_bucket = None  # throttles "LOW for Xs" logs

    while True:
        acc = GPIO.input(PIN_ACC)          # 1 = ACC present, 0 = ACC absent
        now = time.monotonic()

        if acc == 0:
            if acc_low_since is None:
                acc_low_since = now
                last_report_bucket = None
                logging.info("ACC LOW detected (timer start).")
            else:
                low_for = now - acc_low_since

                # Log every ~2 seconds while low
                bucket = int(low_for // 2)
                if bucket != last_report_bucket:
                    last_report_bucket = bucket
                    logging.info("ACC LOW for %.1fs", low_for)

                if (low_for >= ACC_CONFIRM_LOW) and (not shutdown_sent):
                    shutdown_sent = True
                    logging.warning(
                        "ACC LOW confirmed (>= %.1fs). Shutdown in %.1fs.",
                        ACC_CONFIRM_LOW, SHUTDOWN_DELAY
                    )
                    time.sleep(SHUTDOWN_DELAY)
                    logging.warning("Issuing shutdown now.")
                    shutdown_now()

        else:
            if acc_low_since is not None:
                logging.info("ACC HIGH restored (timer reset).")
            acc_low_since = None
            shutdown_sent = False
            last_report_bucket = None

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
