import re

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
        if key in subs:
            result = subs[key]
        elif key.rstrip("'s") in subs:
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
