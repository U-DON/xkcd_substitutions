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

# For easier matching, lower-case and escape the dictionary keys.
subs = dict((re.escape(k.lower()), v) for k, v in subs.iteritems())

# TODO: Handle both spaces and dashes in certain words.
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
    article_url = request.form['url']
    readability_api = 'https://readability.com/api/content/v1/'
    token = os.environ['READABILITY_TOKEN']

    resp = requests.get(readability_api + 'confidence', params={'url': article_url})
    confidence = resp.json()['confidence']

    if confidence < 0.5:
        abort(403)

    resp = requests.get(readability_api + 'parser', params={'url': article_url, 'token': token})
    resp = resp.json()
    original_title = resp['title']
    original_content = resp['content']
    xkcd_title = xkcdify(original_title)
    xkcd_content = xkcdify(original_content)

    return render_template('xkcd_version.html', xkcd_title=Markup(xkcd_title), xkcd_content=Markup(xkcd_content))

if __name__ == '__main__':
    app.run(debug=True)
