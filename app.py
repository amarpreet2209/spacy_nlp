from flask import Flask,request,jsonify
app = Flask(__name__)

import spacy
nlp = spacy.load('en')

import nltk
nltk.download('stopwords')

from nltk.stem.porter import PorterStemmer
porter_stemmer = PorterStemmer()

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from word2number import w2n

import assemblyai
aai = assemblyai.Client(token='39f8f26db4c546c99308fba032eda3dd')

import os
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))



@app.route('/', methods=["POST"])
def example():

	target = os.path.join(UPLOAD_FOLDER,'')

	if not os.path.isdir(target):
		os.mkdir(target)

	for f in request.files.getlist("file"):
		destination = "/".join([target,f.filename])
		f.save(destination)
		
		transcript = aai.transcribe(filename=f.filename)
		while transcript.status != 'completed':
			transcript = transcript.get()
		text = transcript.text

	example_sent = text

	stop_words = set(stopwords.words('english'))
	 
	word_tokens = word_tokenize(example_sent)

	filtered_sentence = []
	filtered_sentence = [w for w in word_tokens if not w in stop_words]
	filtered_sentence = ' '.join(word for word in filtered_sentence)

	doc = nlp(filtered_sentence)

	temp_no_of_dogs = []
	temp_no_of_cats = []

	is_dog = False
	is_cat = False

	is_bleeding = False
	is_fire = False
	is_dead = False
	is_injured = False

	for token in doc:
	  if(token.lemma_ == 'dog'):
	    is_dog = True
	  elif(token.lemma_ == 'cat'):
	    is_cat = True
	  elif(token.lemma_ == 'bleeding'):
	    is_bleeding = True
	  elif(token.lemma_ == 'fire'):
	    is_fire = True
	  elif(token.lemma_ == 'die'):
	    is_dead = True    

	d = []

	for token in doc:
	    d.append((token.lemma_,token.pos_))

	dogs_temp_ar = []
	cats_temp_ar = []

	cat_index = 9999
	dog_index = 9999


	for i in range(len(d)):
	  a,k = d[i]
	  if a =='cat':
	    cat_index = i
	    cats_temp_ar.append(w2n.word_to_num(d[i-1][0]))

	if cat_index!= 9999:
	  for i in range(cat_index,len(d)):
	    a,k = d[i]
	    if k =='NUM' and d[i-2][0]=='cat':
	      if d[i+1][1]=='VERB':
	        cats_temp_ar.append(w2n.word_to_num(a))
	        break
	num_cats = 0
	for i in cats_temp_ar:
	  num_cats += i

	for i in range(len(d)):
	  a,k = d[i]
	  if a =='dog':
	    dog_index = i
	    dogs_temp_ar.append(w2n.word_to_num(d[i-1][0]))

	if dog_index!= 9999:
	  for i in range(dog_index,len(d)):
	    a,k = d[i]
	    if k =='NUM' and d[i-2][0]=='dog':
	      if d[i+1][1]=='VERB':
	        dogs_temp_ar.append(w2n.word_to_num(a))
	        break
	num_dogs = 0
	for i in dogs_temp_ar:
	  num_dogs += i

	result =  [{
	"is_dog" : str(is_dog),
	"is_cat" : str(is_cat),
	"is_bleeding" : str(is_bleeding),
	"is_fire" : str(is_fire),
	"is_dead" : str(is_dead),
	"is_injured" : str(is_injured) },
	{
	"num_dogs" : str(num_dogs),
	"num_cats" : str(num_cats)
	}]

	return jsonify(result)

app.run(debug=True)


