''' data_pipeline:
'''
import sys
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
tqdm.pandas()

def norm_and_std(df):
    '''TODO: DOCSTRING
    '''
    df2 = df.copy()
    ## Drop
    drop_na_cols = ['age', 'income', 'gender']
    df2.dropna(subset=drop_na_cols, inplace=True)
    drop_cols = ['event', 'index', 'offer_id', 'person', 'gender']
    df2.drop(drop_cols, inplace=True, axis=1)
    ## Standardize
    s_scaler = StandardScaler()
    std_cols = ['age', 'income', 'memb_leng']
    df2[std_cols] = s_scaler.fit_transform(df2[std_cols])
    #Normalize time series data
    #I am normalizing this to the timescale of the individual offer.
    df2.loc[:, 'time_viewed'] = (df2.time_viewed - df2.time) / (df2.time_end - df2.time)
    df2.loc[:, 'trans_time'] = (df2.trans_time - df2.time) / (df2.time_end - df2.time)
    df2.loc[:, 'time'] = (df2.time)/df2.time.max()
    #Normalizing since relative magnitude is important for these.
    mm_scaler = MinMaxScaler()
    df2[['age', 'income', 'memb_leng', 'difficulty', 'reward_rcvd', 'reward_offd', 'duration']] = \
    mm_scaler.fit_transform( \
    df2[['age', 'income', 'memb_leng', 'difficulty', 'reward_rcvd', 'reward_offd', 'duration']])
    ## Standardize
    # Columns:
    # New Colun
    return df2


def organize_raw_data(portfolio, profile, transcript, dropna=True):
    ''' This function organizes the raw data via setting datatype, setting indexes, and one hot encd
        input: Startbuck challenge raw dataframes: portfolio,profile, and transcrips
            dropna (Bool): Default = True .  Drops profile roles with NA in income, gender, or age.
        output: (7 dataframes, 3 revised originals and 4 which are filtered versions of transcript)
            portfolio_new: portfolio (one hot encoded channels, some column renames)
            profile_new: cleaned profile (member start date to datetime, one hot encoded gender)
            transcript_new: cleaned transcript \
                (value dict-> one hot encoded event type, amount(spend), \
                reward(completion), offer_id(offers,view/complte))
            t_offer: transcript_new filtered:offers only
            t_viewed: transcript_new filtered:viewed only
            t_trans: transcript_new filtered:transactions only
            t_compl: transcript_new filtered:complteted offers only
    '''
    ############### Portfolio ###
    portfolio.rename(columns={'id':'offer_id'}, inplace=True)# match other table
    mlb = MultiLabelBinarizer()  # one hot encode channels
    portfolio = portfolio.join(pd.DataFrame(mlb.fit_transform(portfolio.pop('channels')), \
        columns=mlb.classes_, index=portfolio.index))
    portfolio = portfolio.merge(\
        pd.get_dummies(portfolio['offer_type'], prefix='offer', prefix_sep='_'), \
        left_index=True, right_index=True)
    portfolio.set_index('offer_id') # Since offer_id is unique, we can use that as an index
    portfolio['duration'] = portfolio['duration'].apply(lambda x: x*24)
    
    ############### Profile
    profile.loc[:, 'became_member_on'] = pd.to_datetime(profile['became_member_on'], \
        format='%Y%m%d')#Convert to datetime
    profile['memb_leng'] = (profile.became_member_on.max()-profile.became_member_on).\
        dt.days.astype(float)/(365.25/12)#Relative leng of memb
    profile = profile.merge(pd.get_dummies(profile['gender'], prefix='gender', prefix_sep='_'), \
        left_index=True, right_index=True)#one hot encode gender

    profile.set_index('id', inplace=True)  # Since id is unique, we can use that as an index
    if dropna == True:
        profile.dropna(subset=['age', 'gender', 'income'], inplace=True)

    ################# Transcript

    transcript = transcript.merge(transcript.value.apply(pd.Series), \
        left_index=True, right_index=True)
    # cleaning up 'offer_id' and 'offer id', so as there is a single column
    transcript.loc[transcript['offer_id'].isna(), 'offer_id'] = \
        transcript[transcript['offer_id'].isna()]['offer id']
    transcript = transcript.merge(\
        pd.get_dummies(transcript['event'], prefix='event', prefix_sep='_'), \
        left_index=True, right_index=True)
    transcript.drop(columns=['offer id', 'value'], inplace=True)
    transcript = transcript[transcript['person'].isin(profile.index)].reset_index()

    return portfolio, profile, transcript

def split_trans(transcript):
    t_offer = transcript[transcript['event'] == 'offer received']
    t_viewed = transcript[transcript['event'] == 'offer viewed']
    t_trans = transcript[transcript['event'] == 'transaction']
    t_compl = transcript[transcript['event'] == 'offer completed']
    
    return t_offer, t_viewed, t_trans, t_compl
def view_match(row, t_viewed):
    ''' matches up offers and views by same person and offer within time limit.
        Marks offer/person/time as viewed and notes the time of the view.

        input: df row per pd.apply()
        output: updated df row
    '''

    for idx, trn in t_viewed[(t_viewed.person == row.person)&\
    (t_viewed.offer_id == row.offer_id)].sort_values(by='time').iterrows():
        if (trn.time >= row.time) & (trn.time < row.time_end):
            row['event_offer viewed'] = 1
            row['time_viewed'] = trn['time']
        return row
    return row

def scrub_trans(row, t_trans):
    '''
    Matches transactions to offer based on the following conditions
    - person matches
    - transaction was made after offer was made
    - transaction was viewed
    - transaction was made after the offer was viewed
    - transaction was made before offer expired.'''
    for idx, trn in t_trans[t_trans.person == row.person].sort_values(by='time').iterrows():
        if (trn.time >= row.time) & (row['event_offer viewed'] == 1) & \
        (trn.time < row.time_end) & (trn.time >= row.time_viewed):
            row['event_transaction'] = 1
            row['trans_time'] = trn['time']
            row['trans_spend'] = trn['amount']
            return row
    return row

def scrub_compl(row, t_compl):
    '''
    Runs through the t_offer dataframe and marks offer as complete under the following contionds
    marks the offer complete if
    - person and offer match

    input: df row per pd.apply() function
    output: updated df row
    '''
    for idx, trn in t_compl[(t_compl.person == row.person) & \
    (t_compl.offer_id == row.offer_id)].sort_values(by='time').iterrows():
        if (trn.time >= row.time) & (trn.time < row.time_end):
            row['event_offer completed'] = 1
            row['reward_x'] = trn.reward
            return row
    return row

def merge_tables(t_offer, portfolio, profile):
    # Merge pertinant fields from profile
    prof_merge_col = ['age', 'income', 'gender', 'gender_F',\
        'gender_M', 'gender_O', 'memb_leng']
    # Merge pertinant fields from portfolio
    port_merge_col = ['offer_id', 'duration', 'difficulty', 'email', \
        'mobile', 'social', 'web', 'offer_bogo', 'offer_discount',\
        'offer_informational', 'reward']
    t_matched = pd.merge(t_offer, portfolio[port_merge_col], \
        on=['offer_id'], how='left')
    t_matched = t_matched.merge(profile[prof_merge_col], how='left', left_on='person', \
        right_on=profile.index)
    t_matched['time_end'] = t_matched['time'] + t_matched['duration']
    t_matched['trans_time'] = np.nan
    t_matched['trans_spend'] = np.nan

    return t_matched

def match_trans(t_matched, t_viewed, t_trans, t_compl):
    print('     ...Matching views...')
    t_matched = t_matched.progress_apply(view_match, axis=1, args=(t_viewed,))
    print('     ...Matching transactions...')
    t_matched = t_matched.progress_apply(scrub_trans, axis=1, args=(t_trans,))
    print('     ...Matching completions...')
    t_matched = t_matched.progress_apply(scrub_compl, axis=1, args=(t_compl,))
    return t_matched

def main():
    print(len(sys.argv))
    if len(sys.argv) == 5:

        port_filepath, profile_filepath, trans_filepath, pickle_fileloc, picklefilename = sys.argv[1:]

        print('Loading data...\n    PORTFOLIO: {}\n    PROFILE: {}\n    TRANSCRIPT: {}'
              .format(port_filepath, profile_filepath, trans_filepath))
        portfolio = pd.read_json(port_filepath, orient='records', lines=True)
        profile = pd.read_json(profile_filepath, orient='records', lines=True)
        transcript = pd.read_json(trans_filepath, orient='records', lines=True)

        print('Formatting data...')
        portfolio, profile, transcript = organize_raw_data(portfolio, profile, transcript)
        print('Splitting transcript by event type...')
        t_offer, t_viewed, t_trans, t_compl = split_trans(transcript)
        print('Merging offers with profile and portfolio tables... ')
        t_matched = merge_tables(t_offer, portfolio, profile)
        print('Matching events to respective offers...')
        t_matched = match_trans(t_matched, t_viewed, t_trans, t_compl)

        t_matched.rename(columns=\
            {'reward_x':'reward_rcvd', 'reward_y':'reward_offd', 'event_offer completed':'event_offer_completed', \
            'event_offer received':'event_offer_received', 'event_offer viewed':'event_offer_viewed'}, inplace=True)

        #Other
        t_matched.drop(columns=['amount','event'], inplace=True)
        t_matched.trans_spend.fillna(value=0, inplace=True)
        t_matched.reward_rcvd.fillna(value=0, inplace=True)

        print('Reorganizing Data...')

        print('Normalizaizing and Standardizing Data... ')
        t_matched_norm = norm_and_std(t_matched)

        print('Saving data...\n  : {}'.format(pickle_filepath))

        t_matched2.to_pickle(pickle_filepath)

        print('{} Saved!'.format(pickle_filepath))

    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')
        return


if __name__ == '__main__':
    main()
