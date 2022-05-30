#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
# from pandas import show_versions
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from config import *
from flask_migrate import Migrate
from operator import itemgetter
import datetime
import re
import sys
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#



# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()

  data = []
  areas = []

  for venue in venues:
        areas.append((venue.state, venue.city))

  areas.sort(key=itemgetter(0,1))

  now = datetime.datetime.now()

  for area in areas:

    venues_list = []

    for venue in venues:
          
        if ((venue.city == area[1]) & (venue.state == area[0])):
              shows = Show.query.filter_by(venue_id=venue.id).all()

              num_upcoming_shows = 0

              for show in shows:
                    if show.date_time > now:
                          num_upcoming_shows += 1

              venues_list.append({
                'id': venue.id,
                'name': venue.name,
                "num_upcoming_shows": num_upcoming_shows
              })

    data.append({
      "city": area[1],
      "state": area[0],
      "venues": venues_list 
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search = request.form.get("search_term","")

  data = []

  venues = Venue.query.filter(Venue.name.ilike(f"%{search}%")).all()

  for venue in venues:
        shows = Show.query.filter_by(venue_id=venue.id).all()
        upcoming = 0

        for show in shows:
              if show.date_time > datetime.datetime.now():
                    upcoming += 1
        data.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": upcoming
        })
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data = []
  venue = Venue.query.get(venue_id)
  upcoming = []
  past = []
  
  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.date_time > datetime.datetime.now())
  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.date_time < datetime.datetime.now())

  for show in upcoming_shows_query:
        upcoming.append({
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": str(show.date_time)
        })

  for show in past_shows_query:
        past.append({
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": str(show.date_time)
        })

  

  data = {
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.talent,
    "seeking_description": venue.seeking_description,
    "image_link":venue.image_link,
    "past_shows": past,
    "upcoming_shows": upcoming,
    "past_shows_count": len(past),
    "upcoming_shows_count": len(upcoming),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # venue = VenueForm()
  try:
    name = request.form['name'].strip()
    city = request.form['city'].strip()
    state = request.form['state'].strip()
    address = request.form['address'].strip()
    
    phone = request.form['phone'].strip()
    phone = re.sub("\D", "", phone)

    image_link = request.form['image_link'].strip()
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link'].strip()
    website_link = request.form['website_link'].strip()
    seeking_talent = True if 'seeking_talent' in request.form else False
    seeking_description = request.form['seeking_description'].strip()

    # TODO: modify data to be the data object returned from db insertion
    venue = Venue(name=name, city=city, 
                  state=state, address=address,
                  phone=phone, image_link=image_link,
                  genres=genres, facebook_link=facebook_link,
                  website_link=website_link, talent=seeking_talent,
                  seeking_description=seeking_description)
    
    
    db.session.add(venue)
    db.session.commit()
  
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(f"Venue {name} could not be listed!!!", "error")
  finally:
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
      error = False
      try:

          # TODO: Complete this endpoint for taking a venue_id, and using
          venue = Venue.query.get(venue_id)

          db.session.delete(venue)
          db.session.commit()
      except:
        error = True
        print(sys.info_exec)
        db.session.rollback()
      finally:
        db.session.close()

      if error:
            flash("An error occured, deletion could not be completed", "error")
      if not error:
            flash("Deletion Sucessful")

  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
      return redirect(url_for('show_venue'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()

  data = []

  for artist in artists:
        data.append({
          "id": artist.id,
          "name": artist.name
        })
      
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search = request.form.get("search_term", "")

  data = []

  artists = Artist.query.filter(Artist.name.ilike(f"%{search}%")).all()
  
  for artist in artists:
        shows = Show.query.filter_by(artist_id=artist.id)
        upcoming = 0

        for show in shows:
              if (show.date_time > datetime.datetime.now()):
                    upcoming += 1

        data.append({
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": upcoming
        })
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = []
  upcoming = []
  past = []
  artist = Artist.query.get(artist_id)

  # genres = [genre for genre in artist.genres]

  upcoming_query = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.date_time > datetime.datetime.now())
  past_query = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.date_time < datetime.datetime.now())

  for show in upcoming_query:
        upcoming.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.date_time)
        })

  for show in past_query:
      past.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": str(show.date_time)
      })

  data = {
    "id": artist_id,
    "name": artist.name,
    "genres": list(artist.genres),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.looking_venues,
    "seeking_description": artist.seeking_desc,
    "image_link": artist.image_link,
    "past_shows": past,
    "upcoming_shows": upcoming,
    "past_shows_count": len(past),
    "upcoming_shows_count": len(upcoming)
  }   

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  if  artist:
        form.data.name = artist.name
        form.data.address = artist.address
        form.data.genres = artist.genres
        form.data.city = artist.city
        form.data.state = artist.state
        form.data.phone = artist.phone
        form.data.website = artist.website_link
        form.data.facebook_link = artist.facebook_link
        form.data.seeking_venue = artist.looking_venues
        form.data.seeking_description = artist.seeking_desc
        form.data.image_link = artist.image_link
 
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)

  try:
    artist.name = request.form["name"]
    artist.city = request.form["city"]
    artist.state = request.form["state"]
    artist.phone = request.form["phone"]
    artist.phone = re.sub('\D', "", artist.phone)
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.website_link = request.form['website_link']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_desc = request.form['seeking_description']
    artist.looking_venues = True if "seeking_venue" in request.form else False

    db.session.commit()
    flash(f"{artist.name}'s profile updated successfully!!!")
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(f"{artist.name} profile could not be updated.", "error")
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  
  if  venue:
        form.data.name = venue.name
        form.data.genres = venue.genres
        form.data.address = venue.address
        form.data.city = venue.city
        form.data.state = venue.state
        form.data.phone = venue.phone
        form.data.website = venue.website_link
        form.data.facebook_link = venue.facebook_link
        form.data.seeking_venue = venue.looking_venues
        form.data.seeking_description = venue.seeking_desc
        form.data.image_link = venue.image_link

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.get.query(venue_id)
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.phone = re.sub("\D", "", phone)
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    venue.seeking_talent = True if "seeking_talent" in request.form else False
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()
    flash(f"Venue {venue.name} updated successfully!!!!")
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(f"Venue {venue.name} could not be updated!!!")
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    name = request.form["name"].strip()
    city = request.form["city"].strip()
    state = request.form["state"].strip()
    phone = request.form["phone"].strip()
    phone = re.sub("\D", "", phone)
    genres = request.form.getlist("genres")
    image_link = request.form["image_link"].strip()
    facebook_link = request.form["facebook_link"].strip()
    looking_venues = True if "seeking_venues" in request.form else False
    seeking_desc = request.form["seeking_description"].strip()

    artist = Artist(
      name=name, city=city, state=state,
      phone=phone, genres=genres, image_link=image_link,
      facebook_link=facebook_link, looking_venues=looking_venues,
      seeking_desc=seeking_desc
    )

    db.session.add(artist)
    db.session.commit()

    flash(f'Artist {name} was successfully listed!')

  except:
    print(sys.exc_info())
    db.session.rollback()
    flash(f'Artist {name} could not be listed!', "error")
  finally:
    db.session.close()

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []

  shows = Show.query.all()

  for show in shows:
        data.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": str(show.date_time)
        })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    venue_id = request.form['venue_id']
    artist_id = request.form["artist_id"]
    date_time = request.form['start_time']

    show = Show(
      venue_id = venue_id,
      artist_id = artist_id,
      date_time = date_time 
    )

    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    print(sys.exc_info())
    db.session.rollback()
    flash('Show could  not be listed!', "error")

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
