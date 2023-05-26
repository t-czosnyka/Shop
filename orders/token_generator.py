from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36


class OrderConfirmationTokenGenerator(PasswordResetTokenGenerator):

    def make_token(self, order):
        """
        Return a token that can be used once to confirm order
        """
        return self._make_token_with_timestamp(
            order,
            self._num_seconds(self._now()),
            self.secret,
        )

    def _make_token_with_timestamp(self, order, timestamp, secret):
        # timestamp is number of seconds since 2001-1-1. Converted to base 36,
        # this gives us a 6 digit string until about 2069.
        ts_b36 = int_to_base36(timestamp)
        hash_string = salted_hmac(
            self.key_salt,
            self._make_hash_value(order, timestamp),
            secret=secret,
            algorithm=self.algorithm,
        ).hexdigest()[
            ::2
        ]  # Limit to shorten the URL.
        return "%s-%s" % (ts_b36, hash_string)

    def _make_hash_value(self, order, timestamp):
        # make hash with order confirmed status that will change after token is used.
        return f"{order.id}{order.email}{timestamp}{order.confirmed}"

    def check_token(self, order, token):
        """
        Check that an order confirm token is correct for given order.
        """
        if not (order and token):
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
                self._make_token_with_timestamp(order, ts, secret),
                token,
            ):
                break
        else:
            return False

        # Check the timestamp is within limit.
        if (self._num_seconds(self._now()) - ts) > settings.ORDER_CONFIRMATION_TIMEOUT:
            return False

        return True


order_confirmation_token_generator = OrderConfirmationTokenGenerator()