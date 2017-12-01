from haystack import indexes
from models import Post
import datetime


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    pub_date = indexes.DateTimeField(model_attr='pub_date')

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())