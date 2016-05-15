from flask import Flask, Markup, render_template, request

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
    # Test
    "London": "blah",
    "dollar": u"m\u00e9nage \u00e0 trois",
}

class ReadabilityAPI():
    BASE_URI = 'https://readability.com/api/content/v1'
    CONFIDENCE_RESOURCE = '/confidence'
    PARSER_RESOURCE = '/parser'

    def __init__(self):
        self.token = os.environ['READABILITY_TOKEN']

    def confidence(self, url):
        resp = requests.get(self.BASE_URI + self.CONFIDENCE_RESOURCE,
                            params={'url': url})
        confidence = resp.json()['confidence']
        return confidence

    def parse(self, url):
        if self.confidence(url) < 0.5:
            return {}

        resp = requests.get(self.BASE_URI + self.PARSER_RESOURCE,
                            params={'url': url, 'token': self.token})
        resp = resp.json()
        return resp

# For easier matching, lower-case and escape the dictionary keys.
subs = dict((re.escape(k.lower()), v) for k, v in subs.iteritems())

# TODO: Handle both spaces and dashes for multi-word keys.
pattern = re.compile("\\b" + "\\b|\\b".join(subs.keys()) + "\\b", flags=re.IGNORECASE)

def xkcdify(content):
    def sub(matchobj):
        match = re.escape(matchobj.group())
        if subs.has_key(match):
            result = subs[match]
        else:
            # If the matched string wasn't a valid key, it's likely that the
            # case-insensitive matching encountered an upper-case-containing
            # form of a lower-case key.
            result = subs[match.lower()]
        return "<span class=\"substitution\" title=\"" + match + "\">" + result + "</span>"

    return pattern.sub(sub, content)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=('POST',))
def generate():
    readability = ReadabilityAPI()
    article_url = request.form['url']
    resp = readability.parse(article_url)

    if not resp:
        abort(403)

    xkcd_title = xkcdify(resp['title'])
    xkcd_content = xkcdify(resp['content'])

    return render_template('xkcd_version.html', xkcd_title=Markup(xkcd_title), xkcd_content=Markup(xkcd_content))

if __name__ == '__main__':
    app.run(debug=True)
