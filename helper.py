"""
    Helper classes, can be moved later
"""
import attr

@attr.s
class Vector3:
    # pylint: disable=invalid-name
    X: float = attr.ib()
    Y: float = attr.ib()
    Z: float = attr.ib()

    def __eq__(self, other):
        epsilon = 1e4
        if (
            abs(self.X - other.X) > epsilon
            or abs(self.Y - other.Y) > epsilon
            or abs(self.Z - other.Z) > epsilon
        ):
            return False
        return True

