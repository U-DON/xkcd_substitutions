from flask import Flask, Markup, abort, render_template, request

import config
from readability import ReadabilityError, ConfidenceError, ReadabilityAPI
import xkcd

import os

app = Flask(__name__)

configs = {
    'development': config.DevelopmentConfig,
    'production': config.ProductionConfig
}

env = os.environ['APP_ENV']
app.config.from_object(configs[env])

@app.route('/')
def index():
    return render_template('index.html', examples=xkcd.examples)

@app.route('/xkcdify/')
def xkcdify():
    readability = ReadabilityAPI()
    article_url = request.args.get('url', '')
    error = None

    try:
        resp = readability.parse(article_url)
        xkcd_title = xkcd.xkcdify(resp['title'])
        xkcd_content = xkcd.xkcdify(resp['content'])
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
            app.logger.error("Readability API encountered an issue. "
                             + e.msg
                             + "\n"
                             + e.resp.text)

        # If the response didn't have any error messages, display a general
        # error message since it's likely the API is experiencing problems.
        if not error:
            error = ("The service is having unexpected issues."
                     + "Please try again later.")
    except Exception as e:
        app.logger.error("Unhandled exception: " + e)
        error = "Encountered an unknown error."

    if error:
        return render_template('error.html', error=error)

    content = render_template('xkcd.html',
                              xkcd_title=Markup(xkcd_title),
                              xkcd_content=Markup(xkcd_content))

    if request.is_xhr:
        return content

    return render_template('base.html', content=Markup(content))

if __name__ == '__main__':
    app.run()
