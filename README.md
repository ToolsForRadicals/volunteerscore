# Tools for Radicals: Volunteer Score
This is a small web app that sorts Nationbuilder supporters by their likelihood to volunteer. It takes a Nationbuilder CSV export, and returns a list of Nationbuilder IDs, and an "inferred_support_score" between 1-5, where 5 is 'very likely to volunteer', and 1 is 'very unlikely to volunteer'

You can try a demo at https://volunteerscore.herokuapp.com

## How it works

Volunteerscore relies on the 2016 Census questions on volunteering. For the most accurate predictions, it's best if your Nationbuilder export contains:

* A valid Primary Address
* A valid Gender
* A valid Age / Date of Birth

If that data isn't in the CSV file, the app will estimate the supporter's age and gender based on the supporter's first name.
If the supporter doesn't have a valid primary address, it will attempt to use the 'primary_zip' postcode field.

Despite the relative simplicity of the model (Just Age, Gender, Suburb and Volunteer score), I've found it to be extremely effective at prioritising calling and doorknock lists.

Pull requests welcome, code improvements welcome. Design especially welcome

# Deploying to Heroku

There are no external dependencies