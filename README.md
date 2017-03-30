Udacity - Blog Website - Project 2 - Filipe Costa
============

This is a front-end (HTML, CSS, front-end frameworks like Bootstrap) and back-end (Python with Jinja2 and Google App Engine - GAE)
project intended to provide a blog tool.
The blog only allows text content for both posts and comments. User can edit/delete posts and comments,
also like other user's posts.
Users can registrate themselves using just username and password, e-mail is optional.
Sensitive information (like password) of the blog is stored using hash algorithms.

## Libraries
This project use external library other than the ones included in Python Source Libraries.
The external libraries are:
1. google.appengine

Please make sure to have it installed before moving forward.
Aditional instructions on how to install GAE (MacOS ONLY) are provided below:
1. Install [Python](https://www.python.org/). Specific version 2.7 in order to the GAE SDK to work properly
2. Install [Google Cloud SDK](https://cloud.google.com/sdk/) and follow the instructions in this page
3. After the installation, from the terminal, run the command
   1. `gcloud components install app-engine-python`
4. [Make yourself a new GAE project](https://cloud.google.com/appengine/docs/standard/python/console/#create)
5. Ok, time to test it.

## Running locally
You can test a fully working live demo following these steps:
1. Open a terminal and check Python is installed and running properly
   1. You can try 'python --version' in terminal and check the output
2. Go to `/project` folder in terminal
3. Verify you can run the command below.
   1. `dev_appserver.py`
4. No errors should araise and `localhost:8080` is up and running

## Deploy to Google Cloud
You can deploy a fully working live app following these steps:
1. Go to `/project` folder in terminal
2. Verify you can run the command below and insert `Y` for the input after running it
   1. `gcloud app deploy`
3. VERY IMPORTANT STEP: GAE uses index on tables to improve performance and make sure users are not consuming a lot
of resources (freemium account, so don't abuse rule :) ). The file `index.yaml` must be sent to the server. Just run:
   1. `gcloud app datastore create-indexes index.yaml`
4. Wait for some time until the indexes are updated and created. You can follow the status in [here](https://console.cloud.google.com/datastore/indexes)
5. No errors should araise and your project should be running on `https://<your_gae_project>.appspot.com`


## [Contacting the Author](mailto:s.costa.filipe@gmail.com)
Click above and feel free to get in touch in case of trouble or suggestions.