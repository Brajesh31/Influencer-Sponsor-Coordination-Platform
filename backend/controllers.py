from flask import Flask, render_template, request, redirect, url_for
from flask import current_app as app
from .models import *
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib.ticker import MaxNLocator
import numpy as np

# ---------------------------------------------------------- ROUTES ---------------------------------------------------------- #
@app.route('/')
def home():
    return render_template('welcome_page.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        # checking if credentials match a sponsor
        sponsor = Sponsor.query.filter_by(username=username, password=password).first()
        if sponsor:
            if not sponsor.flagged:
                return render_template('sponsor_dashboard.html', first_name=sponsor.first_name, last_name=sponsor.last_name, 
                                       sponsor_id=sponsor.id, requested_ad_requests=fetch_requested_ad_requests_for_sponsor(sponsor.id),
                                       active_campaigns=fetch_active_campaigns(sponsor.id), 
                                       pending_ad_requests=fetch_pending_ad_requests_of_sponsor(sponsor.id))
            else:
                return render_template('user_login.html', error='You have been flagged! Can\'t login.')
        
        # checking if credentials match a influencer
        influencer = Influencer.query.filter_by(username=username, password=password).first()
        if influencer:
            if not influencer.flagged:
                return render_template('influencer_dashboard.html', influencer_id=influencer.id, influencer_info=fetch_influencer_details(influencer.id),
                                       active_ads=fetch_active_ads(influencer.id), pending_ads=fetch_pending_ad_requests_for_influencer(influencer.id),
                                       requested_ads=fetch_requested_ad_requests_of_influencer(influencer.id), fname=influencer.first_name, lname=influencer.last_name)
            else:
                return render_template('user_login.html', error='You have been flagged! Can\'t login.')
        
        # credentials do not match, show error msg and redirect to login
        return render_template('user_login.html', error="Invalid credentials!")
    
    return render_template('user_login.html', error='')


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('admin_username')
        password = request.form.get('admin_password')

        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            return render_template('admin_dashboard.html', active_campaigns=fetch_active_campaigns(), flagged_campaigns=fetch_flagged_campaigns(), 
                                   flagged_influencers=fetch_flagged_influencers(), flagged_sponsors=fetch_flagged_sponsors())
        return render_template('admin_login.html',error='Invalid credentials!')
    
    return render_template('admin_login.html', error='')


@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    return render_template('admin_dashboard.html', active_campaigns=fetch_active_campaigns(), flagged_campaigns=fetch_flagged_campaigns(), 
                           flagged_influencers=fetch_flagged_influencers(), flagged_sponsors=fetch_flagged_sponsors())


@app.route('/flag_sponsor/<int:sponsor_id>', methods=['GET', 'POST'])
def flag_sponsor(sponsor_id):
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    sponsor.flagged = True
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/unflag_sponsor/<int:sponsor_id>', methods=['GET', 'POST'])
def unflag_sponsor(sponsor_id):
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    sponsor.flagged = False
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/flag_influencer/<int:influencer_id>', methods=['GET', 'POST'])
def flag_influencer(influencer_id):
    influencer = Influencer.query.filter_by(id=influencer_id).first()
    influencer.flagged = True
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/unflag_influencer/<int:influencer_id>', methods=['GET', 'POST'])
def unflag_influencer(influencer_id):
    influencer = Influencer.query.filter_by(id=influencer_id).first()
    influencer.flagged = False
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/flag_campaign/<int:campaign_id>', methods=['GET', 'POST'])
def flag_campaign(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    campaign.flagged = True
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/unflag_campaign/<int:campaign_id>', methods=['GET', 'POST'])
def unflag_campaign(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    campaign.flagged = False
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin_find', methods=['GET', 'POST'])
def admin_find():
    return render_template('admin_find.html', active_campaigns=fetch_active_campaigns(), completed_campaigns=fetch_completed_campaigns(), 
                           all_influencers=fetch_all_influencers(), all_sponsors=fetch_all_sponsors(), scheduled_campaigns=fetch_scheduled_campaigns())


@app.route('/admin_statistics')
def admin_statistics():
    campaigns = Campaign.query.all()
    ads = Ad_Request.query.all()
    sponsors = Sponsor.query.all()
    influencers = Influencer.query.all()

    status = [ad.status for ad in ads if ad.status is not None]
    visibility = [campaign.visibility for campaign in campaigns]
    public_campaigns = visibility.count('public')
    private_campaigns = visibility.count('private')

    flagged_campaigns = sum(1 for campaign in campaigns if campaign.flagged)
    unflagged_campaigns = len(campaigns) - flagged_campaigns
    flagged_sponsors = sum(1 for sponsor in sponsors if sponsor.flagged)
    unflagged_sponsors = len(sponsors) - flagged_sponsors
    flagged_influencers = sum(1 for influencer in influencers if influencer.flagged)
    unflagged_influencers = len(influencers) - flagged_influencers
    
    categories = ['Campaigns', 'Sponsors', 'Influencers']
    flagged = [flagged_campaigns, flagged_sponsors, flagged_influencers]
    unflagged = [unflagged_campaigns, unflagged_sponsors, unflagged_influencers]

    fig, ax = plt.subplots(figsize=(4, 4))
    plt.clf()
    bar_width = 0.25
    index = np.arange(len(categories))
    plt.bar(index, unflagged, bar_width, label='Unflagged', color='pink')
    plt.bar(index + bar_width, flagged, bar_width, label='Flagged', color='palevioletred')
    plt.xlabel('Categories')
    plt.ylabel('Count')
    plt.xticks(index + bar_width / 2, categories)
    plt.legend()
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.tight_layout()
    plt.savefig('static/statistics/admin/flagged_unflagged.png')

    # Query the count of ads for each niche
    niche_ad_counts = (db.session.query(Niche.name, db.func.count(Ad_Request.id))
                       .join(Ad_Request, Niche.id == Ad_Request.niche_id)
                       .group_by(Niche.name).all())
    niche_names = [n[0] for n in niche_ad_counts]
    ad_counts = [n[1] for n in niche_ad_counts]
    fig, ax = plt.subplots(figsize=(4, 4))
    plt.clf()
    plt.bar(niche_names, ad_counts, bar_width, color='palevioletred')
    plt.xlabel('Niche Names')
    plt.ylabel('Number of Ads')
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xticks(rotation=30, ha='right')  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout to make room for x-axis labels    
    plt.savefig('static/statistics/admin/ad_niche.png')
    
    fig, ax = plt.subplots(figsize=(4, 4))
    plt.clf()
    plt.hist(status, 10, color='palevioletred')
    plt.xlabel('Ad Status')
    plt.ylabel('Number of Ads')
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.savefig('static/statistics/admin/ad_status.png')

    fig, ax = plt.subplots(figsize=(4, 4))
    plt.clf()
    plt.pie([public_campaigns, private_campaigns], explode=(0.1, 0), labels=['Public', 'Private'], colors=['pink', 'palevioletred'], autopct='%1.1f%%', shadow=True, startangle=140)
    plt.savefig('static/statistics/admin/campaign_visibility.png')

    # Query the number of campaigns for each sponsor
    sponsor_campaigns = (db.session.query(Sponsor.first_name, Sponsor.last_name, db.func.count(Campaign.id))
                         .join(Campaign, Sponsor.id == Campaign.sponsor_id)
                         .group_by(Sponsor.first_name, Sponsor.last_name).all())
    sponsor_names = [f"{sc[0]} {sc[1]}" for sc in sponsor_campaigns]
    campaign_counts = [sc[2] for sc in sponsor_campaigns]
    fig, ax = plt.subplots(figsize=(4, 4))
    plt.clf()
    plt.bar(sponsor_names, campaign_counts, bar_width, color='palevioletred')
    plt.xlabel('Sponsors')
    plt.ylabel('Number of Campaigns')
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xticks(rotation=30, ha='right')   # Rotating x-axis labels for better readability
    plt.tight_layout()  # to make room for x-axis labels
    plt.savefig('static/statistics/admin/sponsor_campaigns.png')

    # Query the total number of influencers and sponsors
    total_influencers = db.session.query(Influencer).count()
    total_sponsors = db.session.query(Sponsor).count()
    fig, ax = plt.subplots(figsize=(4, 4))
    plt.clf()
    plt.pie([total_influencers, total_sponsors], labels=['Influencers', 'Sponsors'],explode=(0.1, 0), autopct='%1.1f%%', colors=['pink', 'palevioletred'], shadow=True, startangle=140)
    plt.savefig('static/statistics/admin/influencers_sponsors_count.png')
    
    return render_template('admin_statistics.html')


@app.route('/campaign_details/<int:camp_id>', methods=['GET', 'POST'])
def particular_campaign_details_for_admin(camp_id):
    return render_template('admin_campaign_details.html', campaign_info=fetch_campaign_details(camp_id))


@app.route('/influencer_signup', methods=['GET', 'POST'])
def influencer_signup():
    if request.method == 'POST':
        # collecting inputs from form
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        age = request.form.get('age')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        # checking if an influencer with the same username already exists; if not, adding the influencer in the database
        influencer = Influencer.query.filter_by(username=username).first()
        if influencer:
            return render_template('influencer_registration.html', error='An influencer with this username already exists!')
        
        influencer = Influencer(first_name=first_name, last_name=last_name, age=age, email=email, username=username, password=password)
        db.session.add(influencer)
        db.session.commit()
        
        # retieving the reach information (social media accounts)
        influencer_id = influencer.id            # getting the ID of the newly added influencer
        social_accounts = request.form.getlist('social_accounts')
        for platform in social_accounts:
            followers = request.form.get(f'{platform}Followers')
            profile_link = request.form.get(f'{platform}Profile')
            reach = Reach(influencer_id=influencer_id, platform=platform, followers=followers, profile_link=profile_link)
            db.session.add(reach)
            db.session.commit()

        # collecting niche information
        niches = request.form.getlist('niches')
        for niche_name in niches:
            niche = Niche.query.filter_by(name=niche_name).first()
            if not niche:
                niche = Niche(name=niche_name)
                db.session.add(niche)
                db.session.commit()
                
            influencer_niche = Influencer_Niche(influencer_id=influencer_id, niche_id=niche.id)
            db.session.add(influencer_niche)
            db.session.commit()
        
        return render_template('user_login.html', error='')

    return render_template('influencer_registration.html', error='')


@app.route('/influencer_dashboard/<int:influencer_id>', methods=['GET', 'POST'])
def influencer_dashboard(influencer_id):
    influencer = Influencer.query.filter_by(id=influencer_id).first()
    return render_template('influencer_dashboard.html', influencer_id=influencer_id, influencer_info=fetch_influencer_details(influencer_id),
                        active_ads=fetch_active_ads(influencer_id), pending_ads=fetch_pending_ad_requests_for_influencer(influencer_id),
                        fname=influencer.first_name, lname=influencer.last_name, requested_ads=fetch_requested_ad_requests_of_influencer(influencer_id))


# when a sponsor assigns an ad to an influencer, he has already added the influencer's id in the ad's influencer_id attribute and set status from None to pending
# if the influencer accepts the request then he will just change the status of the ad from pending to accepted.
@app.route('/influencer_dashboard/accept_ad_request/<int:influencer_id>/<int:ad_id>', methods=['GET', 'POST'])
def influencer_accept_ad_request(influencer_id, ad_id):
    ad_request = Ad_Request.query.filter_by(id=ad_id).first()
    ad_request.status = 'accepted'
    db.session.commit()

    influencer = Influencer.query.filter_by(id=influencer_id).first()
    return render_template('influencer_dashboard.html', influencer_id=influencer_id, influencer_info=fetch_influencer_details(influencer_id),
                        active_ads=fetch_active_ads(influencer_id), pending_ads=fetch_pending_ad_requests_for_influencer(influencer_id),
                        fname=influencer.first_name, lname=influencer.last_name, requested_ads=fetch_requested_ad_requests_of_influencer(influencer_id))



# if the influencer rejects the ad, he will first change the status of the ad from pending to None and remove his id from the influencer_id attribute of the ad
@app.route('/influencer_dashboard/reject_ad_request/<int:influencer_id>/<int:ad_id>', methods=['GET', 'POST'])
def influencer_reject_ad_request(influencer_id, ad_id):
    ad_request = Ad_Request.query.filter_by(id=ad_id).first()
    ad_request.status = None
    ad_request.influencer_id = None
    db.session.commit()

    influencer = Influencer.query.filter_by(id=influencer_id).first()
    return render_template('influencer_dashboard.html', influencer_id=influencer_id, influencer_info=fetch_influencer_details(influencer_id),
                        active_ads=fetch_active_ads(influencer_id), pending_ads=fetch_pending_ad_requests_for_influencer(influencer_id),
                        fname=influencer.first_name, lname=influencer.last_name, requested_ads=fetch_requested_ad_requests_of_influencer(influencer_id))



@app.route('/influencer_find/<int:influencer_id>', methods=['GET', 'POST'])
def influencer_find(influencer_id):
    influencer = Influencer.query.filter_by(id=influencer_id).first()
    niches = Niche.query.all()
    filtered_niche_id = request.args.get('niche_id')
    if not filtered_niche_id:
        # no filter has been selcted so show all the public campaigns and all the ads from public, unflagged campaigns
        return render_template('influencer_find.html', fname=influencer.first_name, lname=influencer.last_name, influencer_id=influencer_id, 
                           all_public_campaigns=fetch_all_public_campaigns(), all_ads=fetch_all_ads(), niches=niches)
    else:
        # if a niche is selected to be used a filter
        return render_template('influencer_find.html', fname=influencer.first_name, lname=influencer.last_name, influencer_id=influencer_id, 
                               all_ads=fetch_all_ads(filtered_niche_id), niches=niches)


@app.route('/influencer_statistics/<int:influencer_id>')
def influencer_statistics(influencer_id):
    influencer = Influencer.query.filter_by(id=influencer_id).first()
    
    # Fetch data
    monthly_earnings = (db.session.query(
                        db.func.strftime("%Y-%m", Campaign.end_date).label("month"),
                        db.func.sum(Ad_Request.payment_amount).label("total_earnings"))
                        .join(Campaign, Ad_Request.campaign_id == Campaign.id)
                        .filter(Ad_Request.influencer_id == influencer_id, Ad_Request.status == 'completed')
                        .group_by("month")
                        .order_by("month").all())
    
    fig, ax = plt.subplots(figsize=(4, 4))
    if monthly_earnings:
        months, earnings = zip(*monthly_earnings)
        plt.clf()
        plt.plot(months, earnings, marker='o', linestyle='--', color='palevioletred')
    plt.xlabel('Month')
    plt.ylabel('Earnings')
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.savefig('static/statistics/influencer/monthly_earnings.png')
    
    # Ad status distribution
    completed_ads = Ad_Request.query.filter(Ad_Request.influencer_id == influencer_id, Ad_Request.status == 'completed').count()
    active_ads = Ad_Request.query.filter(Ad_Request.influencer_id == influencer_id, Ad_Request.status == 'accepted').count()
    ad_categories = ['Completed', 'Active']
    ad_values = [completed_ads, active_ads]
    fig, ax = plt.subplots(figsize=(4, 4))
    plt.clf()
    plt.pie(ad_values, labels=ad_categories, colors=['pink', 'palevioletred'], autopct='%1.1f%%', startangle=140, explode=(0.05, 0), shadow=True)
    plt.savefig('static/statistics/influencer/ad_status.png')
    
    return render_template('influencer_statistics.html', fname=influencer.first_name, lname=influencer.last_name, influencer_id=influencer_id)

# when an influencer requests for an ad, she/he changes the status of that ad_request form none to requested and adds his own id in the 
# influencer_id attribute of the ad_request.
@app.route('/request_sponsor_for_ad/<int:influencer_id>/<int:ad_id>', methods=['GET', 'POST'])
def request_sponsor_for_ad(influencer_id, ad_id):
    ad_request = Ad_Request.query.filter_by(id=ad_id).first()
    ad_request.status = 'requested'
    ad_request.influencer_id = influencer_id
    db.session.commit()

    influencer = Influencer.query.filter_by(id=influencer_id).first()
    return render_template('influencer_find.html', fname=influencer.first_name, lname=influencer.last_name, influencer_id=influencer_id, 
                           all_public_campaigns=fetch_all_public_campaigns(), all_ads=fetch_all_ads())


@app.route('/campaign_details_for_influencer/<int:influencer_id>/<int:camp_id>', methods=['GET', 'POST'])
def particular_campaign_details_for_influencer(influencer_id, camp_id):
    influencer = Influencer.query.filter_by(id=influencer_id).first()
    return render_template('influencer_campaign_details.html', fname=influencer.first_name, lname=influencer.last_name, influencer_id=influencer_id,
                           campaign_info=fetch_campaign_details(camp_id))


@app.route('/sponsor_signup', methods=['GET', 'POST'])
def sponsor_signup():
    if request.method == 'POST':
        # collecting inputs form form
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        industry = request.form.get('industry')
        budget = request.form.get('budget')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        type = request.form.get('type')

        # checking if a sponsor with the same username already exists; if not, adding the sponsor in the database
        sponsor = Sponsor.query.filter_by(username=username).first()
        if sponsor:
            return render_template('sponsor_registration.html', error='A sponsor with this username already exists!')
        
        sponsor = Sponsor(first_name=first_name, last_name=last_name, email=email, username=username, password=password, industry=industry, budget=budget, type=type)
        db.session.add(sponsor)
        db.session.commit()
        return render_template('user_login.html', error='')
    
    return render_template('sponsor_registration.html')


@app.route('/sponsor_dashboard/<int:sponsor_id>', methods=['GET', 'POST'])
def sponsor_dashboard(sponsor_id):
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    return render_template('sponsor_dashboard.html', sponsor_id=sponsor_id, first_name=sponsor.first_name, last_name=sponsor.last_name,
                           active_campaigns=fetch_active_campaigns(sponsor_id), requested_ad_requests=fetch_requested_ad_requests_for_sponsor(sponsor_id),
                           pending_ad_requests=fetch_pending_ad_requests_of_sponsor(sponsor_id))


# when an influencer requested for an ad, he already added his id in the influencer_id attribute of that ad. 
# When the sponsor accepts the request, he just changes the status of the ad_request from 'requested' to 'accepted'
@app.route('/sponsor_dashboard/accept_ad_request/<int:sponsor_id>/<int:ad_id>', methods=['GET', 'POST'])
def sponsor_accept_ad_request(sponsor_id, ad_id):
    ad_request = Ad_Request.query.filter_by(id=ad_id).first()
    ad_request.status = 'accepted'
    db.session.commit()

    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    return render_template('sponsor_dashboard.html', sponsor_id=sponsor_id, first_name=sponsor.first_name, last_name=sponsor.last_name,
                           active_campaigns=fetch_active_campaigns(sponsor_id), requested_ad_requests=fetch_requested_ad_requests_for_sponsor(sponsor.id),
                           pending_ad_requests=fetch_pending_ad_requests_of_sponsor(sponsor_id))


# when an influencer requested for an ad, he already added his id in the influencer_id attribute of that ad. 
# When the sponsor rejects the request, he changes the status of the ad_request from 'requested' to None 
# and removes that influencer's id from the influencer_id attribute of the ad
@app.route('/sponsor_dashboard/reject_ad_request/<int:sponsor_id>/<int:ad_id>', methods=['GET', 'POST'])
def sponsor_reject_ad_request(sponsor_id, ad_id):
    ad_request = Ad_Request.query.filter_by(id=ad_id).first()
    ad_request.status = None
    ad_request.influencer_id = None
    db.session.commit()

    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    return render_template('sponsor_dashboard.html', sponsor_id=sponsor_id, first_name=sponsor.first_name, last_name=sponsor.last_name,
                           active_campaigns=fetch_active_campaigns(sponsor_id), requested_ad_requests=fetch_requested_ad_requests_for_sponsor(sponsor.id),
                           pending_ad_requests=fetch_pending_ad_requests_of_sponsor(sponsor_id))



@app.route('/sponsor_find/<int:sponsor_id>', methods=['GET', 'POST'])
def sponsor_find(sponsor_id):
    filtered_niche_id = request.args.get('niche_id')
    niches = Niche.query.all()
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    return render_template('sponsor_find.html', first_name=sponsor.first_name, last_name=sponsor.last_name, sponsor_id=sponsor_id, 
                           all_influencers=fetch_influencer_details_for_sponsor(filtered_niche_id), niches=niches)


@app.route('/sponsor_statistics/<int:sponsor_id>')
def sponsor_statistics(sponsor_id):
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    current_date = datetime.now().date()
    completed_campaigns = Campaign.query.filter(Campaign.sponsor_id == sponsor_id, Campaign.end_date < current_date).count()
    scheduled_campaigns = Campaign.query.filter(Campaign.sponsor_id == sponsor_id, Campaign.start_date > current_date).count()
    active_campaigns = Campaign.query.filter(Campaign.sponsor_id == sponsor_id, Campaign.start_date < current_date, Campaign.end_date > current_date).count()
    completed_ads = (db.session.query(Ad_Request)
                     .join(Campaign, Campaign.id == Ad_Request.campaign_id)
                     .filter(Campaign.sponsor_id == sponsor_id, Ad_Request.status == 'completed').count())
    scheduled_ads = (db.session.query(Ad_Request)
                     .join(Campaign, Campaign.id == Ad_Request.campaign_id)
                     .filter(Campaign.sponsor_id == sponsor_id, Campaign.start_date > current_date).count())
    active_ads = (db.session.query(Ad_Request)
                  .join(Campaign, Campaign.id == Ad_Request.campaign_id)
                  .filter(Campaign.sponsor_id == sponsor_id, Ad_Request.status == 'accepted').count())
    
    # Campaign status distribution
    fig, ax = plt.subplots(figsize=(4, 4))
    plt.clf()
    categories = ['Completed', 'Scheduled', 'Active']
    values = [completed_campaigns, scheduled_campaigns, active_campaigns]
    plt.pie(values, labels=categories, autopct='%1.1f%%', colors=['pink', 'mistyrose', 'palevioletred'], startangle=140, explode=(0, 0, 0.05), shadow=True)
    plt.savefig('static/statistics/sponsor/campaign_status.png')

    # Ad status distribution
    fig, ax = plt.subplots(figsize=(4, 4))
    plt.clf()
    ad_categories = ['Completed', 'Scheduled', 'Active']
    ad_values = [completed_ads, scheduled_ads, active_ads]
    plt.pie(ad_values, labels=ad_categories, autopct='%1.1f%%', colors=['pink', 'mistyrose', 'palevioletred'], startangle=140, explode=(0, 0, 0.05), shadow=True)
    plt.savefig('static/statistics/sponsor/ad_status.png')

    # Monthly expenditure
    monthly_expenditure = (db.session.query(
                            db.func.strftime("%Y-%m", Campaign.start_date).label("month"),
                            db.func.sum(Campaign.budget).label("total_budget"))
                           .filter(Campaign.sponsor_id == sponsor_id)
                           .group_by("month")
                           .order_by("month").all())
    months, expenditures = zip(*monthly_expenditure)
    fig, ax = plt.subplots(figsize=(4, 4))
    plt.clf()
    plt.plot(months, expenditures, marker='o', linestyle='--', color='palevioletred')
    plt.xlabel('Month')
    plt.ylabel('Expenditure')
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.savefig('static/statistics/sponsor/monthly_expenditure.png')

    return render_template('sponsor_statistics.html', sponsor_id=sponsor_id, first_name=sponsor.first_name, last_name=sponsor.last_name)
    

@app.route('/campaign_details/<int:sponsor_id>/<int:camp_id>', methods=['GET', 'POST'])
def particular_campaign_details_for_sponsor(sponsor_id, camp_id):
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    niches = Niche.query.all()
    return render_template('sponsor_campaign_details.html', sponsor_id=sponsor_id, campaign_info=fetch_campaign_details(camp_id),
                           first_name=sponsor.first_name, last_name=sponsor.last_name, niches=niches)


@app.route('/sponsor_all_campaigns/<int:sponsor_id>', methods=['GET', 'POST'])
def sponsor_all_campaigns(sponsor_id):
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    return render_template('sponsor_all_campaigns.html', active_campaigns=fetch_active_campaigns(sponsor_id), sponsor_id=sponsor_id, 
                           first_name=sponsor.first_name, last_name=sponsor.last_name, completed_campaigns=fetch_completed_campaigns(sponsor_id), scheduled_campaigns=fetch_scheduled_campaigns(sponsor_id))


@app.route('/add_campaign/<int:sponsor_id>', methods=['GET', 'POST'])
def add_campaign(sponsor_id):
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()

    # retrieving details from form
    title = request.form.get('campaignTitle')
    description = request.form.get('campaignDescription')
    budget = float(request.form.get('campaignBudget'))
    start_date_str = request.form.get('campaignStartDate')
    end_date_str = request.form.get('campaignEndDate')
    visibility = request.form.get('campaignVisibility')
    goal = request.form.get('campaignGoal')

    # getting dates in the desired format
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Checking if the total campaign budget exceeds the sponsor budget
    is_valid, message = check_total_campaign_budget(sponsor_id, budget)
    if not is_valid:
        return render_template('sponsor_all_campaigns.html', active_campaigns=fetch_active_campaigns(sponsor_id), sponsor_id=sponsor_id, 
                           first_name=sponsor.first_name, last_name=sponsor.last_name, completed_campaigns=fetch_completed_campaigns(sponsor_id),
                           scheduled_campaigns=fetch_scheduled_campaigns(sponsor_id), error=message)

    # creating a new campaign
    new_campaign = Campaign(title=title, description=description, budget=budget, start_date=start_date, end_date=end_date, 
                            visibility=visibility, goal=goal, sponsor_id=sponsor_id)
    db.session.add(new_campaign)
    db.session.commit()

    return render_template('sponsor_all_campaigns.html', active_campaigns=fetch_active_campaigns(sponsor_id), sponsor_id=sponsor_id, 
                           first_name=sponsor.first_name, last_name=sponsor.last_name, completed_campaigns=fetch_completed_campaigns(sponsor_id),
                           scheduled_campaigns=fetch_scheduled_campaigns(sponsor_id))


@app.route('/edit_campaign/<int:sponsor_id>/<int:camp_id>', methods=['GET', 'POST'])
def edit_campaign(sponsor_id, camp_id):
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()

    # retrieving values from the form
    title = request.form.get('campaignTitle')
    description = request.form.get('campaignDescription')
    budget = float(request.form.get('campaignBudget'))
    start_date = request.form.get('campaignStartDate')
    end_date = request.form.get('campaignEndDate')
    visibility = request.form.get('campaignVisibility')
    goal = request.form.get('campaignGoal')

    # locate the record where the edits are to be made
    existing_campaign = Campaign.query.filter_by(id=camp_id).first()

    # checking if the campaign's budget exceeds the total sponsor budget
    is_valid, message = check_total_campaign_budget(sponsor_id, budget, existing_campaign.budget)
    if not is_valid:
        return render_template('sponsor_all_campaigns.html', first_name=sponsor.first_name, last_name=sponsor.last_name, sponsor_id=sponsor_id, 
                           active_campaigns=fetch_active_campaigns(sponsor_id), completed_campaigns=fetch_completed_campaigns(sponsor_id),
                           scheduled_campaigns=fetch_scheduled_campaigns(sponsor_id), error=message)

    # editing the details
    existing_campaign.title = title
    existing_campaign.description = description
    existing_campaign.budget = budget
    existing_campaign.start_date =  datetime.strptime(start_date, '%Y-%m-%d').date()
    existing_campaign.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    existing_campaign.visibility = visibility
    existing_campaign.goal = goal

    db.session.commit()

    return render_template('sponsor_all_campaigns.html', first_name=sponsor.first_name, last_name=sponsor.last_name, sponsor_id=sponsor_id, 
                           active_campaigns=fetch_active_campaigns(sponsor_id), completed_campaigns=fetch_completed_campaigns(sponsor_id),
                           scheduled_campaigns=fetch_scheduled_campaigns(sponsor_id), error='')


@app.route('/delete_campaign/<int:sponsor_id>/<int:camp_id>', methods=['GET', 'POST'])
def delete_campaign(sponsor_id, camp_id):
    existing_campaign = Campaign.query.filter_by(id=camp_id).first()
    if existing_campaign:
        db.session.delete(existing_campaign)
        db.session.commit()
    
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    return render_template('sponsor_all_campaigns.html', active_campaigns=fetch_active_campaigns(sponsor_id), sponsor_id=sponsor_id, 
                           first_name=sponsor.first_name, last_name=sponsor.last_name, completed_campaigns=fetch_completed_campaigns(sponsor_id), 
                           scheduled_campaigns=fetch_scheduled_campaigns(sponsor_id))


@app.route('/new_ad_request/<int:sponsor_id>/<int:camp_id>', methods=['GET', 'POST'])
def create_ad_request(sponsor_id, camp_id):
    niches = Niche.query.all()
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()

    # getting values from form
    title = request.form.get('adTitle')
    payment_amount = float(request.form.get('adPaymentAmount'))
    requirement = request.form.get('adRequirement')
    niche_id = request.form.get('adNiche')

    # check if others is selected as a niche
    if niche_id == 'other':
        new_niche_name = request.form.get('otherNiche')
        new_niche = Niche(name=new_niche_name)
        db.session.add(new_niche)
        db.session.commit()
        niche_id = new_niche.id

    # checking if the ad's payment amount exceeds the total campaign budget
    is_valid, message = check_total_payment_amount(camp_id, payment_amount)
    if not is_valid:
        return render_template('sponsor_campaign_details.html', sponsor_id=sponsor_id, campaign_info=fetch_campaign_details(camp_id),
                    first_name=sponsor.first_name, last_name=sponsor.last_name, niches=niches, error=message)

    # creating new ad request
    new_ad_request = Ad_Request(title=title, requirement=requirement, payment_amount=payment_amount, niche_id=niche_id, campaign_id=camp_id)
    db.session.add(new_ad_request)
    db.session.commit()

    return render_template('sponsor_campaign_details.html', sponsor_id=sponsor_id, campaign_info=fetch_campaign_details(camp_id),
                    first_name=sponsor.first_name, last_name=sponsor.last_name, niches=niches)


@app.route('/find_influencer_for_ad/<int:sponsor_id>/<int:camp_id>/<int:ad_id>', methods=['GET','POST'])
def find_influencer_for_ads(sponsor_id, camp_id, ad_id):
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    return render_template('sponsor_ad_request_influencer.html', sponsor_id=sponsor_id, first_name=sponsor.first_name, last_name=sponsor.last_name,
                    all_influencers=fetch_influencer_details_for_sponsor(), camp_id=camp_id, ad_request_id=ad_id)
    

# When a sponsor requests an influencer for an ad, he adds the influencer's id in the influencer_id attribute of the ad and also sets the status of the ad as 'pending'
@app.route('/request_influencer_for_ad/<int:sponsor_id>/<int:camp_id>/<int:ad_id>/<int:influencer_id>', methods=['GET','POST'])
def request_influencer_for_ad(sponsor_id, camp_id, ad_id, influencer_id):
    ad_request = Ad_Request.query.filter_by(id=ad_id).first()
    ad_request.influencer_id = influencer_id
    ad_request.status = 'pending'
    db.session.commit()

    niches = Niche.query.all()
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    return render_template('sponsor_campaign_details.html', sponsor_id=sponsor_id, campaign_info=fetch_campaign_details(camp_id),
                           first_name=sponsor.first_name, last_name=sponsor.last_name, niches=niches)


@app.route('/edit_ad/<int:sponsor_id>/<int:camp_id>/<int:ad_id>', methods=['GET', 'POST'])
def edit_ad_request(sponsor_id, camp_id, ad_id):
    niches = Niche.query.all()
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()

    # getting values from form
    title = request.form.get('adTitle')
    payment_amount = float(request.form.get('adPaymentAmount'))
    requirement = request.form.get('adRequirement')
    niche_id = request.form.get('adNiche')

    # locate the record where the edits are to be made
    existing_ad = Ad_Request.query.filter_by(id=ad_id).first()

    # cheching if after editing the payment amount exceeds the toal cmapaign budget
    is_valid, message = check_total_payment_amount(camp_id, payment_amount, existing_ad.payment_amount)
    if not is_valid:
        return render_template('sponsor_campaign_details.html', sponsor_id=sponsor_id, campaign_info=fetch_campaign_details(camp_id),
                    first_name=sponsor.first_name, last_name=sponsor.last_name, niches=niches, error=message)

    existing_ad.title = title
    existing_ad.payment_amount = payment_amount
    existing_ad.niche_id = niche_id
    existing_ad.requirement = requirement

    db.session.commit()

    return render_template('sponsor_campaign_details.html', sponsor_id=sponsor_id, campaign_info=fetch_campaign_details(camp_id),
                    first_name=sponsor.first_name, last_name=sponsor.last_name, niches=niches, error='')


@app.route('/delete_ad/<int:sponsor_id>/<int:camp_id>/<int:ad_id>', methods=['GET', 'POST'])
def delete_ad_request(sponsor_id, camp_id, ad_id):
    existing_ad = Ad_Request.query.filter_by(id=ad_id).first()
    if existing_ad:
        db.session.delete(existing_ad)
        db.session.commit()

    niches = Niche.query.all()
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    return render_template('sponsor_campaign_details.html', sponsor_id=sponsor_id, campaign_info=fetch_campaign_details(camp_id),
                    first_name=sponsor.first_name, last_name=sponsor.last_name, niches=niches)

# more routes




# ---------------------------------------------------------- USER DEFINED FUNCTIONS ---------------------------------------------------------- #



'''function to calculate the progress of a camp/ad based on the start and end date'''
def progress(start_date, end_date):
    current_date = datetime.now().date()
    total_duration = (end_date - start_date).days
    elapsed_duration = (current_date - start_date).days
    progress = (elapsed_duration / total_duration) * 100

    return int(min(max(progress, 0), 100))


'''function for retrieving all (unflagged) active campaigns for sposnor_all_campaigns and admin_find page'''
def fetch_active_campaigns(sponsor_id=None):
    current_date = datetime.now().date()

    if sponsor_id:
        # Logic for fetching active campaigns for a specific sponsor
        campaigns = (db.session.query(Campaign)
                    .filter(Campaign.start_date <= current_date, Campaign.end_date >= current_date, 
                            Campaign.sponsor_id==sponsor_id, Campaign.flagged==False).all())
    else:
        # Logic for fetching active campaigns for admin
        campaigns = (db.session.query(Campaign)
                    .filter(Campaign.start_date <= current_date, Campaign.end_date >= current_date, Campaign.flagged==False)
                    .all())
        
    active_campaigns = {}
    for campaign in campaigns:
        if campaign.id not in active_campaigns.keys():
            active_campaigns[campaign.id] = {'title': campaign.title, 'description': campaign.description,'goal': campaign.goal,
                                            'start_date': campaign.start_date, 'end_date': campaign.end_date, 'budget': campaign.budget,
                                            'visibility': campaign.visibility, 'progress':progress(campaign.start_date, campaign.end_date)}
    return active_campaigns

'''function for retrieving all flagged campaigns for admin dashboard'''
def fetch_flagged_campaigns():
    campaigns = Campaign.query.filter_by(flagged=True).all()
    flagged_campaigns = {}
    for campaign in campaigns:
        if campaign.id not in flagged_campaigns.keys():
            flagged_campaigns[campaign.id] = {'title': campaign.title, 'description': campaign.description, 'goal': campaign.goal, 
                                              'start_date':campaign.start_date, 'end_date': campaign.end_date}
    return flagged_campaigns

'''function for retrieving all flagged influencers for admin dashboard'''
def fetch_flagged_influencers():
    influencers = Influencer.query.filter_by(flagged=True).all()
    flagged_influencers = {}
    for influencer in influencers:
        if influencer.id not in flagged_influencers.keys():
            flagged_influencers[influencer.id] = {'fname': influencer.first_name, 'lname': influencer.last_name, 'username': influencer.username,
                                                  'social_accounts': social_accounts(influencer.id), 'niches': niches(influencer.id)}
    return flagged_influencers

'''function for retrieving all flagged sponsors for admin dashboard'''
def fetch_flagged_sponsors():
    sponsors = Sponsor.query.filter_by(flagged=True).all()
    flagged_sponsors = {}
    for sponsor in sponsors:
        if sponsor.id not in flagged_sponsors.keys():
            flagged_sponsors[sponsor.id] = {'fname': sponsor.first_name, 'lname': sponsor.last_name, 'username': sponsor.username, 'industry': sponsor.industry,
                                            'budget': sponsor.budget, 'type': sponsor.type, 'email': sponsor.email}
    return flagged_sponsors

'''function for retrieving all (unflagged) influencers' data for admin find page'''
def fetch_all_influencers():
    influencers = Influencer.query.filter_by(flagged=False).all()
    all_influencers = {}
    for influencer in influencers:
        if influencer.id not in all_influencers.keys():
            all_influencers[influencer.id] = {'fname': influencer.first_name, 'lname': influencer.last_name, 'username': influencer.username, 'earning': influencer.earning,
                                              'email': influencer.email, 'social_accounts': social_accounts(influencer.id), 'niches': niches(influencer.id)}
    return all_influencers

'''function for retrieving all (unflagged) sponsors' data for admin find page'''
def fetch_all_sponsors():
    sponsors = Sponsor.query.filter_by(flagged=False).all()
    all_sponsors = {}
    for sponsor in sponsors:
        if sponsor.id not in all_sponsors.keys():
            all_sponsors[sponsor.id] = {'fname': sponsor.first_name, 'lname': sponsor.last_name, 'industry': sponsor.industry,
                                        'budget': sponsor.budget, 'email': sponsor.email, 'type': sponsor.type }
    return all_sponsors

'''function for retrieving all completed campaigns for sponsor_all_campaigns page and admin_find page'''
def fetch_completed_campaigns(sponsor_id=None):
    current_date = datetime.now().date()

    if sponsor_id:
        # Logic for finding out completed campaigns for a particular sponsor
        campaigns = (db.session.query(Campaign)
                .filter(Campaign.end_date < current_date, Campaign.sponsor_id==sponsor_id).all())
    else:
        # Logic for finding out all completed campaigns for admin
        campaigns = (db.session.query(Campaign)
                .filter(Campaign.end_date < current_date).all())

    completed_campaigns = {}
    for campaign in campaigns:
        if campaign.id not in completed_campaigns.keys():
            completed_campaigns[campaign.id] = {'title': campaign.title, 'description': campaign.description, 'goal': campaign.goal, 'budget': campaign.budget,
                                                'start_date': campaign.start_date, 'end_date': campaign.end_date, 'visibility': campaign.visibility}
    return completed_campaigns

'''fucntion for fetching all campaigns scheduled for future for sponsor_all_campaigns and admin_find page'''
def fetch_scheduled_campaigns(sponsor_id=None):
    current_date = datetime.now().date()

    if sponsor_id:
        # Logic for finding out scheduled campaigns for a particular sponsor
        campaigns = (db.session.query(Campaign)
                .filter(Campaign.start_date > current_date, Campaign.sponsor_id==sponsor_id).all())
    else:
        # Logic for finding out all scheduled campaigns for admin page
        campaigns = (db.session.query(Campaign)
                .filter(Campaign.start_date > current_date).all())

    scheduled_campaigns = {}
    for campaign in campaigns:
        if campaign.id not in scheduled_campaigns.keys():
            scheduled_campaigns[campaign.id] = {'title': campaign.title, 'description': campaign.description, 'goal': campaign.goal, 'budget': campaign.budget,
                                                'start_date': campaign.start_date, 'end_date': campaign.end_date, 'visibility': campaign.visibility}
    return scheduled_campaigns

'''function for retrieving pending ad requests for sponsor dashboard. These are those ad requests that the sponsor has send to a particular influencer
and is waiting for the influencer to accept/reject'''
def fetch_pending_ad_requests_of_sponsor(sponsor_id):
    ad_requests = (db.session.query(Ad_Request.id, Ad_Request.title.label('ad_title'),
                                    Campaign.title.label('campaign_title'),
                                    Influencer.first_name, Influencer.last_name)
                                    .join(Campaign, Ad_Request.campaign_id==Campaign.id)
                                    .join(Influencer, Ad_Request.influencer_id==Influencer.id)
                                    .filter(Campaign.sponsor_id==sponsor_id, Ad_Request.status=='pending').all())
    pending_ad_requests = {}
    for ad in ad_requests:
        if ad.id not in pending_ad_requests.keys():
            pending_ad_requests[ad.id] = {'ad_title':ad.ad_title, 'campaign_title':ad.campaign_title, 
                                          'influencer_fname': ad.first_name, 'influencer_lname': ad.last_name}
    return pending_ad_requests

'''function for retrieving the requested ad requests for sponsor dashboard. These are those ad requests that an influencer has requested to
a sponsor for and is waiting for conformation from the sponsors side.'''
def fetch_requested_ad_requests_for_sponsor(sponsor_id):
    ad_requests = (db.session.query(Ad_Request.id, Ad_Request.title.label('ad_title'), Ad_Request.influencer_id,
                                    Campaign.title.label('campaign_title'),
                                    Influencer.first_name, Influencer.last_name)
                                    .join(Campaign, Campaign.id == Ad_Request.campaign_id)
                                    .join(Influencer, Influencer.id == Ad_Request.influencer_id)
                                    .filter(Campaign.sponsor_id == sponsor_id, Ad_Request.status == 'requested').all())
    requested_ad_requests = {}
    for ad in ad_requests:
        if ad.id not in requested_ad_requests.keys():
            requested_ad_requests[ad.id] = {'ad_title':ad.ad_title, 'campaign_title':ad.campaign_title, 'influencer_fname': ad.first_name, 'influencer_lname': ad.last_name,
                                            'social_accounts': social_accounts(ad.influencer_id), 'niches': niches(ad.influencer_id)}
    return requested_ad_requests


'''function for retrieving all (unflagged) influencer details for sponsor find page'''
def fetch_influencer_details_for_sponsor(niche_id = None):
    if niche_id: 
        # if a niche_id has been provided then filter only those influencers that have this niche associated with them
        influencers = (db.session.query(Influencer.id, Influencer.first_name, Influencer.last_name,
                                    Niche.name.label('niche_name'),
                                    Reach.platform, Reach.profile_link, Reach.followers)
                                    .join(Influencer_Niche, Influencer_Niche.influencer_id==Influencer.id)
                                    .join(Niche, Niche.id==Influencer_Niche.niche_id)
                                    .join(Reach, Reach.influencer_id==Influencer.id)
                                    .filter(Influencer.flagged==False, Niche.id==niche_id).all())
    else: 
        # if no niche_id is passed, it is None by default and all influencers are to be queried from the database.
        influencers = (db.session.query(Influencer.id, Influencer.first_name, Influencer.last_name,
                                    Niche.name.label('niche_name'),
                                    Reach.platform, Reach.profile_link, Reach.followers)
                                    .join(Influencer_Niche, Influencer_Niche.influencer_id==Influencer.id)
                                    .join(Niche, Niche.id==Influencer_Niche.niche_id)
                                    .join(Reach, Reach.influencer_id==Influencer.id)
                                    .filter(Influencer.flagged==False).all())
    all_influencers = {}
    for influencer in influencers:
        if influencer.id not in all_influencers.keys():
            all_influencers[influencer.id] = {'fname': influencer.first_name, 'lname': influencer.last_name, 
                                              'social_accounts': social_accounts(influencer.id), 'niches': niches(influencer.id)}
        
    return all_influencers

'''function for checking if the new campaign's budget will cumulatively exceed the total sponsor budget'''
def check_total_campaign_budget(sponsor_id, new_campaign_budget, existing_campaign_budget=0):
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).all()
    total_budget = sum(campaign.budget for campaign in campaigns) - existing_campaign_budget + new_campaign_budget
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    if sponsor.budget < total_budget:
        return False, f"Total campaign budget exceeded the sponsor budget of {sponsor.budget}. Try again!"
    return True, ""


'''function for checking if the new ad's budget will cumulatively exceed the total campaign budget'''
def check_total_payment_amount(camp_id, new_ad_payment, existing_ad_payment=0):
    ads = Ad_Request.query.filter_by(campaign_id=camp_id).all()
    total_payment = sum(ad.payment_amount for ad in ads) - existing_ad_payment + new_ad_payment
    campaign = Campaign.query.filter_by(id=camp_id).first()
    if campaign.budget < total_payment:
        return False, f"Total payment amount exceeded the campaign budget of {campaign.budget}. Try again!"
    return True, ""



'''function for retrieving the details of a particular campaign and its associated ad_requests for sponsor_campaign_details and admin_campaign_details page'''
def fetch_campaign_details(camp_id):
    campaigns = (db.session.query(Campaign.id.label('campaign_id'), Campaign.title.label('campaign_title'), Campaign.description, Campaign.flagged,
                                Campaign.start_date, Campaign.end_date, Campaign.visibility, Campaign.budget, Campaign.goal,
                                Ad_Request.id.label('ad_id'), Ad_Request.title.label('ad_title'), Ad_Request.requirement,
                                Ad_Request.payment_amount, Ad_Request.status, Ad_Request.influencer_id,
                                Niche.name.label('niche_name'),
                                Influencer.first_name, Influencer.last_name)
                                .outerjoin(Ad_Request, Ad_Request.campaign_id==Campaign.id)
                                .outerjoin(Niche, Niche.id==Ad_Request.niche_id)
                                .outerjoin(Influencer, Influencer.id==Ad_Request.influencer_id)
                                .filter(Campaign.id==camp_id).all())
    campaign_info = {}
    for campaign in campaigns:
        if campaign.campaign_id not in campaign_info.keys():
            campaign_info[campaign.campaign_id] = {'title':campaign.campaign_title, 'description': campaign.description, 'goal': campaign.goal, 'start_date': campaign.start_date, 
                                        'end_date': campaign.end_date,'visibility': campaign.visibility, 'budget': campaign.budget, 'flagged': campaign.flagged, 'ads': {}}
        
        if campaign.ad_id not in campaign_info[campaign.campaign_id]['ads'].keys():
            campaign_info[campaign.campaign_id]['ads'][campaign.ad_id] = {'title': campaign.ad_title, 'requirements': campaign.requirement, 
                                                            'payment_amount': campaign.payment_amount, 'influencer_fname': campaign.first_name, 
                                                            'influencer_lname': campaign.last_name, 'influencer_id':campaign.influencer_id, 'status': campaign.status, 'niche': campaign.niche_name}

    return campaign_info
        
'''function for retrieving influencer details of a particular influencer for his/her influencer_dashboard'''
def fetch_influencer_details(influencer_id):
    influencer = Influencer.query.filter_by(id=influencer_id).first()
    influencer_info = {influencer.id: {}}
    influencer_info[influencer.id] = {'fname': influencer.first_name, 'lname': influencer.last_name, 'username': influencer.username,
                                      'email': influencer.email, 'earning':influencer.earning,
                                      'social_accounts':social_accounts(influencer_id), 'niches': niches(influencer_id)}
    return influencer_info

'''function for retrieving social accounts of an influencer'''
def social_accounts(influencer_id):
    tuples = (db.session.query(Influencer.id, Reach.platform, Reach.followers, Reach.profile_link)
                  .join(Reach, Reach.influencer_id==influencer_id).all())
    social_accounts = {}
    for tuple in tuples:
        if tuple.platform not in social_accounts.keys():
            social_accounts[tuple.platform] = {'followers': tuple.followers, 'profile_link': tuple.profile_link}
    return social_accounts

'''function for retrieving niches of an influencer'''
def niches(influencer_id):
    tuples = (db.session.query(Niche.id.label('niche_id'), Niche.name.label('niche_name'))
              .join(Influencer_Niche, Influencer_Niche.niche_id == Niche.id)
              .join(Influencer, Influencer.id == Influencer_Niche.influencer_id)
              .filter(Influencer.id == influencer_id).all())
    niches = []
    for tuple in tuples:
        niches.append(tuple.niche_name)
    return niches


'''function for retrieving active ad_requests' details for influencer_dashboard. Active ad requests for an influencer are those whose influencer_id 
matches, whose campaign's timeline is going on, campaign isn't flagged and the request status is accepted.'''
def fetch_active_ads(influencer_id):
    current_date = datetime.now().date()
    ads = (db.session.query(Ad_Request.id, Ad_Request.title.label('ad_title'), Ad_Request.payment_amount, Ad_Request.requirement,
                            Campaign.title.label('campaign_title'), Campaign.description, Campaign.goal, Campaign.start_date, Campaign.end_date,
                            Sponsor.first_name, Sponsor.last_name, Sponsor.type, Niche.name.label('niche_name'))
                            .join(Campaign, Campaign.id==Ad_Request.campaign_id)
                            .join(Sponsor, Campaign.sponsor_id==Sponsor.id)
                            .join(Niche, Ad_Request.niche_id==Niche.id)
                            .filter(Campaign.start_date <= current_date, Campaign.end_date >= current_date,
                                    Ad_Request.influencer_id==influencer_id, Campaign.flagged==False, Ad_Request.status=='accepted').all())
    active_ads = {}
    for ad in ads:
        if ad.id not in active_ads.keys():
            active_ads[ad.id] = {'ad_title':ad.ad_title, 'payment_amount': ad.payment_amount, 'ad_requirement': ad.requirement, 
                                 'campaign_title': ad.campaign_title, 'campaign_description': ad.description, 'sdate': ad.start_date, 'edate': ad.end_date,
                                 'sponsor_fname': ad.first_name, 'sponsor_lname': ad.last_name, 'sponsor_type': ad.type, 'niche': ad.niche_name, 
                                 'progress': progress(ad.start_date, ad.end_date)}
    return active_ads

'''function for retreiving pending ad_requests for influencer_dashboard. Pending ads for an influencer are those that have the same influencer_id,
are the 'status' of those ads is 'pending and the campaign is not flagged and the corresponsing campaign isn't completed yet.'''
def fetch_pending_ad_requests_for_influencer(influencer_id):
    current_date = datetime.now().date()
    ads = (db.session.query(Ad_Request.id, Ad_Request.title.label('ad_title'), Ad_Request.payment_amount, Ad_Request.requirement, Ad_Request.niche_id,
                            Campaign.title.label('campaign_title'), Campaign.description, Campaign.goal, Campaign.start_date, Campaign.end_date,
                            Sponsor.first_name, Sponsor.last_name, Sponsor.type, Niche.name.label('niche_name'))
                            .join(Campaign, Campaign.id==Ad_Request.campaign_id)
                            .join(Sponsor, Campaign.sponsor_id==Sponsor.id)
                            .join(Niche, Ad_Request.niche_id==Niche.id)
                            .filter(Ad_Request.influencer_id==influencer_id, Campaign.flagged==False, Ad_Request.status=='pending', Campaign.end_date > current_date).all())
    pending_ads = {}
    for ad in ads:
        if ad.id not in pending_ads.keys():
            pending_ads[ad.id] = {'ad_title':ad.ad_title, 'payment_amount': ad.payment_amount, 'ad_requirement': ad.requirement, 
                                 'campaign_title': ad.campaign_title, 'campaign_description': ad.description, 'sdate': ad.start_date, 'edate': ad.end_date,
                                 'sponsor_fname': ad.first_name, 'sponsor_lname': ad.last_name, 'sponsor_type': ad.type, 'niche': ad.niche_name, 'niche_id': ad.niche_id}
    return pending_ads


'''function for retreiving all requested ad requests for influencer_dashboard. These are those ad requests that the influencer requested for to the sponsor'''
def fetch_requested_ad_requests_of_influencer(influencer_id):
    ad_requests = (db.session.query(Ad_Request.id, Ad_Request.title.label('ad_title'), Ad_Request.payment_amount,
                                    Campaign.title.label('campaign_title'), Campaign.start_date, Campaign.end_date,
                                    Sponsor.first_name, Sponsor.last_name)
                                    .join(Campaign, Campaign.id == Ad_Request.campaign_id)
                                    .join(Sponsor, Sponsor.id == Campaign.sponsor_id)
                                    .filter(Ad_Request.influencer_id == influencer_id, Ad_Request.status == 'requested').all())
    requested_ads = {}
    for ad in ad_requests:
        if ad.id not in requested_ads.keys():
            requested_ads[ad.id] = {'ad_title': ad.ad_title, 'campaign_title': ad.campaign_title, 'sdate': ad.start_date, 'edate': ad.end_date,
                                    'payment_amount': ad.payment_amount, 'sponsor_fname': ad.first_name, 'sponsor_lname': ad.last_name}
    return requested_ads


'''function for retreiving the ad requests of all public and unflagged campaigns for influencer_find page'''
def fetch_all_ads(niche_id = None):
    if niche_id:
        # if a niche name has been passed as an argument to the function then filter ads based on that.
        ad_requests = (db.session.query(Ad_Request.id, Ad_Request.title.label('ad_title'), Ad_Request.payment_amount, Ad_Request.requirement, Ad_Request.influencer_id,
                                Campaign.title.label('campaign_title'), Campaign.description, Campaign.goal, Campaign.start_date, Campaign.end_date,
                                Sponsor.first_name, Sponsor.last_name, Sponsor.type, Niche.name.label('niche_name'), Niche.id.label('niche_id'))
                                .join(Campaign, Campaign.id==Ad_Request.campaign_id)
                                .join(Sponsor, Campaign.sponsor_id==Sponsor.id)
                                .join(Niche, Ad_Request.niche_id==Niche.id)
                                .filter(Campaign.flagged==False, Campaign.visibility=='public', Ad_Request.status == None, Niche.id==niche_id).all())
    else:
        # if no niche name has been passed, it is None by default and we'll query all the ads irrespective of their niche from db.
        ad_requests = (db.session.query(Ad_Request.id, Ad_Request.title.label('ad_title'), Ad_Request.payment_amount, Ad_Request.requirement, Ad_Request.influencer_id,
                                Campaign.title.label('campaign_title'), Campaign.description, Campaign.goal, Campaign.start_date, Campaign.end_date,
                                Sponsor.first_name, Sponsor.last_name, Sponsor.type, Niche.name.label('niche_name'))
                                .join(Campaign, Campaign.id==Ad_Request.campaign_id)
                                .join(Sponsor, Campaign.sponsor_id==Sponsor.id)
                                .join(Niche, Ad_Request.niche_id==Niche.id)
                                .filter(Campaign.flagged==False, Campaign.visibility=='public').all())
    all_ads = {}
    for ad in ad_requests:
        if ad.id not in all_ads.keys():
            all_ads[ad.id] = {'ad_title':ad.ad_title, 'payment_amount': ad.payment_amount, 'ad_requirement': ad.requirement, 
                                 'campaign_title': ad.campaign_title, 'campaign_description': ad.description, 'sdate': ad.start_date, 'edate': ad.end_date,
                                 'sponsor_fname': ad.first_name, 'sponsor_lname': ad.last_name, 'sponsor_type': ad.type, 'niche': ad.niche_name, 'assigned_influencer':ad.influencer_id}
    return all_ads


'''function for retreiving all public and unflagged campaigns (those that are not completed yet) for influencer_find page'''
def fetch_all_public_campaigns():
    current_date = datetime.now().date()
    campaigns = Campaign.query.filter(Campaign.end_date > current_date, Campaign.visibility=='public', Campaign.flagged==False).all()
    all_public_campaigns = {}
    for campaign in campaigns:
        if campaign.id not in all_public_campaigns.keys():
            all_public_campaigns[campaign.id] = {'title': campaign.title, 'description': campaign.description, 'goal': campaign.goal,
                                                 'sdate': campaign.start_date, 'edate': campaign.end_date, 'budget': campaign.budget}
    return all_public_campaigns


'''function for checking how many ads got completed'''
def check_ad_requests():
    current_date = datetime.now().date()
    
    # Retrieve all ad requests
    ad_requests = Ad_Request.query.all()
    
    for ad_request in ad_requests:
        campaign = Campaign.query.get(ad_request.campaign_id)
        if campaign and campaign.end_date < current_date:
            if ad_request.status != 'completed':
                # Retrieve the influencer associated with the ad request
                influencer = Influencer.query.get(ad_request.influencer_id)
                if influencer:
                    ad_request.status = 'completed'     # Update the status of the ad request to 'completed'
                    influencer.earnings += ad_request.payment_amount   # Update the influencer's earnings
                    
                    db.session.commit()
