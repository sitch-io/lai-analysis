from twilio.rest import TwilioPricingClient


class TwilioCarriers(object):
    def __init__(self, sid, token):
        self.pricing_client = TwilioPricingClient(sid, token)
        self.carrier_reference = []

    def initialize_carrier_reference(self, country_code):
        self.carrier_reference = self.get_providers_for_country("US")
        return

    def get_carrier_name(self, mcc, mnc):
        carrier = "Unrecognized Carrier"
        for ref_row in self.carrier_reference:
            if mcc == ref_row["mcc"] and mnc == ref_row["mnc"]:
                carrier = ref_row["carrier"]
                break
        return carrier

    def get_providers_for_country(self, iso_country):
        """Use an ISO country code to get all MCC/MNC for a country"""
        retval = []
        country = self.pricing_client.messaging_countries().get(iso_country)
        for provider in country.outbound_sms_prices:
            interesting_data = {"mcc": provider["mcc"],
                                "mnc": provider["mnc"],
                                "carrier": provider["carrier"]}
            retval.append(interesting_data)
        return retval
