from flask import Markup

from bs4 import BeautifulSoup
from bs4.element import NavigableString

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

# List of examples to display on the front page.
examples = [
    {
        'url': "http://www.businessinsider.com/report-10-million-self-driving-cars-will-be-on-the-road-by-2020-2015-5-6",
        'old_title': "10 million self-driving cars will be on the road by 2020"
    },
    {
        'url': "http://www.wired.com/2011/05/ucsd-skeleton-fight/",
        'old_title': "Scientists Fight University of California to Study Rare Ancient Skeletons"
    },
    {
        'url': "http://www.npr.org/2016/01/28/464640980/the-last-candidate-to-skip-the-final-iowa-debate-ronald-reagan",
        'old_title': "The Last Candidate To Skip The Final Iowa Debate? Ronald Reagan"
    }
];

def xkcdify(content):
    """
    Replace text within a string as specified by the xkcd Substitutions comics.

    This takes an HTML fragment and replaces the text accordingly, wrapping the
    resulting substitutions in span tags.

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

        return result

    # Get all the plain text strings in the document without their tags.
    soup = BeautifulSoup(content, 'html.parser')
    content_strings = [element for element in soup.recursiveChildGenerator() \
                       if type(element) == NavigableString]

    for string in content_strings:
        # Use index to track where the current substring of plain text starts.
        index = 0

        # Use wrapper to string together plain text and span elements.
        wrapper_tag = soup.new_tag('span')

        # Upon each match, write to the wrapper the substitution result and the
        # plain text preceding it. Then update index to the position after the
        # matched substring to mark the start of the next plain text substring.
        for m in pattern.finditer(string):
            wrapper_tag.append(soup.new_string(string[index:m.start()]))
            replacement = soup.new_tag('span',
                                       title=m.group(),
                                       **{'class': 'substitution'})
            replacement.string = sub(m)
            wrapper_tag.append(replacement)
            index = m.end()

        # Keep the original plain text unless substitutions were made.
        if wrapper_tag.contents:
            # Only append the rest of the string if substitutions were made,
            # because we would otherwise be left with the full original string.
            wrapper_tag.append(string[index:])
            string.replace_with(wrapper_tag)
            wrapper_tag.unwrap()

    return unicode(soup)

for example in examples:
    example['new_title'] = Markup(xkcdify(example['old_title']))
