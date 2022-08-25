
import logging

logger = logging.getLogger()


class Distances:
    def __init__(self, *args, **kwargs):
        self.matrix = kwargs.get('distances', None)

    def get_travel_time(self, frm, to, team_speed):
        # same from and to distance 0
        if frm[0] == to[0]:
            return 0.0

        # get from
        dist = self.matrix.get(frm[0])
        if dist is None:
            return -1
        # get to
        dist = dist.get(to[0])
        if dist is None:
            return -1

        return (dist['distance'] / team_speed) * 60 * 60;

