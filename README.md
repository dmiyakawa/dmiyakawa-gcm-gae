A simple example for Google Cloud Messaging: GAE side.

Chrome Extension side:
https://github.com/dmiyakawa/dmiyakawa-gcm-extension

See also:
http://developer.chrome.com/apps/cloudMessaging.html

***

To try this on your environment, you need to add
secret.py that contains the following four constants.


* CLIENT_ID
* CLIENT_SECRET
* REFRESH_TOKEN
* ALLOWED_EMAIL

The first three should be prepared via Google APIs
Console. The last one should be your email address
associated with you Google Account.

Also you need to specify your GAE app id to app.yaml

***

Licensed under the Apache License, Version 2.0.
