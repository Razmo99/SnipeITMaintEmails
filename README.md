# SnipeITMaintEmails
Sends Reminder emails when Asset Maintenances are due on Snipe-IT

Set to send reminders at 8:00am everyday

## TODO
- [ ] Configurable reminder times.
- [x] functionality to send to non local mail server

## How it works
1. Connects to Snipe-IT instance and retrieves all Maintenances.
2. Iterates over the maintenances checks the start date against time now
   1. Currently hard coded to be >= 30 (days) delta from time now
3. If any maintenances meet the above condition's they are added to a result list.
4. The results are entered into the MaintenanceMailer with processes them into a table
5. An email is then send with this information.   

## Requirements
- Snipe-IT
- API Key

## Installing
1. Download the Repo and place it on your docker host.
1. Create a new file next to the "docker-compose.yml" called ".env" enter in all the required [docker environment variables](#docker-environment-variables)
1. `docker-compose up --build`
   1. Don't add the `-d` flag so you can see if any errors occur on startup.\
   If it starts successfully then stop and start the container again in detached mode.

## Docker Environment Variables
- SNIPEIT_SERVER {string} # URL of the Snipe-IT Server ***Required**
- SNIPEIT_SERVER_NAME {string} # Name of the Snipe-IT Server ***Required**
- SNIPEIT_TOKEN {string} # API Token from Snipe-IT ***Required**
- MAIL_SERVER {string} # DNS of local exchange server ***Required**
- MAIL_SERVER_PORT {string} # mail port ***Required**
    - Defaults to 587
- MAIL_SERVER_USE_TLS # connected to the smtp using starttls
- MAIL_SERVER_USERNAME # Credentials
    - ***Required if using TLS**
    - Defaults to sender if not specified
- MAIL_SERVER_PASSWORD # Credentials
    - ***Required if using TLS**
- MAIL_SENDER_ADDRESS {string} # what email to send from ***Required**
- MAIL_RECEIVER_ADDRESS {string} # Who to send the mail to ***Required**
- TZ = {string} # Timezone
    - i.e `Australia/Sydney`
- LOG_SAVE_LOCATION {string} # Location to save log file
    - This can be just a file name i.e "snipeit_maint_emails.log" or the full directory path "/app/storage/snipeit_maint_emails.log"
 - DEBUG {bool} # logging level
    - Runs the job immediately on launch to make it quicker to resolve errors

 _If no "save locations" are specified default names will be used and files will be placed in the working dir of the app_   

## Dockerfile
Slightly modified version of the dockerfile layed out [here](https://www.kevin-messer.net/how-to-create-a-small-and-secure-container-for-your-python-applications/)