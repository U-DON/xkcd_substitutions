import requests

import os

class ReadabilityError(Exception):
    """
    Exception that contains information about Readability API errors.

    :param message: Message describing where the API failed..
    :param response: Response from the API request that encountered an error.
    """

    def __init__(self, message, response):
        self.msg = message
        self.resp = response


class ConfidenceError(Exception):
    pass


class ReadabilityAPI():
    """Wrapper for the Readability Parser API."""

    BASE_URI = 'https://readability.com/api/content/v1'
    CONFIDENCE_RESOURCE = '/confidence'
    PARSER_RESOURCE = '/parser'

    def __init__(self):
        self.token = os.environ['READABILITY_TOKEN']

    def confidence(self, url):
        """
        Get the confidence of the API to process the resource at a URL.

        :param url: URL that Readability API will process.
        :returns: Confidence value for the URL.
        """
        resp = requests.get(self.BASE_URI + self.CONFIDENCE_RESOURCE,
                            params={'url': url})

        if not resp.ok:
            raise ReadabilityError("Failed to get confidence for URL: " + url,
                                   resp)

        return resp.json()['confidence']

    def parse(self, url):
        """
        Parse the resource at a URL if the API is sufficiently confident.

        :param url: URL that Readability API will parse.
        :returns: Response generated by the API from processing the resource.
        """
        confidence = self.confidence(url)
        if confidence < 0.5:
            raise ConfidenceError("Low confidence in parsing the article: "
                                  + str(confidence))

        resp = requests.get(self.BASE_URI + self.PARSER_RESOURCE,
                            params={'url': url, 'token': self.token})

        if not resp.ok:
            raise ReadabilityError("Failed to parse content at URL: " + url,
                                   resp)

        return resp.json()
