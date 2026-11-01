import time

MAX_ATTEMPTS = 3
LOCKOUT_DURATION = 60  # seconds

class BruteForceProtector:
    def __init__(self, lockout_enabled=True):
        self.attempts = 0
        self.locked_until = None
        self.lockout_enabled = lockout_enabled

    def is_locked(self):
        if not self.lockout_enabled:
            return False
        return self.locked_until and time.time() < self.locked_until

    def register_attempt(self, success):
        if success:
            self.attempts = 0
            self.locked_until = None
        else:
            self.attempts += 1
            if self.lockout_enabled and self.attempts >= MAX_ATTEMPTS:
                self.locked_until = time.time() + LOCKOUT_DURATION

    def remaining_lock_time(self):
        if self.is_locked():
            return int(self.locked_until - time.time())
        return 0