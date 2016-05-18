from flask import Flask, Markup, abort, render_template, request

import requests

import os, re

app = Flask(__name__)

subs = {
    # Substitutions (1)
    "witnesses": "these dudes I know",
    "allegedly": "kinda probably",
    "new study": "Tumblr post",
    "rebuild": "avenge",
    "space": "spaaace",
    "Google Glass": "Virtual Boy",
    "smartphone": u"Pok\u00e9dex",
    "electric": "atomic",
    "senator": "Elf-lord",
    "car": "cat",
    "election": "eating contest",
    "congressional leaders": "river spirits",
    "Homeland Security": "Homestar Runner",
    "could not be reached for comment": "is guilty and everyone knows it",
    # Substitutions 2
    "debate": "dance-off",
    "self driving": "uncontrollably swerving",
    "poll": "psychic reading",
    "candidate": "airbender",
    "drone": "dog",
    "vows to": "probably won't",
    "at large": "very large",
    "successfully": "suddenly",
    "expands": "physically expands",
    "first-degree": "friggin' awful",
    "second-degree": "friggin' awful",
    "third-degree": "friggin' awful",
    "an unknown number": "like hundreds",
    "front runner": "Blade Runner",
    "global": "spherical",
    "years": "minutes",
    "minutes": "years",
    "no indication": "lots of signs",
    "urged restraint by": "drunkenly egged on",
    "horsepower": "tons of horsemeat",
    # Substitutions 3
    "gaffe": "magic spell",
    "ancient": "haunted",
    "star-studded": "blood-soaked",
    "remains to be seen": "will never be known",
    "silver bullet": "way to kill werewolves",
    "subway system": "tunnels I found",
    "surprising": "surprising (but not to me)",
    "war of words": "interplanetary war",
    "tension": "sexual tension",
    "cautiously optimistic": "delusional",
    "Doctor Who": "The Big Bang Theory",
    "win votes": u"find Pok\u00e9mon",
    "behind the headlines": "beyond the grave",
    "email": "poem",
    "Facebook post": "poem",
    "tweet": "poem",
    "Facebook CEO": "this guy",
    "latest": "final",
    "disrupt": "destroy",
    "meeting": u"m\u00e9nage \u00e0 trois",
    "scientists": "Channing Tatum and his friends",
    "you won't believe": "I'm really sad about",
}

pattern = ("\\b"
           + "\\b|\\b".join(re.sub("[ -]", "[ -]", key)
                            + ("(s|')?" if not key.endswith("s") else "'?") \
                            for key in subs.keys())
           + "\\b")
pattern = re.compile(pattern, flags=re.IGNORECASE)

# For easier matching, lower-case, space (if hyphenated), and escape the
# dictionary keys.
subs = dict((re.escape(k.lower().replace("-", " ")), v) \
            for k, v in subs.iteritems())


def xkcdify(content):
    """
    Replace text within a string as specified by the xkcd Substitutions comics.

    :param content: Original content with text to be replaced.
    :returns: Resulting content after xkcd substitutions.
    """
    def sub(matchobj):
        match = matchobj.group()
        key = re.escape(match).lower().replace("-", " ")

        # If the key doesn't exist, it's possible the pattern encountered the
        # plural or possessive form of a key.
        # TODO: has_key() is deprecated; use `item in dict`
        if subs.has_key(key):
            result = subs[key]
        elif subs.has_key(key.rstrip("'s")):
            result = subs[key.rstrip("'s")]
            if key.endswith("s"):
                result = result + "s"
            elif key.endswith("'"):
                result = result + "'"
        else:
            return match

        return ("<span class=\"substitution\" title=\""
                + match
                + "\">"
                + result
                + "</span>")

    # TODO: Use BeautifulSoup to replace only contents of elements.
    #       Otherwise, the span tag can get into alt text...
    return pattern.sub(sub, content)


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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/xkcdify')
def generate():
    readability = ReadabilityAPI()
    article_url = request.args.get('url', '')
    error = None

    try:
        resp = readability.parse(article_url)
        xkcd_title = xkcdify(resp['title'])
        xkcd_content = xkcdify(resp['content'])
    except ConfidenceError as e:
        error = ("Looks like the content at the URL won't work well."
                 + "Try a different URL!")
    except ReadabilityError as e:
        try:
            # Display the API's error message if it had any.
            resp_json = e.resp.json()
            if resp_json['error']:
                error = resp_json['messages']
        except (KeyError, ValueError):
            app.logger.error(e.msg)
            app.logger.error(e.resp.text)

        # If the response didn't have any error messages, display a general
        # error message since it's likely the API is experiencing problems.
        if not error:
            error = ("The service is having unexpected issues."
                     + "Please try again later.")
    except Exception as e:
        app.logger.error(e)
        error = "Encountered an unknown error."

    if error:
        return render_template('error.html', error=error)

    return render_template('xkcd.html',
                           xkcd_title=Markup(xkcd_title),
                           xkcd_content=Markup(xkcd_content))


if __name__ == '__main__':
    app.run(debug=True)
