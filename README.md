A simple example for Google Cloud Messaging

Before trying this, you should understand what GCM is.
http://developer.chrome.com/apps/cloudMessaging.html

To try this on your localhost (or remote server),
You need to create secret.py that contains three secrets
GCM will provide to you.

* CLIENT_ID
* CLIENT_SECRET
* REFRESH_TOKEN

Possibly good news:
You don't need to deploy this to GAE production environment
(using appcfg.py).

Because GCM doesn't require us to put messaging server on the cloud,
you can just play with this experimental code with dev_appserver.py
with real push messages.
