def create_app():
    from flask import Flask
    from .slack import slack_route

    app = Flask(__name__)
    app.secret_key = "flask secret key"
    app.config['slack_token'] = "xoxb-3745296232272-4845927270291-uE78X8df2sNz6cC2MSfMsVlH"
    app.config[
        'client_id'] = "448686143800-onbdt28j1691i8jl3dutsl447u3kt9fo.apps.googleusercontent.com"
    app.config['client_secret'] = "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"
    app.config['JSON_AS_ASCII'] = False

    app.register_blueprint(slack_route.bp, url_prefix='/slack')

    return app


app = create_app()

@app.route('/ody/health')
def health():
    from flask import jsonify
    return jsonify(success=True)
