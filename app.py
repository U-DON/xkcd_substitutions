from flask import Flask, Markup, abort, render_template, request

from readability import ReadabilityError, ConfidenceError, ReadabilityAPI

from xkcd import xkcdify

app = Flask(__name__)

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

    return render_template('xkcd.html',
                           xkcd_title=Markup(xkcd_title),
                           xkcd_content=Markup(xkcd_content))

if __name__ == '__main__':
    app.run(debug=True)
