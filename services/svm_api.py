
from sklearn.externals import joblib

class SVMClassifierAPI(object):
  
  def __init__(self, stored_classifier_path):
    self.clf = joblib.load(stored_classifier_path)
  
  def predict(self, X):
    return self.clf.predict(X)