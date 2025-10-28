from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GarminClient:
    """
    A wrapper class for the garminconnect library to simplify interactions
    with the Garmin Connect API.
    """
    def __init__(self, email, password):
        """Initializes the Garmin client."""
        self.email = email
        self.password = password
        self.client = None

    def login(self):
        """Logs in to Garmin Connect."""
        if self.client and self.client.username:
            logger.info("Client already logged in for %s", self.email)
            return True
        try:
            self.client = Garmin(self.email, self.password)
            self.client.login()
            logger.info("Garmin Connect login successful for %s", self.email)
            return True
        except (
            GarminConnectConnectionError,
            GarminConnectTooManyRequestsError,
            GarminConnectAuthenticationError,
        ) as e:
            logger.error("Error during Garmin Connect login: %s", e)
            return False

    def get_user_summary(self):
        """Gets user summary."""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        return self.client.get_user_summary(today)

    def get_activities(self, limit=20, start=0):
        """Gets a list of activities."""
        return self.client.get_activities(start, limit)

    def get_activity_details(self, activity_id):
        """Gets details for a specific activity."""
        return self.client.get_activity_details(activity_id)

    def download_activity(self, activity_id, dl_format):
        """Downloads an activity file in the specified format."""
        return self.client.download_activity(
            activity_id, dl_format=self.client.ActivityDownloadFormat[dl_format]
        )

    def get_devices(self):
        """Gets a list of user's devices."""
        return self.client.get_devices()

    def get_heart_rate_data(self, date):
        """Gets heart rate data for a specific date."""
        return self.client.get_heart_rates(date)

    def get_sleep_data(self, date):
        """Gets sleep data for a specific date."""
        return self.client.get_sleep_data(date)

    def get_stress_data(self, date):
        """Gets stress data for a specific date."""
        return self.client.get_stress_data(date)

    def __getstate__(self):
        """Prepare the object for serialization (for Flask session)."""
        return {'email': self.email, 'password': self.password}

    def __setstate__(self, state):
        """Restore the object from deserialization."""
        self.__init__(state['email'], state['password'])
        # The client will be re-initialized and logged in on the first API call
        # that needs it, avoiding unnecessary logins on every request.