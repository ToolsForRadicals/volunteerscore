# Tools for Radicals: Volunteer Score
This is a small web app that integrates with your Nationbuilder. It takes a list you've already created in Nationbuilder, ranks the supporters on the list by their likelihood to volunteer, then splits the list in to three segments: "My List_High" "My List_Medium" and "My List_Low".
That way, you can call your best volunteer prospects first!

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

You can try a demo at https://volunteerscore.herokuapp.com

## How it works

Volunteerscore relies on the 2016 Census questions on volunteering. For the most accurate predictions, it's best if your People records contain:

* A valid Primary Address
* A valid Gender
* A valid Age / Date of Birth

If that data isn't available, the app will estimate the supporter's age and gender based on the supporter's first name.
If the supporter doesn't have a valid primary address, it will attempt to use the 'primary_zip' postcode field.

Despite the relative simplicity of the model (Just Age, Gender, Suburb and Volunteer score), I've found it to be extremely effective at prioritising calling and doorknock lists.

# Deploying to Heroku

Depending on your list size, running Volunteerscore may take a long while. Future releases might improve this


#Helping Out

This is beta software. Pull requests welcome, code improvements welcome. Design especially welcome. 
If you're interested in detailed Machine Learning / Predictive modelling of volunteers, donors or voters using your own data, please drop me a line:

volunteerscore@iamcarbonatedmilk.com


# Requirements, Caveats
Volunteer Score assumes that you use the primary address and primary zip fields to store supporters addresses. It also assumes that your supporters are in Australia.

Limitations:
* Volunteer Score works best when given a list of supporters in a single relatively homogenous geographic area. Because it returns their likelihood to volunteer *in comparison to their neighbours* , it works less well when you include supporters from extremely geographically diverse regions. (A '5' in remote NT and a '5' in inner Sydney aren't equally likely to volunteer as each other, they're just the most likely in their street or suburb)


# TODO

* Use Nationbuilder lat/lng instead of just zip code
* Error handling of all sorts (Check 200 responses in API, write exception handling for poorly formatted supporters)


