from opencmiss.utils.zinc.general import AbstractNodeDataObject


class EXPoint(AbstractNodeDataObject):

    def __init__(self, x, y, z):
        super(EXPoint, self).__init__(['coordinates'])
        self._x = x
        self._y = y
        self._z = z

    def get(self):
        return [self._x, self._y, self._z]

    def coordinates(self):
        return [self._x, self._y, self._z]

    def __repr__(self):
        return 'x="{0}" y="{1}" z="{2}"'.format(self._x, self._y, self._z)
