# logwatchackingparser
Parse apache log entries for hacking attempts reported by logwatch

Logwatch is an awesome tool which executes and alerts you to various noteworthy events happening on the server. One of such events include notification of "hacking attempts" found inside the apache logs. The problem is that although it provides IP addresses of the offenders, it does not include the specific incidents or additional details from the apache log. This script pulls the offending IP addresses from the logwatch document, locates the associated apache access.log entries and parses them to a new file for review. I have logwatch set to paste new files in a random directory inside my apache intallation, but this script could easily attach the newly created file to the daily logwatch email.
