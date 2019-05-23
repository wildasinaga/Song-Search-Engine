from flask import Flask, render_template, request
from nltk.stem import PorterStemmer
from collections import Counter
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
import math
import copy
import json
import webbrowser

app = Flask(__name__)

kataDepan = set(stopwords.words('english'))
datasets = pd.read_csv("data/datasets.csv")
dokumen = datasets.values.tolist()
stemmer = PorterStemmer()
stemmedDoc, indx = [], []


for baris in dokumen:
	arrayTempBaris = baris[2].split()

	# 2 - Filtering - cek bila kata memiliki kata depan yang harus dihapus
	arrayTempBaris = [x for x in arrayTempBaris if x not in kataDepan]
	tempBaris = " ".join(arrayTempBaris)

	# 3 - Stemming - menghapus awalan
	tempBaris = stemmer.stem(tempBaris)
	stemmedDoc.append(tempBaris.split())
	
for record in stemmedDoc:
	for kata in record:
		if kata not in indx:
			indx.append(kata)
			

df_index = pd.DataFrame({
	'kata':indx
	})
	
for i in range(len(stemmedDoc)):
	terdeteksi = []
	for kata in indx:
		terdeteksi.append(stemmedDoc[i].count(kata))
	df_index[i+1] = pd.Series(terdeteksi)

# print(	df_index)
df_index.to_csv("data/index.csv", index=False)

def process(query):
    que = query 
    kataDepan = set(stopwords.words('english'))
    datasets = pd.read_csv("data/datasets.csv")
    dokumen = datasets.values.tolist()
    index = pd.read_csv("data/index.csv")
    index = index.values.tolist()
    stemmer = PorterStemmer()
    result = [[] for i in range(len(dokumen))]      
    que = stemmer.stem(que)
    que = que.split()
    que = [x for x in que if x not in kataDepan]
    index = [x for x in index if x[0] in que]
    return index
	
#query = "somebody help not"
@app.route('/')
def main():
	return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
	if request.method =='POST':
		query = request.form['keyword']
		que = process(query)

		tf = que

		idf_vocab=[]
		for i in indx:
			k=0
			for tempBaris in stemmedDoc:
				if i in tempBaris:
					k+=1 
			idf_vocab.append(math.log10(len(dokumen)/k))
		

		WTD=[]

		#Define term
		for i in range(len(indx)): 
		
			list_term=[]
			for j in range(len(stemmedDoc)): 
				dictionary={}
				countKata=stemmedDoc[j].count(indx[i])
				if countKata==0:
					score=0
					dictionary[j+1]=score
				else:
					scoreVocab=(1+math.log10(countKata))*idf_vocab[i]
					dictionary[j+1]=scoreVocab
				list_term.append(dictionary)
			WTD.append(list_term)
		

		res = {}
		for doc in range (len(stemmedDoc)):
#     print("DOC:::::::" ,doc)
			sums = 0
			for qu in range (len(tf)):
	#         print(tf[qu][0])
				if(tf[qu][0] in stemmedDoc[doc]):
					ix = indx.index(tf[qu][0])
	#           print("doc-",doc,"-index-",ix)
					val = WTD[ix][doc][doc+1]
	#           print(val,"--",tf[qu][0])
					sums = sums + val
	#     print("Total:",sums)
			res[doc]=sums	
		# print(res)
		result = sorted(res.items(), key = 
				 lambda kv:(kv[1], kv[0]), reverse=True)
	#result
		data = []
		# score = []  
		for i in range (len(result)):
			if(result[i][1]):
				x = result[i][0]
				test = (dokumen[x],result[i][1])
				# data.append(dokumen[x])
				# data.append(result[i][1])
				data.append(test)
		print(data)
		return render_template('result.html',keyword="".join(query),data = data)	
		#for i in range (len(result)):
		#	if(result[i][1]):
		#		x = result[i][0]
	    #	data.append(dokumen[x][0])
	    #return render_template('result.html', keyword=" ".join(query), data=data)
	        #print("Dokumen:",x)
	       # print("SCORE:",res.values())
	        #print("Judul:",dokumen[x][0])
	        #print("Lirik:",dokumen[x][2])
	        #print("===========================================")

# run app
if __name__ == "__main__":
    app.run(debug=True)