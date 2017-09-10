# Extract Email Addresses From Gmail

Extracts all the sender email addresses from emails with a given label in gmail and saves a list of comma seperated values (csv) in the format

    first name, second name, email address

Borrows librally from gmail api example code.

## Use

    python extractEmails.py nameOfLabel

The script expects to find your gmail secret credentials at

    '../client_secret.json'

