# start virtual environment in venv folder
# usage : source act.sh
source ./venv\\youthflask\\Scripts\\activate
# if there is an error msg
# like : AttributeError: 'module' object has no attribute 'SSLContext'
# use this environment setting
# App name(app.py) can be replaced by your app name
export FLASK_APP=app.py