import flask
import csv
from flask import Flask, render_template, request
import difflib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

app = flask.Flask(__name__, template_folder='templates')
#tmdv dataset from kaggle, 5000 movies
df2 = pd.read_csv('tmdb.csv')
#converting sentences to vector format
count = CountVectorizer(stop_words='english')
#soup column stores keywords of movie
count_matrix = count.fit_transform(df2['soup'])

cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

df2 = df2.reset_index()
indices = pd.Series(df2.index, index=df2['title'])
#movie titles stored as list 
all_titles = [df2['title'][i] for i in range(len(df2['title']))]

def get_recommendations(title):
    #calculating similarity values for all movie titles
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    #fetching index of user entered movie
    idx = indices[title]
    #calculating similarity score each movie respect to user entered movie
    sim_scores = list(enumerate(cosine_sim[idx]))
    #More the similarity score, more accurate to recommend
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    #Fetching top 10 results
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    tit = df2['title'].iloc[movie_indices]
    dat = df2['release_date'].iloc[movie_indices]
    rating = df2['vote_average'].iloc[movie_indices]
    moviedetails=df2['overview'].iloc[movie_indices]
    movietypes=df2['keywords'].iloc[movie_indices]
    movieid=df2['id'].iloc[movie_indices]

    #Storing top 10 movies details in return_df document
    return_df = pd.DataFrame(columns=['Title','Year'])
    return_df['Title'] = tit
    return_df['Year'] = dat
    return_df['Ratings'] = rating
    return_df['Overview']=moviedetails
    return_df['Types']=movietypes
    #movie id --> connects dataset and api
    return_df['ID']=movieid
    return return_df

def get_suggestions():
    data = pd.read_csv('tmdb.csv')
    return list(data['title'].str.capitalize())

app = Flask(__name__)
@app.route("/")
@app.route("/index")
def index():
    NewMovies=[]
    with open('movieR.csv','r') as csvfile:
        readCSV = csv.reader(csvfile)
        NewMovies.append(random.choice(list(readCSV)))
        #random movie is selected from past history
    m_name = NewMovies[0][0]
    m_name = m_name.title()
    
    with open('movieR.csv', 'a',newline='') as csv_file:
        fieldnames = ['Movie']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writerow({'Movie': m_name})
        #recommendation for movie selected to display in "movies you may like section"
        result_final = get_recommendations(m_name)
        names = []
        dates = []
        ratings = []
        overview=[]
        types=[]
        mid=[]
        #Maintaining seperate coloumns of recommended movie details
        for i in range(len(result_final)):
            names.append(result_final.iloc[i][0])
            dates.append(result_final.iloc[i][1])
            ratings.append(result_final.iloc[i][2])
            overview.append(result_final.iloc[i][3])
            types.append(result_final.iloc[i][4])
            mid.append(result_final.iloc[i][5])
    suggestions = get_suggestions()
    
    return render_template('index.html',suggestions=suggestions,movie_type=types[5:],movieid=mid,movie_overview=overview,movie_names=names,movie_date=dates,movie_ratings=ratings,search_name=m_name)

# Set up the main route
@app.route('/positive', methods=['GET', 'POST'])

def main():
    #Redirecting to home page
    if flask.request.method == 'GET':
        return(flask.render_template('index.html'))

    #Redirected from home page after entered movie name
    if flask.request.method == 'POST':
        m_name = flask.request.form['movie_name']
        m_name = m_name.title()
        #If invalid movie name appears, alert message provided
        if m_name not in all_titles:
            return(flask.render_template('negative.html',name=m_name))
        else:
            with open('movieR.csv', 'a',newline='') as csv_file:
                fieldnames = ['Movie']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writerow({'Movie': m_name})
                #Movie reccomendation for user entered movie
            result_final = get_recommendations(m_name)
            names = []
            dates = []
            ratings = []
            overview=[]
            types=[]
            mid=[]
            for i in range(len(result_final)):
                names.append(result_final.iloc[i][0])
                dates.append(result_final.iloc[i][1])
                ratings.append(result_final.iloc[i][2])
                overview.append(result_final.iloc[i][3])
                types.append(result_final.iloc[i][4])
                mid.append(result_final.iloc[i][5])
               
            #Recomendation displayed on new page "positive.html"
            return flask.render_template('positive.html',movie_type=types[5:],movieid=mid,movie_overview=overview,movie_names=names,movie_date=dates,movie_ratings=ratings,search_name=m_name)

if __name__ == '__main__':
    app.run()
