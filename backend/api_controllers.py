from flask_restful import Api, Resource, reqparse
from .models import *
from datetime import datetime

api = Api()
parser = reqparse.RequestParser()

# we will define what fields the request body will have in case of a post request
parser.add_argument('title')
parser.add_argument('description')
parser.add_argument('goal')
parser.add_argument('start_date')
parser.add_argument('end_date')
parser.add_argument('visibility')
parser.add_argument('budget')

class CampaignAPI(Resource):
    def get(self, sponsor_id):
        # retrieving all the campaigns of a particular sponsor
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).all()
        all_campaigns_details = []
        for campaign in campaigns:
            campaign_details = {'id': campaign.id,
                                'sponsor_id': campaign.sponsor_id,
                                'visibility': campaign.visibility,
                                'title': campaign.title,
                                'description': campaign.description,
                                'goal': campaign.goal,
                                'start_date': campaign.start_date.strftime('%Y-%m-%d'),
                                'end_date': campaign.end_date.strftime('%Y-%m-%d'),
                                'budget': campaign.budget,
                                'flagged': campaign.flagged}
            all_campaigns_details.append(campaign_details)
        return all_campaigns_details
    
    def post(self, sponsor_id):
        # creating a new campaign for a given sponsor
        campaign_data = parser.parse_args()
        # Converting string dates to date objects
        start_date = datetime.strptime(campaign_data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(campaign_data['end_date'], '%Y-%m-%d').date()
        new_campaign = Campaign(title=campaign_data['title'],
                                description=campaign_data['description'],
                                goal=campaign_data['goal'],
                                start_date=start_date,
                                end_date=end_date,
                                visibility=campaign_data['visibility'],
                                budget=campaign_data['budget'],
                                sponsor_id=sponsor_id)
        db.session.add(new_campaign)
        db.session.commit()
        return 'campaign created successfully.', 201

    def put(self, camp_id):
        campaign_data = parser.parse_args()
        campaign = Campaign.query.get(camp_id)
        if campaign:
            campaign.title = campaign_data['title'] if campaign_data['title'] else campaign.title
            campaign.description = campaign_data['description'] if campaign_data['description'] else campaign.description
            campaign.goal = campaign_data['goal'] if campaign_data['goal'] else campaign.goal
            campaign.start_date = datetime.strptime(campaign_data['start_date'], '%Y-%m-%d').date() if campaign_data['start_date'] else campaign.start_date
            campaign.end_date = datetime.strptime(campaign_data['end_date'], '%Y-%m-%d').date() if campaign_data['end_date'] else campaign.end_date
            campaign.visibillity = campaign_data['visibility'] if campaign_data['visibility'] else campaign.visibility
            campaign.budget = campaign_data['budget'] if campaign_data['budget'] else campaign.budget

            db.session.commit()
            return 'Campaign edited.', 200
        else:
            return 'Campaign not found!', 400    

    def delete(self, camp_id):
        campaign = Campaign.query.get(camp_id)
        if campaign:
            db.session.delete(campaign)
            db.session.commit()
            return 'Campaign deleted.', 200
        else:
            return 'Campaign not found!', 400
        
class InfluencerAPI(Resource):
    def get(self, influencer_id):
        influencer = Influencer.query.get(influencer_id)
        if influencer:
            influencer_details = {
                'id': influencer.id,
                'first_name': influencer.first_name,
                'last_name': influencer.last_name,
                'age': influencer.age,
                'username': influencer.username,
                'password': influencer.password,
                'email': influencer.email,
                'earning': influencer.earning,
                'flagged': influencer.flagged
            }
            return influencer_details
        else:
            return 'Influencer not found!', 404
        
class SponsorAPI(Resource):
    def get(self, sponsor_id):
        sponsor = Sponsor.query.get(sponsor_id)
        if sponsor:
            sponsor_details = {
                'id': sponsor.id,
                'first_name': sponsor.first_name,
                'last_name': sponsor.last_name,
                'usernmae': sponsor.username,
                'password': sponsor.password,
                'industry': sponsor.industry,
                'budget': sponsor.budget,
                'email': sponsor.email,
                'type': sponsor.type,
                'flagged': sponsor.flagged
            }
            return sponsor_details
        else:
            return 'Sponsor not found!', 404

api.add_resource(CampaignAPI, '/api/campaign/<int:sponsor_id>',
                 '/api/campaign/update/<int:camp_id>', 
                 '/api/campaign/delete/<int:camp_id>')
api.add_resource(InfluencerAPI, '/api/influencer/<int:influencer_id>')
api.add_resource(SponsorAPI, '/api/sponsor/<int:sponsor_id>')