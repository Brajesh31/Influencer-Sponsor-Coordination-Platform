from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Sponsor(db.Model):
    __tablename__ = 'sponsor'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)         # if it is a company then the first_name denotes the name of the company
    last_name = db.Column(db.String)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    industry = db.Column(db.String, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    type = db.Column(db.Enum('company', 'individual'), nullable=False)
    flagged = db.Column(db.Boolean, default=False)
    campaign = db.relationship('Campaign', backref='sponsor', cascade='all, delete-orphan')

class Influencer(db.Model):
    __tablename__ = 'influencer'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    age = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    earning = db.Column(db.Integer, default=0)
    flagged = db.Column(db.Boolean, default=False)
    reach = db.relationship('Reach', backref='influencer', cascade='all, delete-orphan')
    ad_request = db.relationship('Ad_Request', backref='influencer')
    influencer_niche = db.relationship('Influencer_Niche', backref='influencer')

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

class Reach(db.Model):
    __tablename__ = 'reach'
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    platform = db.Column(db.Enum('instagram', 'twitter', 'youtube', 'linkedin'), nullable=False)
    followers = db.Column(db.Integer, nullable=False)
    profile_link = db.Column(db.String, nullable=False)

class Niche(db.Model):
    __tablename__ = 'niche'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    influencer_niche = db.relationship('Influencer_Niche', backref='niche')
    ad_request = db.relationship('Ad_Request', backref='niche')

class Influencer_Niche(db.Model):
    __tablename__ = 'influencer_niche'
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), primary_key=True, nullable=False)
    niche_id = db.Column(db.Integer, db.ForeignKey('niche.id'), primary_key=True, nullable=False)

class Campaign(db.Model):
    __tablename__ = 'campaign'
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    visibility = db.Column(db.Enum('private', 'public'), default='public', nullable=False)
    # private campaigns are those campigns that an influencer can not see. Only the host sponsor can send req for ads of such campaigns
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    goal = db.Column(db.String)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    flagged = db.Column(db.Boolean, default=False)
    ad_request = db.relationship('Ad_Request', backref='campaign', cascade='all, delete-orphan')

class Ad_Request(db.Model):
    __tablename__ = 'ad_request'
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    status = db.Column(db.Enum('pending', 'accepted', 'completed', 'requested'))
    # when a sposnor gives an ad to influencer it will be 'pending' while if an influencer requests a sponsor for an 
    # ad then the status of that ad would be 'requested' othereise it is None 
    payment_amount = db.Column(db.Float, nullable=False)
    requirement = db.Column(db.String, nullable=False)
    niche_id = db.Column(db.Integer, db.ForeignKey('niche.id'), nullable=False)