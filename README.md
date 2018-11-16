# CheckformissingEmailAlert
Python 3 - We check a mailbox (IMAP) to see if an email is NOT present, then send another email if its not found

#But Why?
I made this because we had a third party service that would send an email if a job completed normally, on a nightly basis.  If the job didn't complete normally, we simply wouldn't get an email.  Ideally, you want an alert if something goes wrong, not if everything goes as planned. In all likelihood, no one is going to notice a MISSING email.  

This program will check an inbox via IMAP. It will match a sender and a subject. If a match is found, ALL emails are deleted and the program exits.  If the email is not found, we generate an email and a text via SMTP.

The program can use redundant email servers, in case one fails. It will also generate an email if we can't check emails via IMAP. The SMTP portion was made to be as fault tolerant as possible.

