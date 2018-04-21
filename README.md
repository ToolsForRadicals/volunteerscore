# Tools for Radicals: Volunteer Score
This is a small web app that sorts Nationbuilder supporters by their likelihood to volunteer. It takes a Nationbuilder CSV export, and returns a list of Nationbuilder IDs, and an "inferred_support_score" between 1-5, where 5 is 'very likely to volunteer', and 1 is 'very unlikely to volunteer'

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

You can try a demo at https://volunteerscore.herokuapp.com

## How it works

Volunteerscore relies on the 2016 Census questions on volunteering. For the most accurate predictions, it's best if your Nationbuilder export contains:

* A valid Primary Address
* A valid Gender
* A valid Age / Date of Birth

If that data isn't in the CSV file, the app will estimate the supporter's age and gender based on the supporter's first name.
If the supporter doesn't have a valid primary address, it will attempt to use the 'primary_zip' postcode field.

Despite the relative simplicity of the model (Just Age, Gender, Suburb and Volunteer score), I've found it to be extremely effective at prioritising calling and doorknock lists.

# Running Locally Deploying to Heroku

By default, Volunteerscore uses the GoogleV3 geocoder. You're limited to 2,500 address lookups per day. If you're planning on geocoding more than 2500 address you can either:
* Provide a Google Maps Geocoder API key
* Use the OpenStreetMap Nominatim Geocoder (Which is less accurate, but less restrictive)

You can specify your geocoder when deploying to Heroku - Just type "Nominatim" if you want to use Nominatim.


#Helping Out

This is beta software. Obvious improvements include direct Nationbuilder API integration. Pull requests welcome, code improvements welcome. Design especially welcome. 
If you're interested in detailed Machine Learning / Predictive modelling of volunteers, donors or voters please drop me a line:

volunteerscore@iamcarbonatedmilk.com


# Requirements, Caveats
This app assumes that you have a CSV file that contains at least some of the following fields:

* nationbuilder_id
* born_at
* sex
* first_name
* primary_address1
* primary_city
* primary_state

It assumes that all the supporters are located in Australia, and tries to geocode them as such.

Limitations:
* Volunteer Score works best when given a list of supporters in a single relatively homogenous geographic area. Because it returns their likelihood to volunteer *in comparison to their neighbours* , it works less well when you include supporters from extremely geographically diverse regions. (A '5' in remote NT and a '5' in inner Sydney aren't equally likely to volunteer as each other, they're just the most likely in their street or suburb)

* Geocoding is slow, done on a supporter by supporter basis and is not cached by the app. If all supporters have a valid primary address, it may take a long time to geocode them all. If it's taking too long, just upload the supporters with postcodes only (no primary_address1 field)

