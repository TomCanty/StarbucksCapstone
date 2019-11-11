

def results_bool(y,y_hat,beta = 1.0, print_results=True,ret_results=True):
    ''' This function compares the results of a predicted to an actual 1d array
    
    This function will provide Accuracy, Precision, Recall and F_beta score 
    of a 1d bo0lean prediction array vs actual.
    
    Can print results and/or return a list [Accuracy, Precision, Recall, Fscore, beta]
    
    Input:
    y: (int) actual results
    y_hat: (int) predicted results
    beta: (float) beta of F-score values between 0 to 2 (default 1)
    print_results (default True)
    return_results (default True)
    
    Return (optional): (list) [Accuracy, Precision, Recall, Fscore, beta]
    '''
    # check if input arrays are binary 
    if ((y==1) | (y==0)).all()==False:
        raise Exception("Error: y is not binary")
    if ((y_hat==1) | (y_hat==0)).all()==False:
        raise Exception("Error: y_hat is not binary")
    
    # check beta
    if beta > 2 or beta < 0:
        print('beta {} exceeded 0 to 2 limit, setting beta = 1'.format(beta))
        beta = 1.0
        
    
    accuracy = np.sum(y==y_hat)/len(y)
    tp = len(np.intersect1d(np.where(y_hat==1),np.where(y==1)))
    precision = tp/((y_hat==1).sum())
    recall = tp/(y.sum())
    f_score = (1+beta**2)*(precision * recall )/(beta**2 * (precision + recall))
    
    if print_results==True:
        print('Results:\n--------------------------------------')
        print('{0:<12s} {1:0.2%}'.format('Accuracy: ',accuracy))
        print('{0:<12s} {1:0.2%}'.format('Precision: ',precision))
        print('{0:<12s} {1:0.2%}'.format('Recall: ',recall))
        print('{0:<12s} {1:0.4f}'.format('F_'+str(beta)+': ',f_score))
    
    if ret_results == True:
        return [accuracy, precision, recall, f_score, beta]
    else:
        return

    