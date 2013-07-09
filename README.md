A simple example for Google Cloud Messaging

Before trying this, you should understand what GCM is.
http://developer.chrome.com/apps/cloudMessaging.html

To try this on your localhost (or remote server),
You need to create secret.py that contains three secrets
GCM will provide to you.

* CLIENT_ID
* CLIENT_SECRET
* REFRESH_TOKEN

After launching the instance, you need to
register extension's channel Ids to the server
by accessing (host-name)/StoreChannelId/(channel-id).
There's no comfortable-to-use UI there.
There's no UI for deleting channel-id either.

Licensed under the Apache License, Version 2.0.
