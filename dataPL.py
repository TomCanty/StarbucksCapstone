import pandas
import numpy

 def id_viewed(row):
        ''' matches up offers and views by same person and offer within time limit.   
        Marks offer/person/time as viewed and notes the time of the view.
        
        input: df row per pd.apply()
        output: updated df row 
        '''
        for idx,trn in t_viewed[(t_viewed.person == row.person)&(t_viewed.offer_id == row.offer_id)].sort_values(by='time').iterrows():
            if (trn.time >= row.time) & (trn.time < row.time_end ):
                row['event_offer viewed'] = 1
                row['time_viewed'] = trn['time']
                return row
        return row

def scrub_trans(row):
        '''
        Matches transactions to offer based on the following conditions
        - person matches
        - transaction was made after offer was made
        - transaction was viewed
        - transaction was made after the offer was viewed
        - transaction was made before offer expired.
        '''
        #print(row['person'])
        for idx,trn in t_trans[t_trans.person == row.person].sort_values(by='time').iterrows():
            if (trn.time >= row.time) & (row['event_offer viewed']==1) &(trn.time < row.time_end ) & (trn.time >= row.time_viewed):
                row['event_transaction'] = 1
                row['trans_time'] = trn['time']
                row['trans_spend'] = trn['amount']
                return row
        return row

def scrub_compl(row):
    '''   
    Runs through the t_offer dataframe and marks offer as complete under the following contionds
    

    marks the offer complete if
    - person and offer match
    - 
    
    input: df row per pd.apply() function
    '''
    for idx,trn in t_compl[(t_compl.person == row.person)&(t_compl.offer_id == row.offer_id)].sort_values(by='time').iterrows():
        if (trn.time >= row.time) & (trn.time < row.time_end ):
            row['event_offer completed'] = 1
            row['reward'] = trn.reward
            
            return row
    return row

def organize_raw_data(portfolio=portfolio,profile=profile,transcript=transcript):
    ''' This function organizes the raw data via setting datatype, setting indexes, and onehotencoding
    input: Startbuck challenge raw dataframes: portfolio,profile, and transcrips
    
    output: (7 dataframes, 3 revised originals and 4 which are filtered versions of transcript)
    portfolio_new: portfolio (one hot encoded channels, some column renames)
    profile_new: cleaned profile (member start date to datetime, one hot encoded gender)
    transcript_new: cleaned transcript 
        (value dict-> one hot encoded event type, 
        amount(spend), reward(completion), offer_id(offers,view/complte))
    t_offer: transcript_new filtered:offers only
    t_viewed: transcript_new filtered:viewed only
    t_trans: transcript_new filtered:transactions only
    t_compl: transcript_new filtered:complteted offers only
    
    '''
    
    
    ############### Portfolio
    portfolio.rename(columns={'id':'offer_id'},inplace=True) # match other table 
    mlb = MultiLabelBinarizer()  # one hot encode channels
    portfolio = portfolio.join(pd.DataFrame(mlb.fit_transform(portfolio.pop('channels')),
                          columns=mlb.classes_,
                          index=portfolio.index))
    portfolio = portfolio.merge(pd.get_dummies(portfolio['offer_type'],prefix='offer',prefix_sep='_'),left_index=True,right_index=True)   
    portfolio.set_index('offer_id') # Since offer_id is unique, we can use that as an index
    
    ############### Profile
    profile_na = profile[profile.gender.isna()] 
    profile.loc[:,'became_member_on']=pd.to_datetime(profile['became_member_on'],format='%Y%m%d') #Convert to datetime
    profile = profile.merge(pd.get_dummies(profile['gender'],prefix='gender',prefix_sep='_'),left_index=True,right_index=True) #one hot encode gender
    profile['memb_leng'] = (profile.became_member_on.max()-profile.became_member_on).dt.days.astype(float)/(365.25/12) #Relative leng of memb
    profile.set_index('id',inplace=True)  # Since id is unique, we can use that as an index
    
    ################# Transcript
    
    transcript = transcript.merge(transcript.value.apply(pd.Series),left_index=True,right_index=True)
    transcript.loc[transcript['offer_id'].isna(),'offer_id'] = transcript[transcript['offer_id'].isna()]['offer id'] # cleaning up 'offer_id' and 'offer id', so as there is a single column
    transcript = transcript.merge(pd.get_dummies(transcript['event'],prefix='event',prefix_sep='_'),left_index=True, right_index=True)
    transcript.drop(columns = ['offer id','value'],inplace=True)
    transcript = transcript[transcript['person'].isin(profile.index)].reset_index()
    
    ### break apart into sub-df based on transaction tyle
    t_offer = transcript[transcript['event']=='offer received']
    t_viewed = transcript[transcript['event']=='offer viewed']
    t_trans = transcript[transcript['event']=='transaction']
    t_compl = transcript[transcript['event']=='offer completed']
    
    ###Lookup the duration of each offer and convert to hours to match offer time data.
###and create a time end

    t_matched = pd.merge(t_offer,portfolio[['offer_id','duration']],on=['offer_id'],how='left')
    t_matched['duration'] = t_matched['duration'].progress_apply(lambda x: x*24) # Convert duration to hours
    t_matched['time_end'] = t_matched['time'] + t_matched['duration'] 
    t_matched = t_matched.progress_apply(id_viewed,axis=1)
    t_matched[['trans_time','trans_spend','reward']] = np.nan
    t_matched = t_matched.progress_apply(scrub_trans,axis=1)
    t_matched = t_matched.progress_apply(scrub_compl,axis=1)



# Merge pertinant fields from profile
    prof_merge_col = ['age','income','gender','gender_F',
        'gender_M', 'gender_O', 'memb_leng']

    events = events.merge(profile_new[prof_merge_col],how='left',left_on='person',right_on=profile_new.index)

    # Merge pertinant fields from portfolio

    port_merge_col = ['difficulty', 'offer_id', 'email', 'mobile',
        'social', 'web', 'offer_bogo', 'offer_discount',
        'offer_informational','reward']

    events = events.merge(portfolio_new[port_merge_col],on='offer_id')
    events.rename(columns={'reward_x':'reward_rcvd','reward_y':'reward_offd'},inplace=True)

    #Other
    events.drop(columns='amount',inplace=True)
    events.rename(columns={'event_offer completed':'event_offer_completed','event_offer received':'event_offer_received','event_offer viewed':'event_offer_viewed'},inplace=True)
 





    
    return portfolio,profile,profile_na,transcript,t_offer,t_viewed,t_trans,t_compl


def main():
    
    if len(sys.argv) == 4:

        port_filepath, profile_filepath, trans_filepath, pickle_filepath  = sys.argv[1:]

        print('Loading data...\n    PORTFOLIO: {}\n    PROFILE: {}\n    TRANSCRIPT: {}'
              .format(port_filepath, profile_filepath,trans_filepath))
        
        portfolio = pd.read_json(port_filepath, orient='records', lines=True)
        profile = pd.read_json(profile_filepath, orient='records', lines=True)
        transcript = pd.read_json(trans_filepath, orient='records', lines=True)
        
        print('Cleaning data...')
        portfolio_new,profile_new,profile_na,transcript_new,t_offer,t_viewed,t_trans,t_compl = organize_raw_data()
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()