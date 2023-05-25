from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        out_hash = super()._make_hash_value(user, timestamp)
        print(out_hash)
        out_hash += str(user.user_data.is_active)
        print(out_hash)
        return out_hash

    def check_token(self, user, token):
        """
        Check that a password reset token is correct for a given user.
        """
        if not (user and token):
            return False
        # Parse the token
        try:
            ts_b36, _ = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        for secret in [self.secret, *self.secret_fallbacks]:
            if constant_time_compare(
                    self._make_token_with_timestamp(user, ts, secret),
                    token,
            ):
                break
        else:
            return False

        # Check the timestamp is within limit.
        if (self._num_seconds(self._now()) - ts) > settings.ACCOUNT_ACTIVATION_TIMEOUT:
            print("too_old")
            return False

        return True


account_activation_token_generator = AccountActivationTokenGenerator()