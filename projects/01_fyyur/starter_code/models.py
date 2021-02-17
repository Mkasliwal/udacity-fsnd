from flask_sqlalchemy import SQLAlchemy

# DB Object from SQLAlchemy
db = SQLAlchemy()

# DB Models 
class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True, default="https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80")
    facebook_link = db.Column(db.String(120), nullable=True, default="")
    genres = db.Column(db.String(200))
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(150), nullable=True)
    website = db.Column(db.String(120), nullable=True)

    venue_reg_shows = db.relationship('Show', backref='venueShow')

    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=True, default="https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80")
    facebook_link = db.Column(db.String(120), nullable=True, default="")
    genres = db.Column(db.String(200))
    seeking_description = db.Column(db.String(150), nullable=True, default="")
    seeking_venue = db.Column(db.String(120), nullable=True, default=False)
    website = db.Column(db.String(120), nullable=True, default="")

    artist_reg_shows = db.relationship('Show', backref='artistShow')
    
    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

  def __repr__(self):
    return f'<shows {self.id}>'
