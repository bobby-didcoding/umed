# Bobby Stearman task response

***
***


## Prerequisites
* [Docker & Docker Compose](https://docs.docker.com/desktop/) (<span style="color:orange">Local Development with Docker</span> only)

***
***


## Environment variable and secrets
1. Create a .env file from .env.template
    ```
    #Unix and MacOS
    cp .env.template .env

    #windows
    copy .env.template .env
    ```

***
***

## Fire up Docker:

>Note: You will need to make sure Docker is running on your machine!

Use the following command to build the docker images:
```
docker-compose -f  up -d --build
```
***
***


## Notes
I decided to submit some code along with some notes as this should give you a better of my though process. I haven't fleshed it out fully as I didn't want to spend more than a couple of hours on the task.

## Assumptions
Bulk emails will be sent on a schedule/cron - I would need more information on this as you have not mentioned how and when the emails will be sent.
Likewise, I can't find any way of linking a care_provider to a study or patient. therefore, I have added 'XXX' to the email template.
Lastly, there was not app password or any mention of an email host for the given email account. This is required when sending via the likes of gmail and outlook.

## New stack
- Docker
- Python
- Celery
- Celery-Beat
- Redis
- Flower

Using Celery, Beat, Redis & Flower allows me to create ADHOC and scheduled tasks (see core/celery.py)

## Logging
I have wired up some logging that points to logs/app.log and logs/celery.log and made sure user information is removed (only using UUID)

## Email backend
I am using django-mailer as the email backend as it allows me to store emails in a database.

## Triggering an email (for testing)
I have also added an admin action that alls a celery task (tasks.tasks.create_email). An email will only be sent to Patient if the 'in_study' method returns.

## App secrets
I've used python-dotenv to store secrets in a .env file.

## Scaling
Django can scale to send thousands at a time but I believe Amazons SES & bulk sending service would be more suitable for bulk sending to millions. 

## Exceptions
Send failures and bounce back on email tasks are problematic but can be caught relatively easily. I would write a secondary cron job to cycle through email send failure and track each attempt until a maximum retry limit is reached. Clear logging throughout would be necessary.


***
***




