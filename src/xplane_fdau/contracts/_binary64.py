"""ECMAScript number tokens for finite IEEE-754 binary64 values."""

from __future__ import annotations

from fractions import Fraction
import math
import struct

from .errors import CanonicalJSONError


def _decimal_exponent(value: Fraction) -> int:
    """Return floor(log10(value)) by integer comparison."""
    exponent = len(str(value.numerator)) - len(str(value.denominator))
    threshold = Fraction(10**exponent) if exponent >= 0 else Fraction(1, 10**-exponent)
    if value < threshold:
        exponent -= 1
    return exponent


def _scaled_bounds(lower: Fraction, upper: Fraction, scale: Fraction, *, inclusive: bool) -> tuple[int, int]:
    low = lower / scale
    high = upper / scale
    first = low.numerator // low.denominator + (0 if inclusive and low.denominator == 1 else 1)
    last = high.numerator // high.denominator - (1 if not inclusive and high.denominator == 1 else 0)
    return first, last


def _shortest_decimal(value: float) -> tuple[str, int]:
    exact = Fraction(*value.as_integer_ratio())
    prior = Fraction(*math.nextafter(value, -math.inf).as_integer_ratio())
    following_float = math.nextafter(value, math.inf)
    following = Fraction(*following_float.as_integer_ratio()) if math.isfinite(following_float) else exact + (exact - prior)
    lower = (exact + prior) / 2
    upper = (exact + following) / 2
    significand_bits = struct.unpack(">Q", struct.pack(">d", value))[0] & ((1 << 52) - 1)
    inclusive = significand_bits % 2 == 0
    exponent = _decimal_exponent(exact)

    for precision in range(1, 18):
        choices: list[tuple[Fraction, int, Fraction, int, int]] = []
        for power in range(exponent - precision, exponent - precision + 3):
            scale = Fraction(10**power) if power >= 0 else Fraction(1, 10**-power)
            first, last = _scaled_bounds(lower, upper, scale, inclusive=inclusive)
            first = max(first, 10 ** (precision - 1))
            last = min(last, 10**precision - 1)
            if first > last:
                continue
            target = exact / scale
            floor = target.numerator // target.denominator
            for digit in (max(first, min(last, floor)), max(first, min(last, floor + 1))):
                decimal = digit * scale
                choices.append((abs(decimal - exact), digit % 2, -decimal, digit, power))
        if choices:
            _, _, _, digits, power = min(choices)
            return str(digits), power
    raise CanonicalJSONError("cannot serialize binary64")


def _format_decimal(digits: str, power: int) -> str:
    position = len(digits) + power
    if 0 < position <= 21:
        if len(digits) <= position:
            return digits + "0" * (position - len(digits))
        return digits[:position] + "." + digits[position:]
    if -6 < position <= 0:
        return "0." + "0" * -position + digits
    exponent = position - 1
    mantissa = digits[0] + ("." + digits[1:] if len(digits) > 1 else "")
    return mantissa + "e" + ("+" if exponent >= 0 else "") + str(exponent)


def _ecmascript_number_token(value: float) -> str:
    """Return the ECMAScript JSON token for a finite binary64 value."""
    if not math.isfinite(value):
        raise CanonicalJSONError("nonfinite binary64")
    if value == 0.0:
        return "0"
    digits, power = _shortest_decimal(abs(value))
    token = _format_decimal(digits, power)
    return "-" + token if value < 0 else token
