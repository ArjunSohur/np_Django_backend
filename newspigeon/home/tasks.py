from celery import shared_task
from home.models import NewsArticle
import feedparser  
from requests.exceptions import Timeout
from newspaper import Article
from datetime import datetime, timedelta
import nltk
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from transformers import T5ForConditionalGeneration,T5Tokenizer
from sentence_transformers import SentenceTransformer
import pickle

from .models import nlp_models

nltk.download('punkt')


@shared_task(bind=True)
def fetch_articles(self):
    print("hi")
    feeds = [
        ["Reuters via Google", "https://news.google.com/rss/search?q=when:24h+allinurl:reuters.com&ceid=US:en&hl=en-US&gl=US"],
    ]

    #instance = nlp_models.objects.first()
    instance = None

    if instance is not None:
        # An instance already exists in the database
        model = pickle.loads(instance.model)
        tokenizer = pickle.loads(instance.tokenizer)
        sentence_embedder = pickle.loads(instance.sentence_embedder)
    else:
        # An instance doesn't exist, create and save one
        model = T5ForConditionalGeneration.from_pretrained("Michau/t5-base-en-generate-headline")
        tokenizer = T5Tokenizer.from_pretrained("Michau/t5-base-en-generate-headline")
        sentence_embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        model_pickle = pickle.dumps(model)
        tokenizer_pickle = pickle.dumps(tokenizer)
        sentence_embedder_pickle = pickle.dumps(sentence_embedder)
        
        new_instance = nlp_models(model=model_pickle, tokenizer=tokenizer_pickle, sentence_embedder=sentence_embedder_pickle)

        new_instance.save()

    count = 0

    try:
        # Delete all news articles
        NewsArticle.objects.all().delete()
        response_data = {'message': 'All news articles have been deleted.'}
        print(response_data)
    except Exception as e:
        response_data = {'error': str(e)}
        print(response_data)

    for sub_feed in feeds:
        feed = feedparser.parse(sub_feed[1])
        one_day_ago = datetime.now() - timedelta(days=1)

        recent_items = []
        for entry in feed.entries:
            try:
                published = datetime(*entry.published_parsed[:6])
                if published > one_day_ago:
                    recent_items.append(entry)
            except:
                if not entry.title == "":
                    recent_items.append(entry)

        for item in recent_items:
            try:
                article = Article(item.links[0].href, timeout=1)
                print(item.links[0].href)
                article.download()
                article.parse()
                article.nlp()
                article_text = article.text

                vector = sentence_embedder.encode(article_text)

                text =  "headline: " + article_text

                encoding = tokenizer.encode_plus(text, return_tensors = "pt")
                input_ids = encoding["input_ids"]
                attention_masks = encoding["attention_mask"]

                beam_outputs = model.generate(
                    input_ids = input_ids,
                    attention_mask = attention_masks,
                    max_length = 64,
                    num_beams = 3,
                    early_stopping = True,
                )

                result = tokenizer.decode(beam_outputs[0])
                print(result)
                print(count)

                existing_article = NewsArticle.objects.filter(url=entry.link).first()

                if existing_article:
                     print(f'Article already exists: {existing_article.title}')
                else:
                    try:
                        NewsArticle.objects.update_or_create(
                            title = result,
                            text = article_text,
                            url = item.links[0].href,
                            date = article.publish_date,
                            authors = article.authors,
                            domain = article.meta.get("og:site_name"),
                            vector =  vector
                        )
                    except:
                        print("article not processed: ", item.links[0].href)

            except Timeout:
                print("ARTICLE COLLECTION TIMED OUT:", item.links[0].href)
            except Exception as e:
                print("ARTICLE COLLECTION ERROR:", e)

            print("=" * 30)
            count +=1

            print("---------------------------------------------")
    
    return "fetch articles completed with no runtime errors - does not mean successful database storage."


@shared_task(bind=True)
def test_task(self):
    print("task successful")
