from django.contrib.auth.tokens import PasswordResetTokenGenerator


class ConfirmationCodeGenerator(PasswordResetTokenGenerator):
    """Кастомный генератор `сonfirmation_code`."""

    def _make_hash_value(self, user, timestamp):
        """
        Hash the user's primary key and some user state that's sure to change
        after a password reset to produce a token that invalidated when it's
        used:
        1. The password field will change upon a password reset (even if the
           same password is chosen, due to password salting).
        2. The last_login field will usually be updated very shortly after
           a password reset.
        Failing those things, settings.PASSWORD_RESET_TIMEOUT_DAYS eventually
        invalidates the token.

        Running this data through salted_hmac() prevents password cracking
        attempts using the reset token, provided the secret isn't compromised.
        """
        # Truncate microseconds so that tokens are consistent even if the
        # database doesn't support microseconds.
        if user.last_login is None:
            login_timestamp = ''
        else:
            login_timestamp = user.last_login.replace(
                microsecond=0, tzinfo=None
            )
        if user.password:
            return f'{user.pk}{user.password}{login_timestamp}{timestamp}'
        else:
            return f'{user.pk}password{login_timestamp}{timestamp}'


default_token_generator = ConfirmationCodeGenerator()
