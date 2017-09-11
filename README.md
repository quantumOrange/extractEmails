# Extract Email Addresses From Gmail

Extracts all the sender email addresses from emails with a given label in gmail and saves a list of comma separated values (csv) in the format

    first name, second name, email address

Borrows liberally from gmail api example code.

## Usage

    python extractEmails.py nameOfLabel

The script expects to find your gmail secret credentials one level up at

    '../client_secret.json'

