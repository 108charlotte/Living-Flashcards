# Commands to run (please run these in the root of the repo (/Living-Flashcards, not /living_flashcards)): 
python -m venv .venv  
if on mac: source .venv/bin/activate  
if on windows: .venv\Scripts\activate
pip install -r requirements.txt  

To view the application: 
1. navigate to the living_flashcards folder
2. run "python manage.py runserver" 
3. add /flashcards/ to the end of the url of the window which appears

- quick note: if we add search functionality it will be a new app (flashcards is another example of an app), so we probably shouldn't code everything in the flashcards.html file (just the figma for flashcards)

# Resources: 
python spaced repetition library: https://github.com/open-spaced-repetition/py-fsrs (requires MIT license attribution)
setting up auth in django: https://docs.djangoproject.com/en/6.0/topics/auth/

test user info: 
TestUser
testingtesting123