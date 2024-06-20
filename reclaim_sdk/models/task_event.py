from datetime import datetime, date, timedelta

from reclaim_sdk.client import ReclaimAPICall
from reclaim_sdk.models.model import ReclaimModel
from reclaim_sdk.utils import to_datetime, from_datetime


class ReclaimTaskEvent(ReclaimModel):
    """
    Task events are a special case, as they cannot be created by the user.
    They are created by the API when a task is scheduled. The user can only
    update the start and end times of the event, pin the event or delete it.
    """

    _name = "Task Event"
    _required_fields = ["start", "end"]
    _endpoint = "/api/planner/event/move"

    def __init__(self, data: dict, **kwargs) -> None:
        super().__init__(data, **kwargs)

    @property
    def id(self):
        return self._data.get("eventId", None)

    @property
    def name(self):
        return self["title"]

    @name.setter
    def name(self, value):
        raise NotImplementedError("Task name cannot be changed in its event")

    @property
    def start(self) -> datetime:
        return to_datetime(self["eventStart"])

    @start.setter
    def start(self, value: datetime):
        self["eventStart"] = from_datetime(value)

    @property
    def end(self) -> datetime:
        return to_datetime(self["eventEnd"])

    @end.setter
    def end(self, value: datetime):
        self["eventEnd"] = from_datetime(value)

    @classmethod
    def search(
        cls,
        start: date = datetime.now().date(),
        end: date = datetime.now().date() + timedelta(days=1),
        **kwargs,
    ):
        params = {}
        params.update({"sourceDetails": True, "allConnected": True})
        params.update({"start": start, "end": end})
        with ReclaimAPICall(cls) as client:
            res = client.get("/api/events", params=params)
            res.raise_for_status()

        results = []

        for item in res.json():
            results.append(cls(data=item))

        return results

    def _create(self, **kwargs):
        """
        Task Events cannot be created by the user.
        """
        raise NotImplementedError("Task Events cannot be created by the user.")

    def delete(self, **kwargs):
        """
        Task Event cannot be deleted by the user.
        """
        raise NotImplementedError("Task Events cannot be deleted by the user.")

    def _update(self, **kwargs):
        """
        Updates the task event. Only the start and end times (event move).
        """
        params = {
            **kwargs,
            "start": self["start"],
            "end": self["end"],
        }
        with ReclaimAPICall(self) as client:
            res = client.post(
                f"{self._endpoint}/{self.id}",
                params=params,
            )
            res.raise_for_status()

        self._data = res.json()["events"][0]
