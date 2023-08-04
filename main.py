import api, db
import os


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    api.app.run(host="0.0.0.0", port=8081, debug=True)
