from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from textwrap import dedent

from gql import Client, gql
from gql.client import SyncClientSession
from gql.transport.exceptions import TransportQueryError
from gql.transport.requests import RequestsHTTPTransport


class BixiError(Exception):
    """Bixi API client error."""


class BixiLoginError(BixiError):
    """Bixi login error."""


@dataclass
class Station:
    """Bixi station data class."""

    id: str
    name: str
    lat: float
    lng: float


@dataclass
class Trip:
    """Bixi trip data class."""

    ride_id: str
    start_time_ms: datetime
    end_time_ms: datetime
    price: float
    duration: timedelta
    start_station_name: str
    end_station_name: str


class Bixi:
    """Bixi API client."""

    GRAPHQL_URL = "https://secure.bixi.com/bikesharefe-gql"

    def __init__(self, session: SyncClientSession):
        self._session = session

    @classmethod
    def login(cls, username: str, password: str) -> "Bixi":
        """Logs into Bixi using `username`, `password` and `account` returning an
        authenticated Bixi client object."""

        transport = RequestsHTTPTransport(url=cls.GRAPHQL_URL, headers={"Accept-Language": "en-US,en;q=0.9"})
        transport.connect()
        client = Client(transport=transport)
        session = SyncClientSession(client)

        query = gql(
            dedent("""
                mutation LogIn($params: LogInInput!) {
                    logIn(params: $params) {
                        success
                        mfaId
                    }
                }
            """)
        )
        query.variable_values = {"params": {"username": username, "password": password}}

        try:
            result = session.execute(query)
        except TransportQueryError as e:
            raise BixiLoginError(f"Failed to log in: {e}") from e

        if not result["logIn"]["success"]:
            raise BixiLoginError(f"Failed to log in: {result['logIn']['error']}")

        if transport.response_headers is None or not transport.response_headers.get("set-cookie"):
            raise BixiLoginError("Failed to log in: No cookie set")

        return Bixi(session)

    def trips(self, offset: int = 0) -> list[Trip]:
        """Gets all trips between `start_time` and `end_time`."""

        query = gql(
            dedent("""
                query GetCurrentUserRides($startTimeMs: String, $memberId: String) {
                    config {
                        rideHistory {
                            enabled
                        }
                        comembers {
                            enabled
                        }
                    }
                    member(id: $memberId) {
                        id
                        rideHistory(startTimeMs: $startTimeMs) {
                            limit
                            hasMore
                            rideHistoryList {
                                rideId
                                startTimeMs
                                endTimeMs
                                price {
                                    amount
                                }
                                duration
                                startAddressStr
                                endAddressStr
                            }
                        }
                    }
                }
            """)
        )
        query.variable_values = {
            **({"startTimeMs": offset if offset is not None else None}),
        }

        try:
            result = self._session.execute(query)
        except TransportQueryError as e:
            raise BixiError(f"Failed to get trips: {e}") from e

        return [
            Trip(
                ride_id=r["rideId"],
                start_time_ms=datetime.fromtimestamp(int(r["startTimeMs"]) / 1000, UTC),
                end_time_ms=datetime.fromtimestamp(int(r["endTimeMs"]) / 1000, UTC),
                price=float(r["price"]["amount"]),
                duration=timedelta(seconds=int(r["duration"]) / 1000),
                start_station_name=r["startAddressStr"],
                end_station_name=r["endAddressStr"],
            )
            for r in result["member"]["rideHistory"]["rideHistoryList"]
        ]

    def stations(self) -> list[Station]:
        """Gets all stations."""

        query = gql(
            dedent("""
                query GetSystemSupply($input: SupplyInput) {
                    supply(input: $input) {
                        stations {
                        stationId
                        stationName
                        location {
                            lat
                            lng
                        }
                        }
                    }
                }
            """)
        )

        try:
            result = self._session.execute(query)
        except TransportQueryError as e:
            raise BixiError(f"Failed to get stations: {e}") from e

        return [
            Station(
                id=s["stationId"],
                name=s["stationName"],
                lat=s["location"]["lat"],
                lng=s["location"]["lng"],
            )
            for s in result["supply"]["stations"]
        ]
