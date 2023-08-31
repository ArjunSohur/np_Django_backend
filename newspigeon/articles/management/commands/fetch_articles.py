from django.core.management.base import BaseCommand
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

from ...models import nlp_models

nltk.download('punkt')


class Command(BaseCommand):
    feeds = [
        ["NYT World", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"],
        ["NYT Africa", "https://rss.nytimes.com/services/xml/rss/nyt/Africa.xml"],
        ["NYT Americas", "https://rss.nytimes.com/services/xml/rss/nyt/Americas.xml"],
        ["NYT APAC", "https://rss.nytimes.com/services/xml/rss/nyt/AsiaPacific.xml"],
        ["NYT EU", "https://rss.nytimes.com/services/xml/rss/nyt/Europe.xml"],
        ["NYT ME", "https://rss.nytimes.com/services/xml/rss/nyt/MiddleEast.xml"],
        ["NYT US", "https://rss.nytimes.com/services/xml/rss/nyt/US.xml"],
        ["NYT Education", "https://rss.nytimes.com/services/xml/rss/nyt/Education.xml"],
        ["NYT Business", "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml"],
        ["NYT Energy", "https://rss.nytimes.com/services/xml/rss/nyt/EnergyEnvironment.xml"],
        ["NYT Small Bussiness", "https://rss.nytimes.com/services/xml/rss/nyt/SmallBusiness.xml"],
        ["NYT Economy", "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml"],
        ["NYT Deals", "https://rss.nytimes.com/services/xml/rss/nyt/Dealbook.xml"],
        ["NYT Tech", "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"],
        ["NYT Personal Tech", "https://rss.nytimes.com/services/xml/rss/nyt/PersonalTech.xml"],
        ["NYT Sports", "https://rss.nytimes.com/services/xml/rss/nyt/Sports.xml"],
        ["NYT Baseball", "https://rss.nytimes.com/services/xml/rss/nyt/Baseball.xml"],
        ["NYT College Basketball", "https://rss.nytimes.com/services/xml/rss/nyt/CollegeBasketball.xml"],
        ["NYT College Football", "https://rss.nytimes.com/services/xml/rss/nyt/CollegeFootball.xml"],
        ["NYT Golf", "https://rss.nytimes.com/services/xml/rss/nyt/Golf.xml"],
        ["NYT Hockey", "https://rss.nytimes.com/services/xml/rss/nyt/Hockey.xml"],
        ["NYT Basketball", "https://rss.nytimes.com/services/xml/rss/nyt/ProBasketball.xml"],
        ["NYT Football", "https://rss.nytimes.com/services/xml/rss/nyt/ProFootball.xml"],
        ["NYT Soccer", "https://rss.nytimes.com/services/xml/rss/nyt/Soccer.xml"],
        ["NYT Tennis", "https://rss.nytimes.com/services/xml/rss/nyt/Tennis.xml"],
        ["NYT Science", "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml"],
        ["NYT Enviornment", "https://rss.nytimes.com/services/xml/rss/nyt/Climate.xml"],
        ["NYT Space", "https://rss.nytimes.com/services/xml/rss/nyt/Space.xml"],
        ["NYT Health", "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml"],
        ["NYT Well Blog", "https://rss.nytimes.com/services/xml/rss/nyt/Well.xml"],
        ["NYT Arts", "https://rss.nytimes.com/services/xml/rss/nyt/Arts.xml"],
        ["NYT Arts2", "https://rss.nytimes.com/services/xml/rss/nyt/ArtandDesign.xml"],
        ["NYT Books", "https://rss.nytimes.com/services/xml/rss/nyt/Books/Review.xml"],
        ["NYT Dance", "https://rss.nytimes.com/services/xml/rss/nyt/Dance.xml"],
        ["NYT Movies", "https://rss.nytimes.com/services/xml/rss/nyt/Movies.xml"],
        ["NYT Music", "https://rss.nytimes.com/services/xml/rss/nyt/Music.xml"],
        ["NYT TV", "https://rss.nytimes.com/services/xml/rss/nyt/Television.xml"],
        ["NYT Theater", "https://rss.nytimes.com/services/xml/rss/nyt/Theater.xml"],
        ["NYT Style", "https://rss.nytimes.com/services/xml/rss/nyt/FashionandStyle.xml"],
        ["NYT Dining", "https://rss.nytimes.com/services/xml/rss/nyt/DiningandWine.xml"],
        ["NYT Love", "https://rss.nytimes.com/services/xml/rss/nyt/Weddings.xml"],
        ["NYT Travel", "https://www.nytimes.com/services/xml/rss/nyt/Travel.xml"],
        ["CNN Top Stories", "http://rss.cnn.com/rss/cnn_topstories.rss"],
        ["CNN World", "http://rss.cnn.com/rss/cnn_world.rss"],
        ["CNN US", "http://rss.cnn.com/rss/cnn_us.rss"],
        ["CNN Business", "http://rss.cnn.com/rss/money_latest.rss"],
        ["CNN Politics", "http://rss.cnn.com/rss/cnn_allpolitics.rss"],
        ["CNN Tech", "http://rss.cnn.com/rss/cnn_tech.rss"],
        ["CNN Health", "http://rss.cnn.com/rss/cnn_health.rss"],
        ["CNN Entertainment", "http://rss.cnn.com/rss/cnn_showbiz.rss"],
        ["CNN Travel", "http://rss.cnn.com/rss/cnn_travel.rss"],
        ["WashPo Politics", "http://feeds.washingtonpost.com/rss/politics?itid=lk_inline_manual_2"],
        ["WashPo Sports", "http://feeds.washingtonpost.com/rss/sports?itid=lk_inline_manual_20"],
        ["WashPo Tech", "http://feeds.washingtonpost.com/rss/business/technology?itid=lk_inline_manual_31"],
        ["WashPo US", "http://feeds.washingtonpost.com/rss/national?itid=lk_inline_manual_32"],
        ["WashPo World", "http://feeds.washingtonpost.com/rss/world?itid=lk_inline_manual_36"],
        ["WashPo Business", "http://feeds.washingtonpost.com/rss/business?itid=lk_inline_manual_37"],
        ["WashPo Lifestyle", "http://feeds.washingtonpost.com/rss/lifestyle?itid=lk_inline_manual_38"],
        ["WashPo Entertainment", "http://feeds.washingtonpost.com/rss/entertainment?itid=lk_inline_manual_39"],
        ["Fox Headlines", "https://moxie.foxnews.com/google-publisher/latest.xml"],
        ["Fox World", "https://moxie.foxnews.com/google-publisher/world.xml"],
        ["Fox Politics", "https://moxie.foxnews.com/google-publisher/politics.xml"],
        ["Fox Science", "https://moxie.foxnews.com/google-publisher/science.xml"],
        ["Fox Health", "https://moxie.foxnews.com/google-publisher/health.xml"],
        ["Fox Sports", "https://moxie.foxnews.com/google-publisher/sports.xml"],
        ["Fox Travel", "https://moxie.foxnews.com/google-publisher/travel.xml"],
        ["Fox Tech", "https://moxie.foxnews.com/google-publisher/tech.xml"],
        ["WSJ World", "https://feeds.a.dj.com/rss/RSSWorldNews.xml"],
        ["WSJ Business", "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml"],
        ["WSJ Markets", "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"],
        ["WSJ Tech", "https://feeds.a.dj.com/rss/RSSWSJD.xml"],
        ["WSJ Lifestyle", "https://feeds.a.dj.com/rss/RSSLifestyle.xml"],
        ["Reuters via Google", "https://news.google.com/rss/search?q=when:24h+allinurl:reuters.com&ceid=US:en&hl=en-US&gl=US"],
    ]

    instance = nlp_models.objects.first()

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

                max_len = 256

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
                            vector =  encoding
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