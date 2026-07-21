from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from textwrap import dedent

from gql import Client, gql
from gql.client import SyncClientSession
from gql.transport.exceptions import TransportQueryError
from gql.transport.requests import RequestsHTTPTransport


class BixiError(Exception):
    """Raised when a Bixi API request fails."""


class BixiLoginError(BixiError):
    """Raised when authenticating with the Bixi API fails."""


@dataclass
class Station:
    """A Bixi bike-share station.

    Attributes:
        id: Unique identifier of the station.
        name: Display name of the station.
        lat: Latitude of the station.
        lng: Longitude of the station.
    """

    id: str
    name: str
    lat: float
    lng: float


@dataclass
class Ride:
    """A completed Bixi ride.

    Attributes:
        id: Unique identifier of the ride.
        start_time: Date and time the ride started.
        end_time: Date and time the ride ended.
        price: Price charged for the ride.
        duration: Duration of the ride.
        start_station_name: Name of the station where the ride started.
        end_station_name: Name of the station where the ride ended.
    """

    id: str
    start_time: datetime
    end_time: datetime
    price: float
    duration: timedelta
    start_station_name: str
    end_station_name: str


class Bixi:
    """Client for the Bixi GraphQL API.

    Attributes:
        GRAPHQL_URL: URL of the Bixi GraphQL endpoint.
    """

    GRAPHQL_URL = "https://secure.bixi.com/bikesharefe-gql"

    def __init__(self, session: SyncClientSession):
        """Create a client from an already-authenticated GraphQL session.

        Args:
            session: Authenticated GraphQL client session, as returned by
                `login`.
        """
        self._session = session

    @classmethod
    def login(cls, username: str, password: str) -> "Bixi":
        """Log into the Bixi API and return an authenticated client.

        Args:
            username: Bixi account username.
            password: Bixi account password.

        Returns:
            An authenticated Bixi client.

        Raises:
            BixiLoginError: If the login request fails, is rejected, or no
                session cookie is returned.
        """

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

    def rides(self, offset: int = 0) -> list[Ride]:
        """Get the current member's ride history.

        Args:
            offset: Number of most-recent rides to skip, for pagination.
                Defaults to 0, which returns the full ride history.

        Returns:
            List of rides, most recent first.

        Raises:
            ValueError: If `offset` is negative.
            BixiError: If the request to fetch rides fails.
        """
        if offset < 0:
            raise ValueError("Offset must be greater than 0")

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
            **({"startTimeMs": offset} if offset else {}),
        }

        try:
            result = self._session.execute(query)
        except TransportQueryError as e:
            raise BixiError(f"Failed to get trips: {e}") from e

        return [
            Ride(
                id=r["rideId"],
                start_time=datetime.fromtimestamp(int(r["startTimeMs"]) / 1000, UTC),
                end_time=datetime.fromtimestamp(int(r["endTimeMs"]) / 1000, UTC),
                price=float(r["price"]["amount"]),
                duration=timedelta(seconds=int(r["duration"]) / 1000),
                start_station_name=r["startAddressStr"],
                end_station_name=r["endAddressStr"],
            )
            for r in result["member"]["rideHistory"]["rideHistoryList"]
        ]

    def stations(self) -> list[Station]:
        """Get all Bixi stations currently in service.

        Returns:
            List of stations.

        Raises:
            BixiError: If the request to fetch stations fails.
        """

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
