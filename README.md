# C4GT Github App Backend
The C4GT is the backend for the [C4GT Community Support App](https://github.com/apps/c4gt-community-support/).

It is primarily an event driven application based around [Github Webhooks](https://docs.github.com/en/webhooks/webhook-events-and-payloads) received via a [Github App Installation](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/using-webhooks-with-github-apps).

It's build on the [quart](https://pgjones.gitlab.io/quart/) web microframework.


# How to Contribute
- Raise or pick a ticket from open issues
- All forks should be pulled from the `development` branch

## Setup
set up .env file
install dependencies in requirements.txt
execute "flask run" in bash to start app

## Reference
[Github Webhook Reference](https://docs.github.com/en/webhooks-and-events/webhooks/webhook-events-and-payloads)
