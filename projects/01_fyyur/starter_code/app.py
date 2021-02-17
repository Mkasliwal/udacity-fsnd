#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
import sys
from datetime import datetime
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  normalisedData = Venue.query.with_entities(Venue.id, Venue.name, Venue.city, Venue.state).all()
  transformedData = []
  for i in normalisedData:
    dataVenue = []
    dataVenue.append({
      "id": i.id,
      "name": i.name,
    })
    transformedData.append({
      "city": i.city,
      "state": i.state,
      "venues": dataVenue
    })
  print(transformedData)
  return render_template('pages/venues.html', areas=transformedData)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', "")
  result = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  transFormedData = []
  for i in result:
    transFormedData.append({
      "id": i.id,
      "name": i.name,
      "upcoming_shows": 2
    })
  response = {
    "count": len(result),
    "data": transFormedData
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  past_shows = []
  upcoming_shows = []

  venueData = Venue.query.get(venue_id)
  print(venueData)
  pastShowsData = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time>datetime.now()).all()
  upcomingShowsData = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time<datetime.now()).all()
  
  for i in pastShowsData:
    past_shows.append({
      "artist_id": i.artist_id,
      "artist_name": i.artistShow.name,
      "artist_image_link": i.artistShow.image_link,
      "start_time": i.start_time.strftime(f'%Y-%m-%d, %H:%M:%S')
    })
  for i in upcomingShowsData:
    upcoming_shows.append({
      "artist_id": i.artist_id,
      "artist_name": i.artistShow.name,
      "artist_image_link": i.artistShow.image_link,
      "start_time": i.start_time.strftime(f'%Y-%m-%d, %H:%M:%S')
    })

  transformedData={
    "id": venueData.id,
    "name": venueData.name,
    "genres": venueData.genres,
    "address": venueData.address,
    "city": venueData.city,
    "state": venueData.state,
    "phone": venueData.phone,
    "website": venueData.website,
    "facebook_link": venueData.facebook_link,
    "seeking_talent": venueData.seeking_talent,
    "seeking_description": venueData.seeking_description,
    "image_link": venueData.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_venue.html', venue=transformedData)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  venueFormData = VenueForm(request.form)
  err=False
  try:
    venueData = Venue(
      name = venueFormData.name.data,
      city = venueFormData.city.data,
      state = venueFormData.state.data,
      address = venueFormData.address.data,
      phone = venueFormData.phone.data,
      image_link = venueFormData.image_link.data,
      facebook_link = venueFormData.facebook_link.data,
      genres = venueFormData.genres.data,
      seeking_talent = venueFormData.seeking_talent.data,
      seeking_description = venueFormData.seeking_description.data,
      website = venueFormData.website.data)
    db.session.add(venueData)
    db.session.commit()
  except:
    err=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not err:
    flash(f'Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    flash(f'Something Went Wrong. Venue ' + request.form['name'] + ' could not be listed')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venueData = Venue.query.get(venue_id)
  err = False
  try:
    db.session.delete(venueData)
    db.session.commit()
  except:
    err = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not err:
    flash(venueData.name+' has been Successfully DELETED :)')
  else:
    flash('Something Went Wrong in Deleting the Venue :/')
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  normalisedData = Artist.query.with_entities(Artist.id, Artist.name).all()
  transformedArtistData = []
  for i in normalisedData:
    dataArtist = []
    transformedArtistData.append({
      "id": i.id,
      "name": i.name,
    })
  print(transformedArtistData)
  return render_template('pages/artists.html', artists=transformedArtistData)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search', "")
  result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  transformedData = []
  for i in result:
    transformedData.append({
      "id": i.id,
      "name": i.name,
      "upcoming_shows": 2
    })
  response = {
    "count": len(result),
    "data": transformedData
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  past_shows = []
  upcoming_shows = []

  artistData = Artist.query.get(artist_id)
  print(artistData)
  pastShowsData = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time>datetime.now()).all()
  upcomingShowsData = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time<datetime.now()).all()

  for i in pastShowsData:
    past_shows.append({
      "venue_id": i.venue_id,
      "venue_name": i.venueShow.name,
      "venue_image_link": i.venueShow.image_link,
      "start_time": i.start_time.strftime(f'%Y-%m-%d, %H:%M:%S')
    })
  for i in upcomingShowsData:
    upcoming_shows.append({
      "venue_id": i.venue_id,
      "venue_name": i.venueShow.name,
      "venue_image_link": i.venueShow.image_link,
      "start_time": i.start_time.strftime(f'%Y-%m-%d, %H:%M:%S')
    })
  
  transformedData={
    "id": artistData.id,
    "name": artistData.name,
    "genres": artistData.genres,
    "city": artistData.city,
    "state": artistData.state,
    "phone": artistData.phone,
    "website": artistData.website,
    "facebook_link": artistData.facebook_link,
    "seeking_venue": artistData.seeking_venue,
    "seeking_description": artistData.seeking_description,
    "image_link": artistData.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=transformedData)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artistData = Artist.query.get(artist_id)
  try:
    form.name.data = artistData.name
    form.genres.data = artistData.genres
    form.city.data = artistData.city
    form.state.data = artistData.state
    form.phone.data = artistData.phone
    form.website.data = artistData.website
    form.facebook_link.data = artistData.facebook_link
    form.seeking_venue.data = artistData.seeking_venue
    form.seeking_description.data = artistData.seeking_description
    form.image_link.data = artistData.image_link
  except:
    abort(404)
  finally:
    return render_template('forms/edit_artist.html', form=form, artist=artistData)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  normalisedData=Artist.query.get(artist_id)
  artistFormData=ArtistForm(request.form)
  print(artistFormData)
  err=False
  try:
    normalisedData.name = artistFormData.name.data
    normalisedData.city = artistFormData.city.data
    normalisedData.state = artistFormData.state.data
    normalisedData.phone = artistFormData.phone.data
    normalisedData.image_link = artistFormData.image_link.data
    normalisedData.facebook_link = artistFormData.facebook_link.data
    normalisedData.genres = artistFormData.genres.data
    normalisedData.seeking_venue = artistFormData.seeking_venue.data
    normalisedData.seeking_description = artistFormData.seeking_description.data
    normalisedData.website = artistFormData.website.data
    db.session.commit()
  except:
    err=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not err:
    print(artistFormData)
    flash(f'Data Updated Successfully')
  else:
    flash(f'Something Went Wrong while Updating Data')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venueData = Venue.query.get(venue_id)
  try:
    form.name.data = venueData.name
    form.genres.data = venueData.genres
    form.address.data = venueData.address
    form.city.data = venueData.city
    form.state.data = venueData.state
    form.phone.data = venueData.phone
    form.website.data = venueData.website
    form.facebook_link.data = venueData.facebook_link
    form.seeking_talent.data = venueData.seeking_talent
    form.seeking_description.data = venueData.seeking_description
    form.image_link.data = venueData.image_link
  except:
    abort(404)
  finally:
    return render_template('forms/edit_venue.html', form=form, venue=venueData)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  normalisedData = Venue.query.get(venue_id)
  venueFormData = VenueForm(request.form)
  err=False
  try:
    normalisedData.name = venueFormData.name.data
    normalisedData.genres = venueFormData.genres.data
    normalisedData.address = venueFormData.address.data
    normalisedData.city = venueFormData.city.data
    normalisedData.state = venueFormData.state.data
    normalisedData.phone = venueFormData.phone.data
    normalisedData.image_link = venueFormData.image_link.data
    normalisedData.facebook_link = venueFormData.facebook_link.data
    normalisedData.seeking_talent = venueFormData.seeking_talent.data
    normalisedData.seeking_description = venueFormData.seeking_description.data
    normalisedData.website = venueFormData.website.data
    db.session.commit()
  except:
    err=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not err:
    print(venueFormData)
    flash(f'Data Updated Successfully')
  else:
    flash(f'Something Went Wrong while Updating Data')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  artistFormData = ArtistForm(request.form)
  err=False
  try:
    artistData = Artist(
      name = artistFormData.name.data,
      city = artistFormData.city.data,
      state = artistFormData.state.data,
      phone = artistFormData.phone.data,
      image_link = artistFormData.image_link.data,
      facebook_link = artistFormData.facebook_link.data,
      genres = artistFormData.genres.data,
      seeking_venue = artistFormData.seeking_venue.data,
      seeking_description = artistFormData.seeking_description.data,
      website = artistFormData.website.data)
    db.session.add(artistData)
    db.session.commit()
  except:
    err=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not err:
    flash(f'Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    flash(f'Something Went Wrong. Artist ' + request.form['name'] + ' could not be listed')
  return render_template('pages/home.html')
  
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  normalisedShows = db.session.query(Show).join(Artist).join(Venue).all()
  transformedShowData = []
  for i in normalisedShows:
    transformedShowData.append({
      "venue_id": i.venue_id,
      "venue_name": i.venueShow.name,
      "artist_id": i.artist_id,
      "artist_name": i.artistShow.name,
      "artist_image_link": i.artistShow.image_link,
      "start_time": i.start_time.strftime(f'%Y-%m-%d, %H:%M:%S')
    })
  print(transformedShowData)
  return render_template('pages/shows.html', shows=transformedShowData)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  showFormData = ShowForm(request.form)
  err=False
  try:
    showData=Show(
      artist_id = showFormData.artist_id.data,
      venue_id = showFormData.venue_id.data,
      start_time = showFormData.start_time.data
    )
    db.session.add(showData)
    db.session.commit()
  except:
    err=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not err:
    flash(f'Show was successfully listed :)')
  else:
    flash(f'Something Went Wrong :/')
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
